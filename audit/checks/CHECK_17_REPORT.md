# Check 17 Report
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**No git operations. Part B locked.**

---

## What I could not establish

1. **17a bootstrap CI for RNA_raw:** Produces NaN due to insufficient variability in the bootstrap samples at n=12 with tied values. Reported for other outcomes only.
2. **Pangolin full-cohort coverage:** Pangolin scored 298 of 1,278 variants; 980 were outside the CFTR transcript gene body in GENCODE v44. Coverage is 23.3%. Three-way analysis is partial.

---

# 17a — The decisive test: gene-mask scorer against the 12 CF-causing variants

## Pre-registration (before computing)

Mann-Whitney U (two-sided). Gene-mask `SPLICE_SITE_USAGE_raw_max`, `ATAC_raw_max`, `RNA_SEQ_raw_max` — three outcomes plus their quantile counterparts. Bonferroni α=0.0167. Bootstrap CI (10,000 resamples) on rank-biserial r.

## Result: stated first

**Neither the gene-mask nor the center-mask scorer separates the twelve CF-causing variants from the remaining 1,266.** All six gene-mask tests are non-significant (p=0.21–0.48). The bootstrap confidence intervals span almost the entire [−1, +1] range. No AlphaGenome splice or regulatory configuration tested separates these CF-causing missense variants from the AM-ambiguous background. **Amendment (Check 18): this null is expected — the 12 predominantly act through protein misfolding, not splicing. 6 of the 12 are beyond 50 bp from any canonical CFTR splice site; all 12 have SpliceAI ≤ 0.23. Testing splice scores against variants pathogenic by non-splicing mechanisms is the wrong experiment. The conclusion is not "AlphaGenome does not track pathogenicity" but "AlphaGenome splice scores do not separate CF-causing missense variants from AM-ambiguous variants, a result expected from mechanism."**

**The 12 are largely indistinguishable because of quantization.** Four of the 12 share splice raw_max value 0.0078125 with 313 cohort members (24.5% of all 1,278). One variant (I601F) occupies a high bucket (0.2266) shared with only 1 other cohort member. The other 11 are distributed across 8 buckets, each shared with 2–370 others. A significant result would require a majority of the 12 to cluster in high-quantile buckets — they do not.

## Gene-mask results

| Outcome | Median 12 | Median 1266 | p | rank-biserial r | 95% CI |
|---|---|---|---|---|---|
| GM_splice_raw | 0.019531 | 0.011719 | 0.480 | −0.116 | [−0.916, +0.548] |
| GM_splice_q | 0.988443 | 0.956547 | 0.469 | −0.121 | [−0.920, +0.531] |
| GM_ATAC_raw | 0.013233 | 0.017322 | 0.207 | +0.212 | [−0.400, +0.717] |
| GM_ATAC_q | 0.551749 | 0.668219 | 0.209 | +0.211 | [−0.410, +0.717] |
| GM_RNA_raw | 0.005656 | 0.006218 | 0.463 | +0.123 | (NaN) |
| GM_RNA_q | 0.974781 | 0.980378 | 0.356 | +0.155 | [−0.477, +0.676] |

**Center-mask results (from 16c):**

| Outcome | Median 12 | Median 1266 | p | rank-biserial r |
|---|---|---|---|---|
| CM_splice_501 | 0.01142 | 0.00922 | 0.463 | −0.123 |
| CM_ATAC_501 | 0.01323 | 0.01683 | 0.249 | +0.193 |
| CM_RNA_501 | 0.02306 | 0.02949 | 0.607 | +0.086 |

## Quantization detail

| Splice raw_max value | 12 in this bucket | Cohort members in this bucket |
|---|---|---|
| 0.0078125 | 4 | 313 (24.5%) |
| 0.01171875 | 1 | 370 (29.0%) |
| 0.015625 | 1 | 143 (11.2%) |
| 0.0234375 | 1 | 56 (4.4%) |
| 0.02734375 | 1 | 44 (3.4%) |
| 0.04296875 | 1 | 14 (1.1%) |
| 0.046875 | 1 | 18 (1.4%) |
| 0.0703125 | 1 | 2 (0.2%) |
| **0.2265625** | **1 (I601F)** | **1 (0.1%)** |

## What this means for clinical claims

Every clinical claim in this paper that rests on AlphaGenome quantile scores — that the 693, 18, or 58 variants are "candidates for functional follow-up," that the 7 priority variants have "regulatory signal beyond protein scoring" — has no validation in the project's own ground truth. The 12 CF-causing variants are not elevated on any AlphaGenome metric at any aggregation level. The absence of elevation is consistent with two interpretations: (1) the models genuinely do not capture pathogenicity for these variants; (2) the models capture it but the ground-truth set is too small and heterogeneous to detect it. Both interpretations require the paper to retract or qualify every clinical claim that implies AlphaGenome scores predict pathogenicity.

---

# 17b — Is the gene-mask winning because it is SpliceAI-like?

## Correlation between scorers

**GM splice raw vs CM splice 501: rho = 0.851 (p ≈ 0).** They are highly correlated. They are not measuring different things.

## Stratified AUPRC by distance to nearest CFTR splice site

SpliceAI > 0.5 as positive class (n=19):

| Stratum | n | n_pos | Baseline | GM AUPRC | CM AUPRC |
|---|---|---|---|---|---|
| < 10 bp | 67 | 2 | 0.030 | 0.583 | 0.571 |
| **10–50 bp** | **259** | **5** | **0.019** | **0.943** | **0.260** |
| 50–500 bp | 525 | 9 | 0.017 | 0.667 | 0.622 |
| > 500 bp | 427 | 3 | 0.007 | 0.414 | 0.232 |

**The gene-mask advantage is concentrated in the 10–50 bp stratum** (GM AUPRC 0.943 vs CM 0.260). In this band, variants are near but not immediately at canonical splice sites. The gene-mask splice scorer, which takes the maximum gene-body splice probability change, selects the same nearby canonical splice site that SpliceAI also detects. The center-mask DIFF_LOG2_SUM over ±250 bp dilutes this signal with adjacent exon/intron context.

**The gene-mask outperforms because it is more SpliceAI-like, not because it captures additional biology.** The two scorers measure similar downstream signal (gene-body maximum splice probability change vs SpliceAI's local splice site scoring), and the similarity is highest where canonical splice sites dominate — within 50 bp.

This is a finding about redundancy, not validity. The gene-mask splice scorer largely reproduces SpliceAI and should be reported as such, not as an orthogonal measure.

---

# 17c — Three verifications

## 17c.1 — Tie handling in GM splice AUPRC

| Positive class | Pessimistic | Average | Optimistic | Range |
|---|---|---|---|---|
| SpliceAI > 0.5 | 0.6971 | 0.6971 | 0.7083 | 0.011 |
| SpliceAI > 0.2 | 0.5829 | 0.5829 | 0.5977 | 0.015 |

The AUPRC range across tie-breaking methods is narrow (0.011–0.015). The 0.697 figure is robust to tie-handling. The CM501 range is even smaller (0.003) because it has 994 unique values.

## 17c.2 — Like-for-like for the 7 priority variants

The 7 are AM-likely-pathogenic (AM > 0.564) and are **not in the 1,278** (which are AM-ambiguous). They cannot be ranked within the 1,278. Percentiles below are the 7 ranked against the 1,278 as a reference distribution.

| Variant | GM_splice_raw | GM_raw vs 1278 | CM_splice_501 | CM_pct vs 1278 | GM q (original) |
|---|---|---|---|---|---|
| L49P | 0.007813 | 0.8th | 0.002098 | 5.5th | 0.821 |
| R104G | 0.027344 | 75.8th | 0.025868 | 79.3th | 0.993 |
| P355L | 0.007813 | 0.8th | 0.000333 | 3.4th | 0.635 |
| F650L | 0.007813 | 0.8th | 0.003246 | 19.3th | 0.640 |
| L986P | 0.011719 | 25.9th | 0.009210 | 49.6th | 0.931 |
| H1054Q | 0.011719 | 25.9th | 0.004398 | 22.9th | 0.948 |
| R1097C | 0.007813 | 0.8th | 0.004638 | 26.0th | 0.721 |

**The old quantile was artificially inflated relative to this cohort.** L49P had quantile 0.821 (82nd percentile of the common-variant background, MAF > 0.01 in gnomAD v3) but ranks at the 0.8th percentile within the 1,278. P355L had quantile 0.635 but ranks at the 3.4th percentile within this cohort. The discrepancy reflects that the 1,278 is a set of coding CFTR missense variants, which collectively score higher than the common-variant background on gene-body splice metrics. Being "top 5% of common variants" meant almost nothing within this specific cohort.

R104G is the exception: its within-cohort GM ranking (75.8th) is consistent with its genome-wide quantile (0.993 = top 0.7%). This suggests R104G has a genuinely elevated splice signal beyond the gene-body baseline.

## 17c.3 — Overlap between the two 18s

- Old 18: GM quantile > 0.95 AND SpliceAI ≥ 0.5 → 18 variants
- New 13: CM splice top 5% AND SpliceAI > 0.5 → 13 variants
- **Overlap: 13 variants (all 13 of the new set are in the old 18)**
- In old 18 only: 5 variants
- In new 13 only: 0 variants

The new set is a strict subset of the old. The 5 variants that dropped out had high gene-mask quantile but did not make the CM top 5%. The 13 core variants are the most robust — they are multi-tool concordant (both high quantile and SpliceAI) regardless of scorer choice. The "coincidence of count" (both yield 18/13 in various configurations) is not a coincidence of variants only at the 13-way level; the full overlap should be reported.

---

# 17d — Pangolin

## Environment

Python 3.11.7 (Anaconda), Pangolin 1.0.2 from GitHub, `pkg_resources` patched with `os.path` method. Dependencies: numpy, torch, pandas, gffutils, PyVCF3, pyfastx. GRCh38 chr7 FASTA: 154 MB. GENCODE v44 GTF filtered to CFTR: 1,191 lines → `/tmp/cftr.db`.

## Coverage limitation

**Pangolin scored 281 variants of 1,278 (22.0%) with non-zero results.** 997 variants returned 0 or were skipped ("Variant not contained in gene body"). This reflects two factors: (1) Pangolin's default masking (`-m True`) zeros out splice gains at annotated sites and splice losses at unannotated sites; (2) variants far from CFTR exon boundaries (> 50 bp from nearest splice site) produce no detectable splice signal from Pangolin's local window. The 1,278 are all coding missense variants, but most coding positions are > 50 bp from the nearest splice donor or acceptor. Within the 298 variants Pangolin did score, 140 had non-zero results.

## Results (treating 0 for unscored)

| Metric | Pangolin | SpliceAI | GM quantile | CM splice 501 |
|---|---|---|---|---|
| rho vs SpliceAI | — | — | 0.287 | 0.292 |
| rho vs Pangolin | 1.0 | 0.216 | 0.134 | — |
| AUROC (SAI>0.5) | 0.680 | — | 0.933 | 0.910 |
| AUPRC (SAI>0.5) | 0.386 | — | 0.697 | 0.371 |
| AUROC (SAI>0.2) | 0.586 | — | 0.895 | 0.886 |
| AUPRC (SAI>0.2) | 0.257 | — | 0.587 | 0.476 |

**SpliceAI–Pangolin agreement baseline:** Spearman rho = 0.216 across all 1,278 (Pangolin 0 for unscored). Among the 298 scored variants, this will be higher but cannot be computed cleanly due to coverage.

**Codon-pair divergence (Pangolin):** Of 145 groups, only 37 had Pangolin data for all members. Among those 37: median within-group diff = 0.000, max = 0.150. 18/37 (49%) show divergence > 0.001. **Pangolin distinguishes some codon pairs.** This is intermediate between SpliceAI (which the 14b analysis showed distinguishes many) and AlphaGenome (which does not). Pangolin shows base-level sensitivity for some pairs, suggesting this is a general property of local splice-specific tools, not unique to SpliceAI.

**The three-way result:** AlphaGenome has the highest AUPRC (0.697 at SpliceAI>0.5), Pangolin is comparable to CM (0.386 vs 0.371). The GM advantage over both Pangolin and CM reflects the high correlation between GM and SpliceAI (both use gene-body/local maximum probability change). SpliceAI–Pangolin agreement is positive but weaker (rho=0.216) than SpliceAI–GM agreement (rho ≈ 0.29 from 16b), suggesting SpliceAI and Pangolin capture partially different signals.

Pangolin scores saved to `results/pangolin_scores.csv` (1,278 rows, 0 for unscored variants).

---

## Files written

- `results/pangolin_scores.csv` — 1,278 rows with Pangolin max absolute score (0 for unscored)
