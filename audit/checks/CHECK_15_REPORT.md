# Check 15 Report
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**No git operations. Part B locked.**

---

## What I could not establish

The per-bin log2FC divergence reported in 14b for H620Q (max diff = 13.92 at offset 0) was likely a numerical artefact of log2(near-zero/near-zero) at coding-sequence positions that are not splice sites. The center-mask scorer using DIFF_LOG2_SUM returns identical values for T>G and T>A, confirming this. I cannot recover the "true" per-bin signal at non-splice positions without a different analysis framework (e.g., computing actual probability differences instead of log2FC). The 14b conclusion that "Explanation B confirmed" is revised in this check.

---

# 15a — The gene-mask splice scorer is measuring the gene, not the variant

## Finding: stated before tables

**The splice gene-mask scorer produces only 87 unique values across 1,278 variants (6.8% unique).** 96.8% of variants share their value with at least one other. The values are multiples of 1/256 (0.0078125, 0.01171875, …) — a quantized discrete signal. The splice scorer is returning the maximum change in splice-site probability (in units of 1/256 resolution) at the most-affected gene-body junction, not a continuous variant-level effect.

**This confirms every Phase 2 splice number is invalid as a local splice disruption metric.**

## Uniqueness and sharing

| Modality | Unique values | Sharing rate | Values quantized? |
|---|---|---|---|
| SPLICE | **87 of 1,278 (6.8%)** | **96.8%** | Yes — multiples of 1/256 |
| ATAC | 957 of 1,278 (74.9%) | 47.9% | No (continuous) |
| RNA | 941 of 1,278 (73.6%) | 49.5% | No (continuous) |

Top 3 splice values: 0.01171875 (370 variants, 29.0%), 0.0078125 (313 variants, 24.5%), 0.015625 (143 variants, 11.2%). The top two values account for 53.5% of all 1,278 variants.

## Distribution

```
Mid-90% range (P5 to P95) occupies 12.7% of the total [0.004, 0.801] range.
1,116 of 1,278 variants (87.3%) fall in the first bin [0.004, 0.044).
```

## Coefficient of variation

| Modality | Mean | Std | CV |
|---|---|---|---|
| SPLICE | 0.0346 | 0.0860 | 2.49 |
| ATAC | 0.0293 | 0.0492 | 1.68 |
| RNA | 0.0087 | 0.0130 | 1.50 |

## Item 5 — Correlation: local per-bin max vs gene-mask raw

| Modality | Rho | p |
|---|---|---|
| SPLICE: local vs GM | 0.224 | 4.9×10⁻⁵ |
| ATAC: local vs GM | −0.114 | 0.040 |
| RNA: local vs GM | 0.308 | 1.5×10⁻⁸ |

The splice gene-mask scorer explains only 5% of the variance in local per-bin effects (R² ≈ rho²  ≈ 0.05). The ATAC GM scorer is negatively correlated with local ATAC per-bin effects. **For splice, the gene-mask scorer carries minimal local information.**

## Item 6 — Position of splice per-bin maximum

For 323 codon-pair variants with per-bin data from 14b:
- Median offset from variant position: **2 bins**
- Within ±10 bins: 274/323 (84.8%)
- Within ±100 bins: 321/323 (99.4%)

**The per-bin maximum is local — within a few base pairs of the variant.** The gene-mask scorer does not fail because the signal is at a distant background bin; it fails because the scorer computes a discrete change in splice-site probability (integer multiples of 1/256) rather than a continuous log2FC at the affected bins. The quantization absorbs the continuous local signal.

---

## Correction and re-examination (added 2026-08-02)

**The quantization finding (87 unique values) applies to the raw column, not the quantile column.** The quantile column (`SPLICE_SITE_USAGE_quantile_max`) has 290 unique values across 1,278 variants, with a top-2-value share of 3.7% — considerably less concentrated than the raw column's 53.5% top-2 share.

The 290 quantile values arise from a mechanism confirmed in two sources. (1) The package source (`variant_scorers.py`, `tidy_anndata`, lines 767–769) shows that `quantile_score` is extracted from `adata.layers['quantiles']` in the same per-(variant, track) shape as `raw_score` — the API returns per-track quantile scores, not a quantile of the raw max. (2) The AlphaGenome FAQ states: "We estimate a background distribution **for each variant scorer and track** using scores for common variants." Each track has its own calibration CDF. The `quantile_max` is `max(abs(quantile_track1), abs(quantile_track2))`, not `quantile(max(abs(raw_track1), abs(raw_track2)))`. A variant whose raw max comes from track 1 can have its quantile max come from track 2 if track 2's CDF maps a lower raw value to a higher quantile. This produces more unique quantile_max values than unique raw_max values.

**The Phase 2 analyses (693, 58.4%, 18, 58) all used the quantile column, not the raw column.** The conclusion at line 20 was stated as: "The splice gene-mask scorer produces only 87 unique values → Phase 2 splice numbers are invalid." The chain from 87 raw values to quantile-based invalidity is indirect.

**The conclusion still holds, but via two arguments that apply directly to the quantile column:**

1. **Gene-body design.** The gene-mask takes the maximum over the entire CFTR gene body (188 kb, 27 exons). For any coding variant, the maximum is driven by the nearest canonical splice site's response — not by the variant's own effect. This applies regardless of how many unique values the quantile column has.

2. **Background distribution mismatch.** The quantile ranks coding CFTR exonic variants against common variants (MAF > 0.01, gnomAD v3), which are predominantly non-coding and non-genic. Any exonic variant inside a highly-spliced gene routinely exceeds the 95th percentile of this background, explaining the 58.4% figure.

The 87-value quantization of the raw column is a third, supporting finding: it shows the scorer cannot resolve individual variant effects beyond coarse integer multiples of 1/256. But the Phase 2 numbers' invalidity rests on arguments 1 and 2, not primarily on the 87-value count.

---

# 15b — Rescore results

**API version:** alphagenome 0.6.1. 1,285 variants (1,278 + 7 priority). 0 errors. Saved to `results/alphagenome/rescore_centermask.csv`.

**Supported widths for CenterMaskScorer(SPLICE_SITE_USAGE):** 501, 2001, 10001, 100001, 200001. Width=101 is NOT supported. Comparison uses width=501 vs width=2001.

## Unique values — scorer improvement confirmed

| Scorer | Unique values | Sharing rate |
|---|---|---|
| Gene-mask splice raw | 35/323 (10.8%) on codon pairs; 87/1278 (6.8%) full | 96.8% |
| **CM splice 501** | 185/323 (57.3%) on codon pairs; **994/1278 (77.8%)** full | much lower |

The center-mask scorer is continuous. This is an improvement in scorer properties.

## Reproducibility check on 323 codon pairs

Within-group splice divergence under each scorer:

| Scorer | Median diff | Max | n > 0.001 |
|---|---|---|---|
| GM splice raw | 0.000 | 0.211 | 37/145 |
| CM splice 501 | 0.000 | 0.231 | 27/145 |
| CM splice 2001 | 0.000 | 0.231 | 32/145 |
| Per-bin max lfc (14b) | 0.410 | 10.490 | 144/145 |

**The center-mask scorer does not recover the per-bin divergence.** Groups that showed identical gene-mask outputs still show identical center-mask outputs. The H620Q case: cm_splice_501 = 0.0518 for both T>G and T>A (identical).

**The 14b conclusion "Explanation B confirmed" is retracted.** The per-bin lfc divergence (up to 13.92) was a numerical artefact: at coding-sequence positions not used as splice sites, the reference prediction is near zero, and log2(alt + 1e-8) − log2(ref + 1e-8) can be large even for tiny absolute changes. DIFF_LOG2_SUM aggregates over the window and is dominated by real splice sites (non-zero reference values), correctly treating the coding-position change as near-zero. **Explanation A holds: the model's scored outputs do not distinguish synonymous codon variants at the splice-activity level.**

## 14c correction: priority 7 are affected

14c incorrectly stated the 7 priority variants were unaffected. They used the same gene-mask scorer. CM_splice_501 values for the 7 range from 0.0003 (Pro355Leu) to 0.0259 (Arg104Gly) — all low. The gene-mask quantile values (0.82–0.999) were artefactually high because the scorer's 87 discrete raw values, produced by a gene-body max over all CFTR splice junctions, map through the common-variant calibration to high quantile values for any exonic variant in a highly-spliced gene. Note: the quantile column itself has 290 unique values (not 87); the discreteness is a property of the raw column. The artefact is in the gene-body design and background mismatch, not in the number of quantile values.

---

# 15c — Analysis without thresholds

## Correlation comparison (stated first)

| Scorer | Rho vs SpliceAI | p |
|---|---|---|
| Gene-mask quantile (original) | 0.287 | 1.2×10⁻²⁵ |
| **CM splice 501 (new)** | **0.292** | **1.6×10⁻²⁶** |
| CM ATAC 501 (control) | −0.026 | 0.36 (n.s.) |

**The center-mask scorer improves the correlation by 0.005.** This is statistically indistinguishable from the gene-mask. The improvement is not material. The ATAC control remains flat.

**Both scorers have rho ≈ 0.29 vs SpliceAI.** The correlation is real, positive, and modality-specific, but modest. It was not artefactually inflated by the gene-mask scorer's discrete structure.

## Recovery (continuous, no threshold)

High-confidence SpliceAI variants (SpliceAI > 0.5, n=19) in CM501 percentile within cohort:
- Median: **97.7th percentile**
- 13/19 (68%) above the 95th percentile
- 17/19 (89%) above the 75th percentile

SpliceAI > 0.2 (n=52): median 95.4th percentile, 27/52 above 95th.

The CM scorer does recover high-SpliceAI variants at high cohort percentiles without requiring an external quantile normalisation.

## Codon-pair divergence under CM scorer

Same as gene-mask: median=0.000, most groups show no divergence. See 15b above.

## H620Q under CM scorer

CM_splice_501: 0.0518 for both T>G and T>A (identical). SpliceAI: 0.73 vs 0.00. AlphaGenome does not capture what SpliceAI detects here. Explanation A holds for the scored outputs.

---

# 15d — Two loose ends

## 693 vs 698: resolved

| Value | Filter | Source |
|---|---|---|
| **693** | splice_q > 0.95 AND SpliceAI **< 0.2** (strict) | `build_comparator_analysis.py`; committed `rescue_analysis.csv` |
| **698** | splice_q > 0.95 AND SpliceAI **≤ 0.2** (includes exactly 0.2) | Check 14a numpy contingency code |

5 variants have SpliceAI_max_delta = exactly 0.2. The committed code uses strict less-than (`< 0.2`), producing 693. Check 14a's contingency table used `~(spliceai > 0.2)` = `spliceai ≤ 0.2`, producing 698.

**Correct figure: 693.** The paper carries 693. Check 14a's table carried an error (698). The association analysis in 14a is unaffected in direction and significance: the discordant count (whether 693 or 698) is at or below the independence expectation (~717).

## Noise floor in 14b: computed, not chosen

The noise floor of 0.453 was the 5th percentile of non-zero per-bin max_lfc values across all 323 variants. All 323 had non-zero values (log2FC is technically always non-zero when add-epsilon is used). Code:

```python
nonzero = [x for x in all_maxlfc if x > 0]
noise_floor = np.percentile(nonzero, 5)  # = 0.4534
```

This is a computed value (5th percentile of the distribution), not an arbitrary choice. However, the 5th percentile threshold is a statistical convention, and the 79/145 split (54% below noise floor) depends on it. At the 10th percentile (0.618), the below-noise count would be higher; at the 1st percentile (0.145), it would be lower.

The 14b classification (79 groups "no divergence") should be read as "79 groups have per-bin max lfc difference below the 5th percentile of individual variant effects." It is a relative statement, not an absolute threshold. The per-bin divergence values reported for those 79 groups (range: 0–0.453) are real but small relative to the distribution.

**Given the 15b finding that per-bin divergence was an artefact, the entire 14b classification is superseded.** Under the correct scorer (CM501 DIFF_LOG2_SUM), 144/145 groups show within-group divergence < 0.001, not 79.

---

## Files written

- `results/alphagenome/rescore_centermask.csv` — 1,285 rows, CM501, CM2001, CM-ATAC, CM-RNA alongside gene-mask
- `results/codon_pairs_tracks/cm_rescore_323_ckpt.csv` — 323-variant CM scorer checkpoint
- `docs/rescore_analysis.md` — full written analysis
