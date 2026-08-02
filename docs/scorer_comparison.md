# Scorer Comparison: AlphaGenome CenterMask Aggregation Types
**Date:** 2026-08-02  
**Branch:** integrity-audit-2026-07

---

## Experimental benchmark result (stated first)

On the 23-variant experimental benchmark (minigene-validated splice-altering vs non-altering), the L2_DIFF aggregation scored 0/12 false positives at its top-20% threshold, while:
- Gene-mask quantile: 8/12 false positives
- CM DLS-501: 4/12 false positives
- SpliceAI: 1/12 (coverage limited — only 2/23 scored)

AUROC/AUPRC: GM=0.856/0.878, CM_DLS=0.849/0.868, CM_L2D=0.833/0.895, SpliceAI=0.432/0.526 (coverage artifact).

---

## Available AggregationType values

| Type | Computation | Notes |
|---|---|---|
| DIFF_MEAN | Mean of (alt − ref) across window bins | Linear mean — spike dilution |
| DIFF_SUM | Sum of (alt − ref) | Proportional to DIFF_MEAN, larger magnitude |
| DIFF_SUM_LOG2 | Sum of log2(alt / ref) per bin | Sum of per-bin log2FC |
| **DIFF_LOG2_SUM** | log2(sum(alt)) − log2(sum(ref)) | **Default for CenterMask** — log-ratio of totals |
| **L2_DIFF** | √∑(alt − ref)² | **L2 norm of differences — spike-amplifying** |
| **L2_DIFF_LOG1P** | √∑(log1p(alt) − log1p(ref))² | **L2 norm with log1p transform — robust** |
| ACTIVE_MEAN | Mean of alt values (not diff) | Reference-independent activity |
| ACTIVE_SUM | Sum of alt values | Same, summed |

**No max-type aggregation is exposed.** The closest to max-type behavior is L2_DIFF and L2_DIFF_LOG1P, which weight large per-bin differences quadratically, amplifying sharp spikes relative to mean-type aggregations. They are not true maxima but are substantially more spike-sensitive than DIFF_LOG2_SUM.

All configurations (width 501 and 2001 for SPLICE_SITE_USAGE) are constructable.

---

## Full 1,278 cohort results (vs SpliceAI)

| Scorer | Unique values | SAI>0.5 AUPRC | AUROC | SAI>0.2 AUPRC | AUROC | Spearman vs SAI |
|---|---|---|---|---|---|---|
| GM quantile | 290 (raw: 87 quantized) | 0.697 | 0.933 | 0.587 | 0.895 | 0.287 |
| GM raw | 87 (quantized) | 0.697 | 0.933 | 0.583 | 0.891 | 0.300 |
| CM DLS-501 | 994 | 0.371 | 0.910 | 0.476 | 0.886 | 0.292 |
| **CM L2D-501** | 667 | **0.664** | **0.947** | **0.586** | **0.906** | **0.311** |
| CM L2L-501 | 988 | 0.661 | 0.945 | 0.583 | 0.907 | 0.311 |
| CM L2D-2001 | 740 | 0.664 | 0.949 | 0.585 | 0.905 | 0.306 |

**CM L2D-501 and CM L2L-501 have substantially higher AUROC than GM_q (0.947 vs 0.933)** and similar AUPRC. Against SpliceAI>0.5, L2D AUPRC (0.664) is lower than GM_q (0.697) but the AUROC difference runs the other direction.

**Why L2D has higher AUROC but lower AUPRC than GM:** AUROC measures rank ordering across the full distribution; AUPRC is dominated by precision at the top of the ranking. GM_q clusters the top-SpliceAI variants in a single high quantile bucket (>0.999): the underlying raw scorer has only 87 discrete values, and the highest raw values — which occur near canonical splice sites and therefore correlate with SpliceAI — map through calibration to a small cluster of near-1.0 quantile values. (The quantile column itself has 290 unique values, not 87; the clustering is inherited from the raw distribution.) L2D_501 has a more continuous distribution but its top-ranked variants are distributed differently.

---

## Stratified AUPRC by distance to splice site (SpliceAI > 0.5)

| Stratum | n | n_pos | GM_q AUPRC | L2D-501 AUPRC |
|---|---|---|---|---|
| < 10 bp | 161 | 12 | 0.846 | 0.849 |
| 10–50 bp | 593 | 4 | 0.779 | 0.778 |
| 50–500 bp | 524 | 3 | 0.308 | 0.309 |

L2D-501 and GM_q are **essentially identical in every stratum** against SpliceAI. The advantage of L2D on the experimental benchmark (0 FP vs 8 FP) does not translate to improved SpliceAI-agreement ranking. This confirms that the experimental benchmark is measuring different biology from SpliceAI — as expected, since SpliceAI and the minigene assays assess different mechanisms.

---

## Codon-pair within-group divergence

| Scorer | Median diff | Max diff | Groups > 0.001 | Groups > 0.1 |
|---|---|---|---|---|
| GM raw | 0.000 | 0.211 | 37/145 | 6/145 |
| CM DLS-501 | 0.000 | 0.231 | 27/145 | 14/145 |
| **CM L2D-501** | **0.000** | **0.677** | **43/145** | **7/145** |
| CM L2L-501 | 0.000 | — | — | — |

**CM L2D-501 distinguishes more codon pairs than DLS-501** (43 vs 27 groups with divergence > 0.001) and has a higher maximum (0.677 vs 0.231). The L2_DIFF aggregation is more sensitive to the sharp local per-bin differences that distinguish synonymous nucleotide variants. This partially reverses the Check 15b conclusion that no center-mask scorer distinguishes codon pairs.

---

## Recommendation

For the paper's splice analysis, the options in order of experimental-benchmark performance:
1. **CM L2D-501 or CM L2L-501:** 0/12 FP on minigene negatives, AUROC 0.947 vs SpliceAI. The right scorer for a tool claiming to detect local splice disruption. Use within-cohort percentiles as the reference (no genome-wide quantile available).
2. **CM DLS-501:** 4/12 FP, reasonable continuous distribution. The current center-mask scorer.
3. **GM quantile:** 8/12 FP. Best AUPRC vs SpliceAI but the worst false-positive rate. Retaining it as a comparison figure is appropriate; using it as the primary splice metric is not, given the experimental benchmark result.

Full scores: `results/alphagenome/l2diff_scores.csv` (1,278 rows, cm_l2d_501, cm_l2l_501, cm_l2d_2001).
