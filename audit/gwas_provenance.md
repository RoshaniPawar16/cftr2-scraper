# Source Record — CF GWAS Re-imputation Data

**Do not edit any file under data/gwas/. Files are vendored read-only.**

---

## Repository

| Field | Value |
|---|---|
| Source URL | https://github.com/danghunccf/CF-GWAS-dataMiningPaper |
| Clone date | 2026-08-02 |
| Commit hash | eba42429968b9c088b07c598c44bc7e9f837b0b4 |
| Last commit message | "Update README.md" |

---

## What this data is

Per-chromosome GWAS summary statistics described in the danghunccf README as
a re-imputation of the CF modifier GWAS cohort. Build: **hg19**.

The README attributes the updated imputation to:

- **Panjwani N et al.** "Improving imputation in disease-relevant regions:
  lessons from cystic fibrosis." *NPJ Genom Med* 3:8 (2018).
  DOI: 10.1038/s41525-018-0047-6, PMC: PMC5861096

**Caveat on this citation:** The Panjwani 2018 paper describes a chromosome-7-only
method (the CFTR locus). It does not address imputation of chrX or any of the
other four modifier loci. The imputation procedure and quality thresholds for
chrX, chr3, chr5, chr6, and chr11 are not documented in any available source.
No imputation quality metric (INFO/r²) is released with these summary statistics.

The original association statistics are from:

- **Corvol et al.** "Genome-wide association meta-analysis identifies five modifier
  loci of lung disease severity in cystic fibrosis." *Nat Commun* 6:8382 (2015).
  DOI: 10.1038/ncomms9382, PMID: 26417704, PMC4589222

**Both citations are required when using these statistics.**
The statistics here are NOT the published Corvol values — they are from the
re-imputation. Use the Panjwani 2018 citation as the primary source for these files.

---

## File format

Tab-separated, gzip-compressed. 14 columns, no missing-value sentinel documented.

```
CHR  SNP  BP  REF  ALT  MAF  k  beta.fix  z.fix  p.fix  beta.ran  z.ran  p.ran  I2
```

| Column | Description |
|---|---|
| CHR | Chromosome (integer or X; no "chr" prefix) |
| SNP | rsID or chr_pos_ref_alt for unnamed variants |
| BP | Position, hg19, 1-based |
| REF | Reference allele (hg19 forward strand, orientation unverified) |
| ALT | Alternative allele |
| MAF | Minor allele frequency |
| k | Number of cohorts in meta-analysis |
| beta.fix | Fixed-effects beta |
| z.fix | Fixed-effects Z-score |
| p.fix | Fixed-effects p-value |
| beta.ran | Random-effects beta |
| z.ran | Random-effects Z-score |
| p.ran | Random-effects p-value |
| I2 | Heterogeneity statistic |

**Note on allele orientation:** The README does not document whether REF/ALT
are encoded relative to the hg19 forward strand or the major/minor allele.
rs3103933 (MUC4/MUC20 lead SNP) shows REF/ALT and beta sign inconsistent with
the Corvol minor allele. Resolve REF/ALT orientation against the hg38 reference
before using betas directionally.

---

## Pre-extracted peaks file

`GWAS_results/gwasImpute2_hg19_SAKNORM_all_meta_fixed_chrPeaks1mb.txt`

Contains SNPs within 1 Mb of each GWAS peak, pre-extracted from the per-chromosome
files. Six loci present:

| Locus | CHR | BP range (hg19) | SNP count |
|---|---|---|---|
| 3q29 | 3 | 194,479,032 – 196,478,667 | 7,936 |
| 5p15 | 5 | 11,882 – 1,524,524 | 5,932 |
| 6p21 | 6 | 31,436,738 – 33,436,144 | 28,942 |
| 11p13 | 11 | 33,786,140 – 35,784,039 | 7,296 |
| Xq23 | X | 114,391,795 – 116,390,913 | 4,747 |
| chr16 (extra) | 16 | 22,787,361 – 24,787,195 | 6,982 |
| **Total** | | | **61,835** |

The chr16 locus is in the peaks file but is NOT one of the published five Corvol
loci. It is kept separate in all downstream analyses.

The Corvol HLA lead SNP rs116003090 is absent from this re-imputation.
No summary statistics exist for it in these files.

---

## SHA-256 checksums (as cloned)

```
dd4491c62984f21d37c5766d389944b1e04a088d5f8b4a38ec5962f12a8d18eb  gwasImpute2_hg19_SAKNORM_all_meta_fixed_chrPeaks1mb.txt
feb00bf76a15ec1ce0ed1085f434b77410cdffd78a4de9e721728ad696a78ac3  chr3_gwasImpute2_hg19_SAKNORM_all_meta.txt.gz
215a4f45786839a8edbb16f5556399e6e9e66aadbdc9372989c7029418347d1f  chr5_gwasImpute2_hg19_SAKNORM_all_meta.txt.gz
f86e9f0b84df43362228387f1a755916937bc9bcc9e217a76a303a5cd07a41cc  chr6_gwasImpute2_hg19_SAKNORM_all_meta.txt.gz
ce8a83c01c71db91a77dc120ee97372f12f3be298e445d7b14695d1ac9c5586f  chr11_gwasImpute2_hg19_SAKNORM_all_meta.txt.gz
69b4a24c15df6bb3cd6a9f6815865a201d5774c014dc9f25cee1a864a7cf3994  chrX_gwasImpute2_hg19_SAKNORM_all_meta.txt.gz
dda7211e5bc821f92752d94b60efd4c6c53f6b704730670145d58b75a82d15ba  chr16_gwasImpute2_hg19_SAKNORM_all_meta.txt.gz
```
