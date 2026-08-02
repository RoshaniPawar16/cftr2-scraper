# Check 19 Report
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**No git operations. Part B locked.**

---

## What I could not establish

1. **CADD scores for 19 of 23 experimental variants.** CADD REST API returned no data for these variants (query format issue). CADD is available for only the 4 variants in the existing cohort.
2. **SpliceAI for 21 of 23 experimental variants.** The Ensembl VEP REST API returned 0 for all 19 new variants. The SpliceAI precomputed scores used in this analysis come from the Ensembl VEP plugin, which may not cover all exon-interior variants outside the VCF. SpliceAI analysis on the experimental benchmark is **limited to 2/23 scored variants** (Gly970Val=0.95 and Ile918Met=0.22); the apparent AUROC=0.432 is a coverage artifact, not a prediction failure.
3. **Additional CFTR experimental splice data.** No further extractable case series were found beyond Zhang 2025 and Bergougnoux 2023.

---

## 19a — Experimental benchmark

### False-positive counts (reported first)

| Tool | Threshold | FP / 12 confirmed-negatives | Sensitivity |
|---|---|---|---|
| **GM splice quantile** | > 0.95 | **8/12 (67%)** | 10/11 (91%) |
| CM DLS-501 | top-20% cohort | 4/12 (33%) | 7/11 (64%) |
| **CM L2D-501** | top-20% cohort | **0/12 (0%)** | **4/11 (36%)** |
| CM L2L-501 | top-20% cohort | 0/12 (0%) | 4/11 (36%) |
| SpliceAI ≥ 0.2 | authors' threshold | 1/12* | 1/11* |

*SpliceAI scores available for only 2/23 variants.

**The gene-mask quantile has the highest sensitivity (91%) but the worst false-positive rate (67%) on this benchmark.** It cannot distinguish confirmed splice-altering from confirmed non-splice-altering variants in 8 of 12 cases. This is the correct summary of its performance and it must be reported before the sensitivity figure, not after.

### Benchmark population

23 variants (22 unique protein changes): 11 confirmed splice-altering, 12 confirmed non-altering. GRCh38 coordinates derived from NM_000492.4 HGVS via Ensembl VEP REST. Source papers: Zhang B et al. 2025 (8 variants), Bergougnoux A et al. 2023 (15 variants). Glu403Asp appears in both (c.1209G>T and G>C — different nucleotides, both positive).

### AUROC / AUPRC (point estimates; n=23 too small for CIs)

| Tool | AUROC | AUPRC |
|---|---|---|
| GM quantile | 0.856 | 0.878 |
| CM DLS-501 | 0.849 | 0.868 |
| CM L2D-501 | 0.833 | 0.895 |
| CM L2L-501 | 0.833 | 0.895 |
| SpliceAI | 0.432 (coverage artifact) | 0.526 |
| AlphaMissense | 0.576 | 0.660 |

### Arg1070Gln (clearest discriminating case)

Confirmed non-splice-altering by minigene, 69 bp from splice site.  
GM_q = 0.963 (false positive at 0.95 threshold).  
CM_DLS_501 = 0.007, CM_L2D_501 = 0.000, SpliceAI = 0.01 — all correctly low.  
The GM false positive arises because the gene-mask scorer detects the canonical splice site 69 bp away, not the variant's specific effect.

Full table and Arg1070Gln detail: `docs/experimental_benchmark.md`.  
Data file: `results/experimental_benchmark.csv`.

---

## 19b — L2_DIFF scorer configuration

### AggregationType inventory

8 types available. No max-type is exposed. Closest to max behavior: L2_DIFF and L2_DIFF_LOG1P.

| Type | Computation |
|---|---|
| DIFF_MEAN | Mean(alt−ref) across window |
| DIFF_SUM | Sum(alt−ref) |
| DIFF_SUM_LOG2 | Sum(log2(alt/ref)) per bin |
| DIFF_LOG2_SUM | log2(sum(alt)) − log2(sum(ref)) — current default |
| **L2_DIFF** | √∑(alt−ref)² — spike-amplifying |
| **L2_DIFF_LOG1P** | √∑(log1p(alt)−log1p(ref))² — robust variant |
| ACTIVE_MEAN | Mean(alt) |
| ACTIVE_SUM | Sum(alt) |

### Full 1,278 cohort results

| Scorer | Unique values | SAI>0.5 AUPRC | AUROC | SAI>0.2 AUPRC | AUROC | Spearman vs SAI |
|---|---|---|---|---|---|---|
| GM quantile | 290 (raw: 87 quantized) | 0.697 | 0.933 | 0.587 | 0.895 | 0.287 |
| GM raw | 87 (quantized) | 0.697 | 0.933 | 0.583 | 0.891 | 0.300 |
| CM DLS-501 | 994 | 0.371 | 0.910 | 0.476 | 0.886 | 0.292 |
| **CM L2D-501** | **667** | **0.664** | **0.947** | **0.586** | **0.906** | **0.311** |
| CM L2L-501 | 988 | 0.661 | 0.945 | 0.583 | 0.907 | 0.311 |
| CM L2D-2001 | 740 | 0.664 | 0.949 | 0.585 | 0.905 | 0.306 |

**CM L2D-501 AUROC = 0.947** — the highest AUROC of any scorer against SpliceAI>0.5. **AUPRC = 0.664** — lower than GM_q (0.697) but the AUROC improvement is 0.014.

The SpliceAI-agreement ranking places GM_q first by AUPRC, but the experimental benchmark (0 FP vs 8 FP) places L2D_501 first by false-positive rate. The two metrics disagree. SpliceAI-agreement and minigene-validated performance measure different things: SpliceAI detects canonical splice site perturbations; minigene assays detect exonic splicing enhancer/silencer disruption. GM_q is good at SpliceAI-agreement because both tools respond to canonical splice sites. L2D_501 is better at minigene discrimination because it amplifies local sharp spikes without gene-body contamination.

### Stratified results

L2D-501 and GM_q are essentially identical in every distance stratum against SpliceAI. The experimental benchmark advantage of L2D does not appear in SpliceAI stratification because SpliceAI and the minigene assays test different mechanisms.

### Codon-pair divergence

CM L2D-501: 43/145 groups show within-group divergence > 0.001 (vs 27/145 for CM DLS-501 and 37/145 for GM_raw). Maximum 0.677. L2D_501 distinguishes more synonymous codon pairs than any previous scorer tested.

Scores saved: `results/alphagenome/l2diff_scores.csv` (1,278 rows).

Full comparison: `docs/scorer_comparison.md`.

---

## 19c — Corrections to rescore_evaluation.md

### 50–500 bp AUPRC qualified

The figures of GM 0.307 and CM 0.081 in the 50–500 bp stratum are computed against 3 SpliceAI>0.5 positives out of 524 variants (baseline 0.6%). They are not withdrawn — the numbers are correct — but are qualified: 41% of the cohort lies beyond SpliceAI's effective detection range. SpliceAI cannot validate anything in this stratum by construction. The substantive finding (stated, not merely implied): most of the cohort cannot be evaluated using SpliceAI as a reference standard.

### Post-hoc selection recorded

The primary concordant-set definition (CM top 5% AND SpliceAI > 0.2) was selected after computing all three definitions. The reason it was chosen: SpliceAI > 0.2 has an external citation (Jaganathan et al. 2019). All three were computed before one was selected. This is now documented in `docs/rescore_evaluation.md` section 19c.

Both corrections applied to `docs/rescore_evaluation.md`.
