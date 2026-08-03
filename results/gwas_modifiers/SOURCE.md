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

**Palindromic SNPs (A/T or C/G) are strand-unresolvable from alleles
alone.** The classifier assigns `REF_ok_palindromic` when source REF
matches the hg38 reference base, and `ALT_as_hg38ref_palindromic` when
source ALT matches. This confirms which allele label agrees with hg38 but
does NOT resolve effect direction: a source coded on the opposite strand
would produce the same allele labels for a palindromic SNP, with betas
pointing to the opposite biological allele. The 7,308 `REF_ok_palindromic`
sites are **unresolved**, not confirmed. Resolution requires MAF comparison
against a reference panel (e.g. gnomAD). These categories are kept
distinct in the column and must not be merged with `REF_ok` or
`ALT_as_hg38ref`.

| Value | Count | Meaning | Beta usable directionally? |
|---|---|---|---|
| REF_ok | 41,863 | Source REF matches hg38 ref | Yes |
| ALT_as_hg38ref | 618 | Source ALT matches hg38 ref; alleles swapped | Yes, after ×−1 |
| strand_flip | 2 | Source REF is complement of hg38 ref | Yes |
| strand_flip_swap | 1 | Source ALT is complement of hg38 ref | Yes, after ×−1 |
| REF_ok_palindromic | 7,308 | Source REF matches hg38 ref, A/T or C/G site | **No — unresolved; MAF check needed** |
| ALT_as_hg38ref_palindromic | 150 | Source ALT matches hg38 ref, A/T or C/G site | **No — unresolved; MAF check needed** |
| non_snv | 2,119 | Indel | Not applicable |
| unknown | 2,792 | No Ensembl data | **No — orientation unknown** |
| **Total** | **54,853** | | |

---

## Beta sign convention — CRITICAL for B2

**Beta values in this file are raw from the source (Panjwani re-imputation).
They have NOT been flipped. B2 must apply the correction before any
directional analysis.**

| orientation | Beta action |
|---|---|
| `REF_ok` | Use as-is |
| `ALT_as_hg38ref` | Multiply beta.fix and beta.ran by −1 |
| `strand_flip` | Use as-is |
| `strand_flip_swap` | Multiply beta.fix and beta.ran by −1 |
| `REF_ok_palindromic` | **Do not use directionally — strand unresolved** |
| `ALT_as_hg38ref_palindromic` | **Do not use directionally — strand unresolved** |
| `unknown` | **Do not use directionally — no hg38 reference data** |
| `non_snv` | Not applicable |

Palindromic and unknown sites (7,458 + 215 in clean SNV set respectively;
see B1_REPORT.md) must not be used in any analysis that depends on effect
direction until MAF comparison against gnomAD resolves strand.
