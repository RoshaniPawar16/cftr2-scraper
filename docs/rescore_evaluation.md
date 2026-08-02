# Rescore Evaluation: Gene-Mask vs Center-Mask Scorer
**Date:** 2026-08-02  
**Branch:** integrity-audit-2026-07  
**Positive class:** SpliceAI > 0.5 (n=19) and SpliceAI > 0.2 (n=52)  
**Cohort:** 1,278 AM-ambiguous CFTR variants

---

## 16a — Matched-base-rate enrichment

The gene-mask quantile was compared at its original threshold (0.95, clearing 58.4% of the cohort). The center-mask was compared at the top 5% of the cohort. These are different bars. The corrected comparison uses the top 5% for all scorers.

**SpliceAI > 0.5 (n=19) at top-5% threshold:**

| Scorer | Base rate | Above | Expected | Enrichment | Fisher p | OR (95% CI) |
|---|---|---|---|---|---|---|
| GM quantile (original bar, top 58%) | 58.5% | 18/19 | 11.1 | 1.62× | 0.0007 | 13.1 (1.7–98.3) |
| **GM quantile (top 5%)** | **5.2%** | **16/19** | **1.0** | **16.3×** | **<0.0001** | **129 (36–457)** |
| GM raw (top 5%) | 5.2% | 16/19 | 1.0 | 16.1× | <0.0001 | 126 (36–447) |
| **CM splice 501 (top 5%)** | **5.0%** | **13/19** | **1.0** | **13.7×** | **<0.0001** | **51 (19–141)** |
| CM ATAC 501 (top 5%) | 5.0% | 0/19 | 1.0 | 0.00× | 0.62 | — |

**SpliceAI > 0.2 (n=52) at top-5% threshold:**

| Scorer | Base rate | Above | Expected | Enrichment | Fisher p | OR (95% CI) |
|---|---|---|---|---|---|---|
| GM quantile (original bar, top 58%) | 58.5% | 49/52 | 30.4 | 1.61× | <0.0001 | 12.4 (3.8–39.9) |
| **GM quantile (top 5%)** | **5.2%** | **34/52** | **2.7** | **12.7×** | **<0.0001** | **70.5 (36–138)** |
| GM raw (top 5%) | 5.2% | 34/52 | 2.7 | 12.5× | <0.0001 | 68.3 (35–133) |
| **CM splice 501 (top 5%)** | **5.0%** | **28/52** | **2.6** | **10.8×** | **<0.0001** | **38.6 (20–73)** |
| CM ATAC 501 (top 5%) | 5.0% | 1/52 | 2.6 | 0.38× | 0.51 | 0.36 (0.05–2.7) |

**At matched base rates, the gene-mask scorer outperforms the center-mask scorer.** GM recovers 16/19 high-SpliceAI variants in its top 5% (enrichment 16.3×, OR=129); CM recovers 13/19 (enrichment 13.7×, OR=51). Both are highly significant and far above the ATAC control (0/19). The center-mask rescore produces a weaker discriminator, not a better one.

**The ATAC control is conclusive.** Zero of 19 SpliceAI>0.5 variants appear in the top 5% by CM ATAC. This confirms the splice discrimination is modality-specific regardless of scorer.

---

## 16b — AUPRC and AUROC (no threshold)

**SpliceAI > 0.5 as positive class** (n=19, baseline=0.0149):

| Scorer | AUROC | AUPRC | AUPRC lift |
|---|---|---|---|
| **GM quantile** | **0.933** | **0.697** | **46.9×** |
| GM raw | 0.933 | 0.697 | 46.9× |
| CM splice 501 | 0.910 | 0.371 | 24.9× |
| CM ATAC 501 | 0.686 | 0.026 | 1.8× |

**SpliceAI > 0.2 as positive class** (n=52, baseline=0.0407):

| Scorer | AUROC | AUPRC | AUPRC lift |
|---|---|---|---|
| **GM quantile** | **0.895** | **0.587** | **14.4×** |
| GM raw | 0.891 | 0.583 | 14.3× |
| CM splice 501 | 0.886 | 0.476 | 11.7× |
| CM ATAC 501 | 0.545 | 0.045 | 1.1× |

**The gene-mask scorer substantially outperforms the center-mask scorer by AUPRC.** At SpliceAI>0.5, GM AUPRC=0.697 vs CM AUPRC=0.371 — the GM is 1.88× better. At SpliceAI>0.2, GM=0.587 vs CM=0.476 (1.23× better).

**Top-k enrichment (SpliceAI > 0.5):**

| k | Expected | GM top-k | GM precision | CM top-k | CM precision | ATAC top-k |
|---|---|---|---|---|---|---|
| 10 | 0.15 | 9 | 0.900 | 6 | 0.600 | 0 |
| 25 | 0.37 | 13 | 0.520 | 9 | 0.360 | 0 |
| 50 | 0.74 | 16 | 0.320 | 13 | 0.260 | 0 |
| 100 | 1.49 | 17 | 0.170 | 13 | 0.130 | 1 |

At k=10, the GM achieves 0.900 precision (9 of 10 top-ranked variants have SpliceAI>0.5). The CM achieves 0.600.

**Spearman (secondary, dominated by tied nulls):** GM rho=0.287, CM rho=0.292 — indistinguishable. Spearman masks the discrimination difference by treating the bulk of near-zero, tied values equivalently.

---

## 16c — Twelve CF-causing positive controls

**Pre-registration:** Mann-Whitney U, two-sided. Three outcomes (CM_splice_501, CM_ATAC_501, CM_RNA_501). Bonferroni α = 0.0167. Effect size: rank-biserial r. Registered before computing.

**Results (n=12 vs n=1266):**

| Outcome | Median 12 | Median 1266 | U | p | rank-biserial r |
|---|---|---|---|---|---|
| CM_splice_501 | 0.01142 | 0.00922 | 8531 | 0.463 | −0.123 |
| CM_ATAC_501 | 0.01323 | 0.01683 | 6127 | 0.249 | +0.193 |
| CM_RNA_501 | 0.02306 | 0.02949 | 6940 | 0.607 | +0.086 |

**All three tests: non-significant at Bonferroni-corrected α=0.0167.** No significant elevation in any modality. At n=12, power to detect a medium-large effect (d=0.8) is approximately 20%; a null result is uninformative, not exonerating.

**Individual results (each of the 12):**

| Variant | AM | CM_splice | sp_pctile | CM_ATAC | ATAC_pctile | CM_RNA | RNA_pctile | SpliceAI | CADD |
|---|---|---|---|---|---|---|---|---|---|
| H954P | 0.367 | 0.01933 | 74.6th | 0.15503 | 97.7th | 0.01285 | 11.7th | 0.0 | 19.6 |
| Y913C | 0.379 | 0.00968 | 53.9th | 0.02310 | 63.1th | 0.02440 | 39.2th | 0.0 | 16.5 |
| A613T | 0.393 | 0.06216 | 92.6th | 0.02171 | 60.0th | 0.06437 | 80.5th | 0.09 | 29.6 |
| Q30P | 0.412 | 0.00242 | 14.0th | 0.00130 | 3.9th | 0.02171 | 32.6th | 0.0 | 23.2 |
| P1021L | 0.427 | 0.00464 | 26.0th | 0.00644 | 19.6th | 0.02448 | 39.5th | 0.0 | 26.5 |
| I601F | 0.490 | 0.20043 | **98.3th** | 0.00043 | 1.7th | 0.22622 | **95.8th** | 0.23 | 24.9 |
| I148N | 0.495 | 0.01255 | 62.1th | 0.01796 | 52.5th | 0.00950 | 6.6th | 0.0 | 24.2 |
| N1088D | 0.499 | 0.00222 | 7.2th | 0.00305 | 9.3th | 0.01780 | 23.5th | 0.0 | 22.6 |
| I506L | 0.507 | 0.00247 | 15.1th | 0.00851 | 26.4th | 0.02060 | 30.3th | 0.01 | 25.7 |
| Q359R | 0.510 | 0.01028 | 55.6th | 0.02061 | 57.7th | 0.01805 | 23.9th | 0.0 | 25.6 |
| H139L | 0.541 | 0.03430 | 84.9th | 0.03587 | 80.5th | 0.05430 | 75.7th | 0.04 | 25.4 |
| V1240G | 0.564 | 0.04238 | 88.3th | 0.00378 | 12.0th | 0.10734 | 88.9th | 0.14 | 29.1 |

Medians — 12: splice=0.0114 ATAC=0.0132 RNA=0.0231  
Medians — 1266: splice=0.0092 ATAC=0.0168 RNA=0.0295

**AUPRC (12 as positives):** 0.0167, baseline=0.0094, lift=1.78×. Only 1 of 12 appears in the top 5% of the cohort by CM splice.

**n=12. A null is not evidence of absence at this size.** The analysis is underpowered for any modality. H954P (ATAC 97.7th) and I601F (splice 98.3th, RNA 95.8th) are interesting individual cases that warrant review, but cannot be generalised from n=1 within a group of 12.

---

## 16d — Pangolin: cannot run

Pangolin 1.0.2 installed from GitHub (`tkzeng/Pangolin`) but fails to import due to `pkg_resources` removal in Python 3.13:

```
ImportError: from pkg_resources import resource_filename
```

Additional blockers (unchanged from triage):
- Reference genome FASTA (GRCh38): MISSING (~3.1 GB download from UCSC or Ensembl)
- Gene annotation file (GTF): MISSING (~50 MB download from Ensembl)

Network is available. Pangolin installation requires a Python ≤ 3.12 environment or patching the `pkg_resources` import. With those resolved, it would require the FASTA and GTF before any variant can be scored.

**SpliceAI–Pangolin agreement baseline** cannot be reported without running Pangolin. The question of whether base-level sensitivity is a property of all splice-specific tools or particular to SpliceAI remains open. Pangolin's reference paper (Zeng & Pritchard 2022) reports high concordance with SpliceAI on canonical splice variants and better performance on deep intronic variants; its behaviour on coding variants is not well characterised.

---

## 16e — Priority 7: old vs new scores

Old SPLICE_q values from gene-mask scorer (genome-wide quantile).  
New CM_splice_501 values and within-1278-cohort percentiles.

| Variant | Old SPLICE_q | Old ATAC_q | Old RNA_q | New CM_splice | sp_pctile | New CM_ATAC | ATAC_pctile | New CM_RNA | RNA_pctile |
|---|---|---|---|---|---|---|---|---|---|
| L49P | 0.821 | 0.081 | 0.999 | 0.00210 | 5.5th | 0.00208 | 6.7th | 0.01030 | 7.4th |
| R104G | 0.993 | 0.699 | 0.974 | 0.02587 | 79.3th | 0.01992 | 56.5th | 0.06081 | 79.0th |
| P355L | 0.635 | 0.537 | 0.965 | 0.00033 | 3.4th | 0.01071 | 32.3th | 0.02570 | 41.8th |
| F650L | 0.640 | 0.693 | 0.957 | 0.00325 | 19.3th | 0.01963 | 56.2th | 0.00669 | 2.6th |
| L986P | 0.931 | 0.675 | 0.959 | 0.00921 | 49.6th | 0.01841 | 53.8th | 0.00610 | 1.7th |
| H1054Q | 0.948 | 0.950 | 0.991 | 0.00440 | 22.9th | 0.07507 | 93.5th | 0.02087 | 30.8th |
| R1097C | 0.720 | 0.905 | 0.968 | 0.00464 | 26.0th | 0.04847 | 87.8th | 0.01795 | 23.9th |

**The correction is dramatic.** Old gene-mask SPLICE_q ranged 0.635–0.993 (all described as "top few percent of all human variants"). New CM splice percentiles within the 1,278 range from 3.4th (P355L) to 79.3th (R104G) — most are in the bottom half of the cohort by this metric.

The old characterisation ("RNA quantile 0.999 for L49P") came from the gene-mask RNA scorer, which is continuous and better-calibrated. The new CM_RNA percentiles for L49P (7.4th) are much lower.

**The ATAC signal for H1054Q (old 0.950, new 93.5th percentile within cohort) and R1097C (old 0.905, new 87.8th) is substantially preserved.** These two variants remain at the high end of the ATAC distribution within the cohort. The original narrative that ATAC distinguishes H1054Q and R1097C from the group is qualitatively supported, though the absolute values and reference base rates are different.

---

## 19c — Corrections applied to this document

**50–500 bp AUPRC qualified:** The AUPRC figures of GM 0.307 and CM 0.081 in the 50–500 bp stratum (from 18a analysis) are computed against 3 SpliceAI>0.5 positives out of 524 variants (baseline 0.6%). These figures are retained as-is but must be read with this caveat: 41% of the cohort lies beyond SpliceAI's ±50 nt effective detection window (the range in which splice site strength changes are typically detected). In this stratum, SpliceAI itself is not validating anything — its positives likely reflect annotated splice sites at exactly 50–500 bp, not SpliceAI's direct splice-site scoring. The substantive finding is: 41% of the cohort cannot be evaluated using SpliceAI as a reference standard.

**Post-hoc selection noted:** The primary concordant-set definition (CM top 5% AND SpliceAI > 0.2, n=27) was selected after computing enrichment for all three candidates. The rationale for choosing it: SpliceAI > 0.2 is the tool authors' own "high-recall" threshold (Jaganathan et al. 2019), providing an external citation. All three definitions were computed before one was selected as primary. The other two (GM_q > 0.95 AND SpliceAI ≥ 0.5; CM top 5% AND SpliceAI > 0.5) are reported as secondary and sensitivity analyses.

---

## 16f — CM splice distribution: no threshold

The center-mask scorer is continuous. No genome-wide quantile normalisation exists. Thresholds must be justified against the within-cohort distribution or an external benchmark, not as "top X% of all human variants."

**CM_splice_501 distribution (n=1,278):**

| | CM_splice_501 | CM_splice_2001 | CM_ATAC_501 | CM_RNA_501 |
|---|---|---|---|---|
| Unique values | 994 | 998 | 997 | 997 |
| Min | 0.000016 | 0.000016 | 0.000035 | 0.00195 |
| Median | 0.00924 | 0.00792 | 0.01683 | 0.02949 |
| P90 | 0.04970 | 0.04164 | 0.05676 | 0.12567 |
| P95 | 0.08275 | 0.06444 | 0.09093 | 0.19208 |
| P99 | 0.28477 | 0.25283 | 0.21268 | 0.60656 |
| Max | 1.22526 | 1.22227 | 0.54214 | 2.45586 |

The distribution is right-skewed; the top 5% (above 0.083) captures the variants with the strongest local splice signal within this cohort. This is the appropriate reference for categorical grouping — not a genome-wide comparison.

**Note on the 693:** The discordant group cannot be reconstituted with the center-mask scorer without an external threshold justification. The 18 multi-tool concordant variants identified by AUPRC top-ranking are the appropriate replacement: variants where both AlphaGenome (by rank within cohort) and SpliceAI agree on a strong splice signal. These 18 variants retain OR=51–129 versus the cohort depending on threshold, compared to OR=13.1 at the original 0.95/0.2 thresholds.
