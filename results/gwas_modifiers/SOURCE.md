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

Palindromic SNPs (A/T or C/G) cannot have strand resolved from alleles
alone. For these, the complement of REF is the same as ALT, so a mismatch
is indistinguishable from a strand flip without MAF comparison to a
reference panel. Palindromic categories are therefore **lower confidence**
than their non-palindromic counterparts. They are kept as distinct values
in the column — never merged with `REF_ok` or `ALT_as_hg38ref` — so that
B2 can apply separate handling.

| Value | Count | Meaning | Confidence |
|---|---|---|---|
| REF_ok | 41,863 | Source REF matches hg38 reference allele | High |
| REF_ok_palindromic | 7,308 | As above, but A/T or C/G — strand unresolvable from alleles | Lower |
| ALT_as_hg38ref | 618 | Source ALT matches hg38 ref — alleles swapped, beta reversal needed | High |
| ALT_as_hg38ref_palindromic | 150 | As above, A/T or C/G — strand unresolvable; reversal needed but less certain | Lower |
| strand_flip | 2 | Source REF is complement of hg38 ref | High |
| strand_flip_swap | 1 | Source ALT is complement of hg38 ref | High |
| non_snv | 2,119 | Indel; orientation check not applicable | — |
| unknown | 2,792 | No Ensembl data; orientation could not be determined | — |
| **Total** | **54,853** | | |

---

## Beta sign convention — CRITICAL for B2

**Beta values in this file are raw from the source (Panjwani re-imputation).
They have NOT been flipped. B2 must apply the correction before any
directional analysis.**

| orientation | Beta action | Note |
|---|---|---|
| `REF_ok` | No flip | Source REF is hg38 ref; standard coding |
| `ALT_as_hg38ref` | **Multiply beta.fix and beta.ran by −1** | Source ALT is hg38 ref; effect alleles are swapped |
| `strand_flip` | No flip | Complement coding; same biological allele is the effect allele |
| `strand_flip_swap` | **Multiply beta.fix and beta.ran by −1** | Complement AND swap |
| `REF_ok_palindromic` | No flip, but **flag** | Reference alleles agree; however strand ambiguity means direction is lower confidence without MAF check |
| `ALT_as_hg38ref_palindromic` | **Multiply by −1, but flag** | Alleles appear swapped; lower confidence — same strand ambiguity |
| `unknown` | **Do not use directionally** | No hg38 reference data |
| `non_snv` | **Do not use directionally** | Indel |

For palindromic sites (`REF_ok_palindromic`, `ALT_as_hg38ref_palindromic`):
the beta action listed is the best available inference from allele
comparison alone. Before using these betas directionally in any analysis,
MAF concordance with a reference panel should be checked to resolve strand.
They are retained in the output rather than excluded; exclusion is B2's
decision.
