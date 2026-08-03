# Source Record — results/gwas_modifiers/

Documents the B1 output files. For input data provenance see
`data/gwas/SOURCE.md`.

---

## B1 output files

| File | Contents | Committed |
|---|---|---|
| `B1_corvol_liftover.csv` | Five Corvol lead SNPs, hg19 → hg38 | Yes |
| `B1_lifted_hg38.csv.gz` | Five loci, all 54,853 variants, with liftover columns | Yes |
| `B1_chr16_lifted_hg38.csv.gz` | Chr16 extra locus (not one of the five), 6,982 variants | Yes |
| `B1_rejects.csv` | 2,528 route failures and disagreements | Yes |
| `B1_REPORT.md` | Full B1 summary with counts and findings | Yes |
| `B1_ensembl_cache.json.gz` | Ensembl batch API responses (intermediate) | **No — gitignored** |

The vendored GWAS clone (`data/gwas/`) is also gitignored; it is
regenerable with `git clone https://github.com/danghunccf/CF-GWAS-dataMiningPaper data/gwas/`
at commit `eba42429968b9c088b07c598c44bc7e9f837b0b4`.

---

## Column definitions — B1_lifted_hg38.csv.gz

Source columns (14, from Panjwani re-imputation, hg19):

| Column | Description |
|---|---|
| CHR | Chromosome (no chr prefix) |
| SNP | rsID or chr_pos_ref_alt for unnamed variants |
| BP | hg19 position, 1-based |
| REF | Source reference allele (hg19; orientation not verified in source) |
| ALT | Source alternative allele |
| MAF | Minor allele frequency |
| k | Number of cohorts in meta-analysis |
| beta.fix | Fixed-effects beta |
| z.fix | Fixed-effects Z-score |
| p.fix | Fixed-effects p-value |
| beta.ran | Random-effects beta |
| z.ran | Random-effects Z-score |
| p.ran | Random-effects p-value |
| I2 | Heterogeneity statistic |

Added columns (14):

| Column | Values | Description |
|---|---|---|
| locus | 3q29 / 5p15 / 6p21 / 11p13 / Xq23 | Window assignment |
| is_snv | YES / NO | len(REF)==1 and len(ALT)==1 |
| rsid_type | clean_rs / multi_rs / no_rs | rsID format classification |
| a_chr | chr3 / chr5 / … | Route A hg38 chromosome (pyliftover) |
| a_pos | integer | Route A hg38 position, 1-based |
| a_strand | + / - | Strand from pyliftover chain |
| a_ok | YES / FAIL | Route A liftover result |
| b_chr | chr3 / chr5 / … | Route B hg38 chromosome (Ensembl/dbSNP) |
| b_pos | integer | Route B hg38 position, 1-based |
| b_ok | YES / FAIL / NA | Route B lookup result |
| b_note | string | Reason for FAIL or NA |
| routes_agree | YES / NO / NA | A and B returned same position |
| hg38_ref | A / C / G / T | Reference allele at hg38 position (from Ensembl) |
| orientation | see below | REF/ALT relationship to hg38 reference |

**orientation values:**

| Value | Meaning |
|---|---|
| REF_ok | Source REF matches hg38 reference allele — standard coding |
| REF_ok_palindromic | As above, but A/T or C/G SNP (strand indeterminate) |
| ALT_as_hg38ref | Source ALT matches hg38 ref — alleles are swapped relative to hg38 |
| ALT_as_hg38ref_palindromic | As above, A/T or C/G SNP |
| strand_flip | Source REF is complement of hg38 ref |
| strand_flip_swap | Source ALT is complement of hg38 ref |
| non_snv | Indel; orientation check not applicable |
| unknown | No Ensembl data available |

---

## Beta sign convention — CRITICAL for B2

**Beta values in this file are raw from the source (Panjwani re-imputation).
They have NOT been flipped. B2 must apply the correction before any
directional analysis.**

The rule:

- `orientation == 'REF_ok'` or `'REF_ok_palindromic'`: source REF is the
  hg38 reference allele → beta is the effect of the ALT allele relative to
  REF. **No flip needed.**

- `orientation == 'ALT_as_hg38ref'` or `'ALT_as_hg38ref_palindromic'`:
  source ALT is the hg38 reference allele → the effect allele in the source
  is what hg38 calls the reference. **Multiply beta.fix and beta.ran by −1
  before using directionally.**

- `orientation == 'strand_flip'`: complement coding; effect allele is the
  same biological allele. **No flip needed.**

- `orientation == 'strand_flip_swap'`: complement AND swap. **Multiply
  beta by −1.**

- `orientation == 'unknown'` or `'non_snv'` or palindromic variants:
  direction is indeterminate. **Do not use beta directionally.**

768 rows in B1_lifted_hg38.csv.gz have `ALT_as_hg38ref` or
`ALT_as_hg38ref_palindromic` (618 + 150). These are all five-loci
variants; none are in B1_chr16_lifted_hg38.csv.gz (chr16 counts not
separately verified).
