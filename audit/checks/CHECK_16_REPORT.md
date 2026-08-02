# Check 16 Report
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**No git operations. Part B locked.**

---

## What I could not establish

1. **Pangolin:** `pangolin 1.0.2` from `tkzeng/Pangolin` installs but fails to import on Python 3.13 (`pkg_resources` removed). Blocked by Python version and absence of reference FASTA and annotation GTF. Cannot report SpliceAI–Pangolin agreement baseline.

2. **16c positive control:** n=12 provides ~20% power at α=0.0167. Non-significant results cannot be interpreted as absence of effect at this size.

---

## 16a + 16b — The correction: stated first

**15c's comparison was unfair but directionally correct.** The center-mask scorer does not improve on the gene-mask scorer. At matched base rates (top 5% of cohort), the gene-mask recovers 16/19 high-confidence SpliceAI variants; the center-mask recovers 13/19. By AUPRC, GM=0.697 vs CM=0.371 at SpliceAI>0.5. The gene-mask is 1.88× better.

**The ATAC control is zero.** 0/19 SpliceAI>0.5 variants in ATAC top 5%. The splice discrimination is modality-specific regardless of scorer.

### 16a — Matched-base-rate table

SpliceAI > 0.5 (n=19), top-5% threshold:

| Scorer | Recovered | Enrichment | Fisher p | OR (95% CI) |
|---|---|---|---|---|
| GM quantile (original 0.95 bar) | 18/19 | 1.6× | 0.0007 | 13.1 (1.7–98.3) |
| GM quantile top 5% | **16/19** | **16.3×** | <0.0001 | **129 (36–457)** |
| GM raw top 5% | 16/19 | 16.1× | <0.0001 | 126 (36–447) |
| **CM splice 501 top 5%** | **13/19** | **13.7×** | <0.0001 | **51 (19–141)** |
| CM ATAC 501 top 5% | 0/19 | 0× | 0.62 | — |

SpliceAI > 0.2 (n=52), top-5% threshold:

| Scorer | Recovered | Enrichment | Fisher p | OR (95% CI) |
|---|---|---|---|---|
| GM quantile top 5% | 34/52 | 12.7× | <0.0001 | 70.5 (36–138) |
| CM splice 501 top 5% | 28/52 | 10.8× | <0.0001 | 38.6 (20–73) |
| CM ATAC 501 top 5% | 1/52 | 0.4× | 0.51 | 0.36 (0.05–2.7) |

### 16b — AUPRC/AUROC

SpliceAI > 0.5 (n=19, baseline=0.015):

| Scorer | AUROC | AUPRC | Lift |
|---|---|---|---|
| **GM quantile** | **0.933** | **0.697** | **46.9×** |
| CM splice 501 | 0.910 | 0.371 | 24.9× |
| CM ATAC 501 | 0.686 | 0.026 | 1.8× |

SpliceAI > 0.2 (n=52, baseline=0.041):

| Scorer | AUROC | AUPRC | Lift |
|---|---|---|---|
| **GM quantile** | **0.895** | **0.587** | **14.4×** |
| CM splice 501 | 0.886 | 0.476 | 11.7× |
| CM ATAC 501 | 0.545 | 0.045 | 1.1× |

Top-10 precision at SpliceAI>0.5: GM=0.900, CM=0.600. Spearman: GM rho=0.287, CM rho=0.292 — tied (indistinguishable, dominated by null bulk).

**Why the gene-mask outperforms despite 87 discrete values:** The gene-mask splice scorer detects canonical CFTR splice site changes. The highest-quantile bins (>0.99) contain variants at or near exon boundaries where both the gene-mask splice probability change and SpliceAI agree on a strong signal. The center-mask DIFF_LOG2_SUM over ±250 bp is noisier because it includes both the variant position and background activity from nearby exon/intron boundaries.

---

## 16c — Twelve CF-causing positive controls

**Pre-registration:** Mann-Whitney U (two-sided), CM_splice_501, CM_ATAC_501, CM_RNA_501, Bonferroni α=0.0167, rank-biserial r.

**Results:**

| Outcome | Median 12 | Median 1266 | p | rank-biserial r |
|---|---|---|---|---|
| CM_splice_501 | 0.01142 | 0.00922 | 0.463 | −0.123 (n.s.) |
| CM_ATAC_501 | 0.01323 | 0.01683 | 0.249 | +0.193 (n.s.) |
| CM_RNA_501 | 0.02306 | 0.02949 | 0.607 | +0.086 (n.s.) |

**All non-significant.** Direction is mixed and small. AUPRC (12 as positives) = 0.0167, baseline 0.0094, lift 1.78×.

**Individual table:** Full in `docs/rescore_evaluation.md`. Notable: I601F is at splice 98.3th and RNA 95.8th percentile (SpliceAI 0.23). H954P is at ATAC 97.7th. Q30P (0.412 AM) is at splice 14.0th, ATAC 3.9th. No consistent pattern.

**n=12 is the finding.** This analysis has been outstanding since Part A5. The result is: non-significant, underpowered, mixed directions. That is the result. It cannot be made stronger without more labelled data.

---

## 16d — Pangolin

**BLOCKED.** Three separate blockers:
1. `pangolin 1.0.2` installs but `from pkg_resources import resource_filename` fails on Python 3.13
2. Reference genome FASTA (GRCh38) absent (~3.1 GB)
3. Gene annotation GTF absent (~50 MB)

Network is available. Fixing blocker 1 requires either a Python ≤ 3.12 environment or patching `resource_filename` to `importlib.resources`. Blockers 2 and 3 require downloads.

The question "does Pangolin distinguish the 145 codon pairs?" and "SpliceAI–Pangolin agreement baseline" remain unanswered.

---

## 16e — Priority 7 corrected

Old SPLICE_q (genome-wide quantile) vs new CM_splice_501 percentile within the 1,278:

| Variant | Old SPLICE_q | New CM_splice | pctile in 1278 | Old ATAC_q | New CM_ATAC | pctile |
|---|---|---|---|---|---|---|
| L49P | 0.821 | 0.00210 | 5.5th | 0.081 | 0.00208 | 6.7th |
| R104G | **0.993** | 0.02587 | **79.3th** | 0.699 | 0.01992 | 56.5th |
| P355L | 0.635 | 0.00033 | 3.4th | 0.537 | 0.01071 | 32.3th |
| F650L | 0.640 | 0.00325 | 19.3th | 0.693 | 0.01963 | 56.2th |
| L986P | 0.931 | 0.00921 | 49.6th | 0.675 | 0.01841 | 53.8th |
| H1054Q | 0.948 | 0.00440 | 22.9th | **0.950** | 0.07507 | **93.5th** |
| R1097C | 0.720 | 0.00464 | 26.0th | 0.905 | 0.04847 | **87.8th** |

**The old gene-mask SPLICE_q was misleading for most of these variants.** Only R104G retains a meaningful splice percentile (79.3th) in the new metric. P355L and L49P drop to 3.4th and 5.5th.

**The ATAC signal is better preserved.** H1054Q (93.5th) and R1097C (87.8th) retain their relative ATAC prominence within the cohort. The original narrative that these two variants have elevated chromatin accessibility signals is qualitatively supported by the center-mask ATAC.

The old RNA_q values (0.956–0.999 for all 7) reflected the gene-mask RNA scorer, which is continuous (941 unique values). New CM_RNA within-cohort percentiles range from 1.7th (L986P) to 79.0th (R104G). The claim that all 7 have strong RNA regulatory signals is not supported at the within-cohort level.

---

## 16f — Replace group definitions

The 693 cannot be reconstituted with the center-mask scorer without an arbitrary threshold. **Do not invent one.**

**CM_splice_501 distribution across 1,278:**

| Statistic | CM_splice_501 |
|---|---|
| Unique values | 994/1278 |
| Median | 0.00924 |
| P90 | 0.04970 |
| P95 | 0.08275 |
| P99 | 0.28477 |
| Max | 1.22526 |

The distribution is continuous and right-skewed. For any categorical table, use within-cohort percentiles and label them as "within-cohort ranking" — never "top X% of all human variants."

The 18 multi-tool concordant variants (top 5% CM splice AND SpliceAI > 0.2, at matched base rate) is the appropriate replacement for the headline figure. OR=38.6 (20–73), p<0.0001.

Full written analysis in `docs/rescore_evaluation.md`.
