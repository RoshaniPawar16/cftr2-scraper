# B1 Report: hg19 → hg38 Liftover of Five CF GWAS Modifier Loci

**Date:** 2026-08-02  
**Branch:** integrity-audit-2026-07  
**Input:** `data/gwas/GWAS_results/gwasImpute2_hg19_SAKNORM_all_meta_fixed_chrPeaks1mb.txt`  
**Source:** github.com/danghunccf/CF-GWAS-dataMiningPaper commit eba42429  
**Citations:**  
  Corvol et al. Nat Commun 6:8382 (2015). DOI: 10.1038/ncomms9382  
  Panjwani et al. NPJ Genom Med 3:8 (2018). DOI: 10.1038/s41525-018-0047-6

**Caveat on the Panjwani citation:** The danghunccf README attributes the
updated imputation to Panjwani et al. 2018, but that paper describes a
chromosome-7-only method (the CFTR locus). The imputation procedure and
quality thresholds for chrX and the other four loci (chr3, chr5, chr6, chr11)
are not documented in any available source. No imputation quality metric
(INFO/r²) is released with these summary statistics.

---

## Step 1: Source data (vendored)

Clone recorded in `data/gwas/SOURCE.md`. Files are read-only; SHA-256
checksums are in that file. The per-chromosome files are gzip-compressed
tab-separated summary statistics (14 columns: CHR SNP BP REF ALT MAF k
beta.fix z.fix p.fix beta.ran z.ran p.ran I2), build hg19.

The pre-extracted peaks file
(`gwasImpute2_hg19_SAKNORM_all_meta_fixed_chrPeaks1mb.txt`) contains
SNPs within 1 Mb of each GWAS peak across six loci.

---

## Step 2: Extraction and count verification

| Locus | CHR | hg19 window | Expected | Observed |
|---|---|---|---|---|
| 3q29 (MUC4/MUC20) | 3 | 194,479,032–196,478,667 | 7,936 | 7,936 ✓ |
| 5p15 (SLC9A3) | 5 | 11,882–1,524,524 | 5,932 | 5,932 ✓ |
| 6p21 (HLA-DRA) | 6 | 31,436,738–33,436,144 | 28,942 | 28,942 ✓ |
| 11p13 (EHF/APIP) | 11 | 33,786,140–35,784,039 | 7,296 | 7,296 ✓ |
| Xq23 (AGTR2/SLC6A14) | X | 114,391,795–116,390,913 | 4,747 | 4,747 ✓ |
| **Five loci total** | | | **54,853** | **54,853 ✓** |
| chr16 (extra, NOT one of the five) | 16 | 22,787,361–24,787,195 | 6,982 | 6,982 ✓ |

All six counts confirmed against specified values. The chr16 locus is kept
separate in all outputs; it is not one of the five published Corvol loci.

**rs116003090 is absent from this re-imputation.** The Corvol HLA lead SNP
(chr6:32,434,850 hg19) falls within the 6p21 window BP range but has no
summary statistics in these files. No figure should cite its re-imputation
statistics; Corvol Table 2 values apply to the original analysis only.

**rsID types (five loci):**

| Type | Count |
|---|---|
| clean_rs (single rsID, e.g. rs12345) | 52,252 |
| multi_rs (semicolon-merged, e.g. rs12;rs34) | 2,415 |
| no_rs (chr_pos_ref_alt format) | 186 |

---

## Step 3: Liftover — two independent routes

### Route A: UCSC hg19ToHg38 chain via pyliftover

| Result | Count |
|---|---|
| Lifted | 54,647 |
| Failed (chain gap) | 206 |

**206 chain-gap failures** fall in three structurally complex regions:

| Region | hg19 range | n | Note |
|---|---|---|---|
| MUC4/MUC20 (chr3) | 195,181,736–195,264,241 | 47 (incl. 8 indels) | MUC4 VNTR; known assembly gap |
| SLC9A3 telomeric end (chr5) | 18,146–44,430 | 13 SNVs | Near chr5 telomere; poorly assembled in hg19 |
| AGTR2/SLC6A14 (chrX) | 114,561,730–116,310,686 | 138 SNVs + 8 indels | X chromosome structural differences hg19→hg38 |

191 of these 206 are recovered by route B (Ensembl has hg38 positions for
the rsIDs even where the chain has no alignment). 15 fail both routes.

### Route B: rsID → hg38 lookup via Ensembl/dbSNP

Batch POST to `rest.ensembl.org/variation/homo_sapiens` (200 rsIDs per
request, 10 concurrent workers). Only clean single rsIDs queried.

| Result | Count |
|---|---|
| OK | 52,061 |
| Not in Ensembl | 191 |
| N/A — no clean rsID (multi_rs or no_rs) | 2,601 |

Of 191 not-in-Ensembl: 160 are indels (mostly VNTRs/complex), 31 are SNVs.

### Route comparison

Comparison is restricted to rows where both routes returned a result
(n=51,870 after excluding N/A and failures on either route).

| Outcome | Count |
|---|---|
| Agree (same chromosome and position) | 49,727 |
| Disagree | 2,139 |
| N/A (one or both routes failed/NA) | 2,987 |

**Disagree breakdown:**

| Pattern | Count | Interpretation |
|---|---|---|
| Indels, delta=1 | 2,097 | VCF anchor-base (pyliftover) vs dbSNP first-variant-base (Ensembl) convention difference — not true discordance |
| Indels, delta>1 | 6 | Complex indels with genuine positional difference; complex local structure |
| SNVs, delta=1 | 1 | Borderline (rs182976354, chrX) — possibly same convention issue |
| SNVs, delta=24–384 | 33 | Genuine discordance; clustered in MUC4 region (chr3:~195.5 Mb) and AGTR2 region (chrX:~114.6 Mb); suggest local assembly differences |
| SNVs, delta>1,000 | 2 | rsIDs remapped/merged in dbSNP; pyliftover uses source hg19 position, Ensembl uses current dbSNP hg38 assignment |

The 2,097 indel delta=1 disagreements are a systematic coordinate
convention difference, not errors. All 2,139 disagreements are recorded
in `B1_rejects.csv` with `reject_reason=routes_disagree`.

---

## Step 4: REF/ALT orientation vs hg38 reference

hg38 reference allele obtained from Ensembl `allele_string` field (first
allele before `/`). Checked for n=49,942 SNVs with Ensembl data.

| Orientation | Count | Downstream action |
|---|---|---|
| REF_ok | 41,863 | None — standard coding |
| REF_ok_palindromic | 7,308 | None — REF matches hg38, but A/T or C/G so strand indeterminate |
| ALT_as_hg38ref | 618 | **Beta sign must be reversed before directional use** |
| ALT_as_hg38ref_palindromic | 150 | Beta sign reversal needed; strand indeterminate |
| strand_flip | 2 | Complement alleles; beta sign unchanged |
| strand_flip_swap | 1 | Complement alleles AND reverse beta sign |

**618 SNVs have ALT coded as the hg38 reference allele.** Any analysis
using beta as a signed effect must reverse sign for these entries.
They are flagged `orientation=ALT_as_hg38ref` in the main output.

**Note on rs3103933 (MUC4/MUC20 lead SNP):** Source REF=A, ALT=G.
Ensembl hg38 allele_string=A/C/G/T (multi-allelic in dbSNP). hg38_ref=A
→ orientation=REF_ok. This does not resolve the discrepancy noted in
`data/gwas/SOURCE.md` between the source allele coding and the Corvol
published minor allele; that requires checking the Corvol paper directly.

---

## Step 5: SNV filter

| Variant type | Count (five loci) |
|---|---|
| SNVs (len(REF)==1 and len(ALT)==1) | 50,164 |
| Indels (excluded from downstream) | 4,689 |

Indel examples: CTTATAT>C (rs536986421 mentioned in task description),
ACT>A, CTT>C, CAAAAAAAAAA>C (VNTR indels). The 4,689 indels are retained
in the main output with `is_snv=NO`; downstream B2 scoring should filter
on `is_snv=YES`.

---

## Outputs

| File | Contents | Rows |
|---|---|---|
| `B1_lifted_hg38.csv.gz` | Five loci, all variants, with liftover columns | 54,853 |
| `B1_chr16_lifted_hg38.csv.gz` | Chr16 extra locus (not one of the five) | 6,982 |
| `B1_rejects.csv` | Route A/B failures and disagreements | 2,528 |
| `B1_ensembl_cache.json.gz` | Raw Ensembl batch responses (reproducibility) | — |
| `B1_corvol_liftover.csv` | Five Corvol lead SNPs lifted (from B1 step 5) | 5 |

**Columns added to main output (beyond the 14 source columns):**

| Column | Values |
|---|---|
| locus | 3q29 / 5p15 / 6p21 / 11p13 / Xq23 / chr16_extra |
| is_snv | YES / NO |
| rsid_type | clean_rs / multi_rs / no_rs |
| a_chr, a_pos, a_strand, a_ok | Route A result (pyliftover, 1-based hg38) |
| b_chr, b_pos, b_ok, b_note | Route B result (Ensembl, 1-based hg38) |
| routes_agree | YES / NO / NA |
| hg38_ref | Reference allele at hg38 position (from Ensembl) |
| orientation | REF_ok / ALT_as_hg38ref / strand_flip / … / unknown |

---

## Recommended filter for downstream (B2) scoring

```python
# Apply to B1_lifted_hg38.csv.gz
is_snv == 'YES'
AND a_ok == 'YES'
AND routes_agree IN ('YES', 'NA')   # NA = no clean rsID, not a conflict
```

This yields the set of SNVs with an unambiguous hg38 position from at
least route A, with no route-B contradiction. Flag `ALT_as_hg38ref`
entries before any directional (signed beta) analysis.

**Clean SNV exclusion arithmetic:**

| Exclusion category | SNVs removed | Note |
|---|---|---|
| Route A failure (`a_ok=FAIL`) | 198 | Chain gaps in MUC4, chr5 telomere, AGTR2 |
| Genuine route conflict (`routes_agree=NO`) | 36 | Requires `a_ok=YES`, so no overlap with above |
| **Total excluded** | **234** | |

Of the 206 total route-A failures, 198 are SNVs and 8 are indels.
The 36 genuine SNV conflicts and 198 SNV route-A failures are mutually
exclusive (a disagreement requires route A to succeed).

50,164 − 234 = **49,930 clean SNVs.**

| Filter step | Retained |
|---|---|
| All five loci | 54,853 |
| SNVs only (`is_snv=YES`) | 50,164 |
| + route A ok (`a_ok=YES`) | 49,966 |
| + no route conflict (`routes_agree` ∈ YES, NA) | **49,930** |
