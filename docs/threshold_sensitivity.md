# Threshold Sensitivity Analysis: Discordant Count and Multi-Tool Confirmed Count

**Date:** 2026-08-02  
**Branch:** integrity-audit-2026-07

---

## Context

The discordant count (693) and multi-tool confirmed count (18) were computed at fixed thresholds:
- AlphaGenome splice quantile > 0.95
- SpliceAI max delta < 0.2 (discordant) or ≥ 0.5 (multi-tool confirmed)

These thresholds are not symmetric in their justification. SpliceAI's cutoffs (0.2 = "potentially splice-altering", 0.5 = "high confidence") are the tool authors' own, published in Jaganathan et al. 2019 and cited by the AlmaBiosciences guidelines. The AlphaGenome 0.95 quantile threshold has no external citation — it is ours.

---

## Full threshold grid

### Discordant count: splice_q > AG_threshold AND SpliceAI < SAI_threshold

| AG threshold | SpliceAI < 0.1 | SpliceAI < 0.2 | SpliceAI < 0.5 |
|---|---|---|---|
| > 0.80 | 1,042 | 1,099 | 1,136 |
| > 0.85 | 979 | 1,034 | 1,071 |
| > 0.90 | 877 | 931 | 966 |
| > **0.95** | **646** | **693** | **728** |
| > 0.99 | 292 | 324 | 355 |

### Multi-tool confirmed: splice_q > AG_threshold AND SpliceAI ≥ SAI_threshold

| AG threshold | SpliceAI ≥ 0.1 | SpliceAI ≥ 0.2 | SpliceAI ≥ 0.5 |
|---|---|---|---|
| > 0.80 | 114 | 57 | 20 |
| > 0.85 | 112 | 57 | 20 |
| > 0.90 | 108 | 54 | 19 |
| > **0.95** | 101 | **18** (note: table uses SpliceAI ≥ 0.5) | **18** (at SpliceAI ≥ 0.5) |
| > 0.99 | 81 | 49 | 18 |

*Note: the headline "18 multi-tool confirmed" uses splice_q > 0.95 AND SpliceAI ≥ 0.5 simultaneously. At AG>0.95, SpliceAI≥0.5 gives 18 and is stable across 0.90–0.95.*

---

## 13b — Headline sensitivity: SpliceAI fixed at 0.2

| AG threshold | Discordant | Total above AG | % discordant |
|---|---|---|---|
| > 0.80 | 1,099 | 1,156 | 95.1% |
| > 0.85 | 1,034 | 1,091 | 94.8% |
| > 0.90 | 931 | 985 | 94.5% |
| > **0.95** | **693** | **747** | **92.8%** |
| > 0.99 | 324 | 373 | 86.9% |

**The headline count swings from 324 to 1,099 across the 0.95–0.99 and 0.80–0.95 range.** Moving from 0.95 to 0.99 drops the discordant count from 693 to 324 — a halving. Moving from 0.95 to 0.90 raises it to 931. The number is substantially a function of the threshold.

---

## 13c — Splice quantile distribution

Histogram across all 1,278 variants (bin width 0.05):

```
[0.00, 0.05):    0
[0.05, 0.10):    1
[0.10, 0.15):    0
[0.15, 0.20):    0
[0.20, 0.25):    2
[0.25, 0.30):    1
[0.30, 0.35):    3
[0.35, 0.40):    2
[0.40, 0.45):    0
[0.45, 0.50):    1
[0.50, 0.55):    6
[0.55, 0.60):    3
[0.60, 0.65):   16
[0.65, 0.70):   15
[0.70, 0.75):   31
[0.75, 0.80):   41
[0.80, 0.85):   65
[0.85, 0.90):  106
[0.90, 0.95):  238   ← dense cluster below 0.95
[0.95, 1.00):  747   ← 58.4% of all variants
```

**The distribution is strongly right-skewed, with 747 of 1,278 variants (58.4%) above 0.95.** The 0.95 threshold does NOT sit in a sparse region — there is a dense cluster in [0.90, 0.95) containing 238 variants. Moving the threshold from 0.95 to 0.90 pulls in 238 more variants; moving to 0.99 drops 374. Small shifts produce large count changes.

**This means the 0.95 threshold is a poor place to cut.** The distribution is not bimodal around this value. A meaningful threshold would sit at a valley in the distribution, which does not exist here. The 1,278 consists almost entirely of variants with high splice quantiles (median > 0.95).

**Why are splice quantiles so high for all 1,278?** These are coding-exon missense variants, all inside the gene body. The `GeneMaskSplicingScorer` uses a gene body mask — it is, by construction, sensitive to variants inside genes. The result that 58.4% score above 0.95 reflects gene-body scoring bias, not variant-specific splice effects.

---

## 13d — External justification for the 0.95 threshold

**Avsec et al. 2026** (AlphaGenome paper) do not specify a threshold for quantile scores in clinical or variant-prioritisation contexts. They use quantile scores as a continuous variable and characterise performance genome-wide. No specific cut-off is suggested.

**Consequence:** The paper must either:
1. Present the full sensitivity curve (table above) rather than defending a single cut at 0.95, or
2. Adopt a threshold derived from an external ground truth — for example, the quantile at which the multi-tool confirmed count (SpliceAI ≥ 0.5 AND AlphaGenome) peaks, or a threshold calibrated against known splice-disrupting variants.

The SpliceAI 0.2 and 0.5 thresholds are citable; the AlphaGenome 0.95 is not. The paper should not present 693 as a single authoritative figure without the sensitivity table.

---

## Recommendation

Report the discordant count as a function of both thresholds. The table in 13a is the appropriate summary. If a single figure is required, it must be accompanied by: (1) a citation for any threshold used, or (2) the sensitivity curve showing the range.

The additional finding from Check 12 applies here: because the gene-mask scorer returns identical scores for synonymous codon variants, 19 groups of variants with the same amino acid change straddle the boundary. These are artefacts of scoring methodology, not of biology. The paper should acknowledge that the 693 and 18 figures reflect gene-masked aggregation scores rather than base-specific splice predictions.
