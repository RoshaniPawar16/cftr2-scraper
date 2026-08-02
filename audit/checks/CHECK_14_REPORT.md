# Check 14 Report
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**No git operations. Part B locked.**

---

## What I could not establish

1. **14b quantile reproducibility:** The 323-variant run used `predict_variant` (per-bin), not `score_variants`. No new quantile scores were generated. Reproducibility of quantile scores against original requires a separate `score_variants` re-run.
2. **Intermediate scorer values for byte-identical groups:** I derived the likely mechanism (shared dominant bin outside the variant position) analytically. Confirming it precisely requires per-bin data with the gene mask overlaid to identify which bin dominates the scorer.

---

# 14a — Association statistics

**The discordance is at chance. The concordance is the signal. Full writeup in `docs/tool_association_analysis.md`.**

### 2×2 table (SpliceAI > 0.2)

|  | SpliceAI > 0.2 | SpliceAI ≤ 0.2 |
|---|---|---|
| AG splice > 0.95 | 49 (exp 30.4) | **698 (exp 716.6)** |
| AG splice ≤ 0.95 | 3 (exp 21.6) | 528 (exp 509.4) |

χ² = 28.57, p < 0.0001. OR = 12.36 (95% CI 3.83–39.86).

**Discordant cell (698) is 18.6 below the independence expectation (716.6).** The discordance does not exceed chance. The significant association is driven by the concordant cell (49 > 30.4) and the deficit in the AG-low/SpliceAI-high cell (3 vs 21.6).

### 2×2 table (SpliceAI > 0.5)

|  | SpliceAI > 0.5 | SpliceAI ≤ 0.5 |
|---|---|---|
| AG splice > 0.95 | 18 (exp 11.1) | 729 (exp 735.9) |
| AG splice ≤ 0.95 | 1 (exp 7.9) | 530 (exp 523.1) |

χ² = 10.46, p = 0.0012. OR = 13.09 (95% CI 1.74–98.34). Fisher exact p = 0.0007.

### Continuous association

| Predictor | Spearman rho vs SpliceAI | p |
|---|---|---|
| AG splice quantile | **0.287** | **1.2 × 10⁻²⁵** |
| AG ATAC quantile | −0.026 | 0.36 (n.s.) |
| AG RNA quantile | 0.056 | 0.047 (marginal) |

The AG splice quantile correlates positively with SpliceAI delta. The correlation is modality-specific (ATAC is flat, as expected). The tools are correlated, not discordant.

### Recovery

18 of 19 high-confidence SpliceAI variants (> 0.5) have AG > 0.95, vs 11.1 expected. Fisher exact OR = 13.1, p = 0.0007.

### Paper reframing

The 693/698 does not exceed chance. The 18 multi-tool concordant variants do. The paper should lead with "18 variants flagged by both tools at above-chance rates (OR 13.1, p = 0.0007)" not "693 discordant variants suggest mechanistic differences."

---

# 14b — Full 323-variant predict_variant run

**API version:** alphagenome 0.6.1 (matches original run). All 323 variants completed, 0 errors.

## Divergence across all 145 groups

| Level | Median diff | IQR | Max | n > 0.001 | n > 0.1 | n > 1.0 |
|---|---|---|---|---|---|---|
| Per-bin max_lfc diff | 0.410 | [0.182, 0.816] | 10.490 | 144/145 | 124/145 | 28/145 |
| Centre-bin lfc diff | 0.269 | [0.094, 0.518] | 13.295 | 135/145 | 106/145 | 13/145 |
| Scorer raw_max diff (orig) | 0.000 | [0.000, 0.004] | 0.211 | 37/145 | 6/145 | 0/145 |
| Scorer quantile diff (orig) | 0.000 | [0.000, 0.003] | 0.234 | 42/145 | 11/145 | 0/145 |

The contrast is striking. Per-bin divergence is substantial (median 0.41, 28 groups exceed 1.0 lfc); scorer divergence is near-zero (median 0.000, maximum 0.211).

## Group classification

Using noise floor = 0.453 (5th percentile of non-zero per-bin max across all 323 variants):

| Category | Count | Criterion |
|---|---|---|
| H620Q-pattern (large local divergence) | 13 | centre_diff > 1.0 lfc |
| Large per-bin divergence | 28 | perbin_diff ≥ 1.0 |
| Modest per-bin divergence | 38 | noise floor ≤ perbin_diff < 1.0 |
| Below noise floor | 79 | perbin_diff < 0.453 |

79 of 145 groups (54%) are below the noise floor at the per-bin level. For these, the model genuinely assigns similar predictions to the two variants. For the remaining 66 groups (45.5%), the model produces distinguishable per-bin outputs.

## Both A and B are operating

**Explanation B holds for 66 groups (45.5%):** Per-bin divergence is above the noise floor, meaning the model distinguishes the base changes at some spatial scale.

**Explanation A holds (or cannot be excluded) for 79 groups (54.5%):** Per-bin divergence is below the noise floor. Either the model truly does not distinguish these bases, or any divergence is below detection.

**The H620Q pattern (centre_diff > 1.0) generalises to 13 groups**, not just H620Q.

## Byte-identical scorer output explained

88 groups have byte-identical gene-mask scorer raw_max but per-bin divergence > 0.1.

**Mechanism:** The `GeneMaskSplicingScorer(width=None)` takes the **maximum** |lfc| across all bins within the CFTR gene mask (~188,665 bins). For two variants within the same codon, the maximum bin within the gene mask is often dominated by a bin far from the variant position — one whose effect is shared by both variants (long-range structural effects on splice site usage). The variant-position bins, even when locally divergent (up to 13.6 lfc), are outcompeted by this shared maximum elsewhere in the gene.

This is not the scorer diluting signal — it is the scorer being dominated by a different signal. A 1-Mb window over a heavily-spliced 188 kb gene will contain many high-LFC bins where both variants produce the same effect (because those bins are far enough from the variant that the two SNVs are indistinguishable). The local spike at the variant position is real, but it does not dominate the gene-mask maximum.

Demonstration for H620Q:
- Scorer raw_max for T>G = 0.621, for T>A = 0.621 (identical)
- Per-bin max at variant position (centre bin): T>G = 13.65, T>A = −0.27
- Per-bin max over full window: T>G = 13.65, T>A = 3.16

The variant-position bin (13.65) is larger than the scorer output (0.621), so the scorer is NOT simply taking the gene-mask maximum. The scorer maximum (0.621) must come from a DIFFERENT bin that has lfc = 0.621 for BOTH variants — a shared bin that is identical regardless of the T>G/T>A difference.

**Conclusion:** The scorer returns the maximum over the gene mask, but this maximum is set by a shared background bin unrelated to the variant being scored. The variant-specific local signal at the variant position (0–13 lfc) is present but not the dominant effect in the gene-mask maximum. This is a structural limitation of the GeneMaskSplicingScorer approach for coding variants: the gene is large enough that shared background effects set the scorer value.

## Top 10 groups by per-bin divergence

| Group | Per-bin diff | Centre diff | Scorer diff | Example |
|---|---|---|---|---|
| H620Q | 10.49 | 13.30 | 0.000 | T>G (max=13.6) vs T>A (max=3.2) |
| L617F | 4.95 | 0.27 | 0.000 | A>C (max=1.3) vs A>T (max=6.2) |
| T844S | 4.15 | 0.52 | 0.211 | A>T (max=1.1) vs C>G (max=5.2) |
| D651E | 3.52 | 0.53 | 0.000 | C>A (max=1.1) vs C>G (max=4.6) |
| G366R | 3.24 | 0.08 | 0.000 | G>A (max=3.9) vs G>C (max=0.6) |
| S1362R | 2.79 | 0.44 | 0.016 | 3-member group, max diff 2.8 |
| M929I | 2.61 | 0.28 | 0.000 | 3-member group, max diff 2.6 |
| K830N | 2.16 | 0.29 | 0.000 | G>C (max=5.8) vs G>T (max=3.6) |
| D1152E | 1.64 | 2.31 | 0.000 | T>G (max=2.6) vs T>A (max=1.0) |
| T296S | 1.59 | 2.23 | 0.008 | C>G (max=2.5) vs A>T (max=0.9) |

In all top-10 cases, the scorer difference is 0.000 or near-zero despite per-bin differences of 1.6–10.5.

---

# 14c — Scope of Phase 2 rescore

## Available scorers relevant to local splice disruption

From `vsl.RECOMMENDED_VARIANT_SCORERS`:

| Scorer key | Class | Width | Notes |
|---|---|---|---|
| `SPLICE_SITE_USAGE` | `GeneMaskSplicingScorer` | None (full gene) | Current scorer — masks full gene; explains byte-identical results |
| `SPLICE_SITES` | `GeneMaskSplicingScorer` | None | Similar; scores donor/acceptor site predictions |
| `SPLICE_JUNCTIONS` | `SpliceJunctionScorer` | — | Scores specific junction reads directly |

**Appropriate scorer for local coding-position splice disruption:**

`CenterMaskScorer(SPLICE_SITE_USAGE, width=501, aggregation_type=DIFF_LOG2_SUM)` is constructable from the API:

```python
vsl.CenterMaskScorer(
    requested_output=dna_output.OutputType.SPLICE_SITE_USAGE,
    width=501,
    aggregation_type=vsl.AggregationType.DIFF_LOG2_SUM
)
```

This masks ±250 bins (±250 bp) centred on the variant — consistent with the SpliceAI window (±50 nt for strong effects; ±400 nt for weaker). This scorer IS supported by the constructor and would capture the local splice signal demonstrated in Check 12.

`GeneMaskSplicingScorer(width=101)` is also supported (width=101, ±50 bp). This is narrower, which is appropriate for splice site effects but may miss exon-internal effects.

**Avsec et al. 2026:** The paper does not specify a recommended local window for coding variant prioritisation. The recommended scorers use full gene masking. No guidance is given for the width parameter in clinical or local-variant contexts.

## What a local-window rescore requires

- **Window:** ±250 bp (width=501) centred on the variant position. This captures splice site consensus sequences (GT-AG rule, branch point at −20 to −40 nt from acceptor) and exonic splice enhancers/silencers.
- **Centring:** Each variant is scored with its own centred window (not a shared gene window).
- **Aggregation:** `DIFF_LOG2_SUM` (difference in log2-sum of predictions between ref and alt within the window). This is the standard for `CenterMaskScorer`.
- **Output type:** `SPLICE_SITE_USAGE` (models probability of each position being used as a splice site).

## Estimated runtime

The original 1,278-variant `score_variants` run took ~20–40 minutes in batches of 20. A rescore with a new scorer configuration uses the same API and batch structure. Estimate: **20–40 minutes** for the 1,278 variants.

## Original run retention

The original run is committed in `results/alphagenome/alphagenome_full_cftr_results.csv` with gene-mask raw_max and quantile columns. The per-bin predictions from the original run were NOT retained (the original run used `score_variants`, which returns only scalars). A rescore with the local-window scorer requires a new API call for all 1,278. The original scorer outputs are not convertible.

## Quantile availability

Pre-computed genome-wide quantile normalisation is available from the AlphaGenome API only for the **RECOMMENDED_VARIANT_SCORERS** (keys: ATAC, RNA_SEQ, SPLICE_SITE_USAGE, etc.). These quantiles are computed against the genome-wide distribution of that scorer's output.

`CenterMaskScorer(SPLICE_SITE_USAGE, width=501)` is NOT in the recommended set. **No genome-wide quantiles exist for this scorer.** The rescore would produce raw `DIFF_LOG2_SUM` values only.

Consequence:
- The 0.95 quantile threshold (already unjustified externally) cannot be applied — there is no genome-wide distribution to normalise against.
- A new threshold strategy is required: either (a) an empirical distribution from a reference set of known-benign variants, (b) a percentile within the 1,278 themselves (relative ranking), or (c) calibration against the 12 known CF-causing variants in the cohort.
- The 693, 18, and 58 counts would not be directly reproducible on the new scorer — entirely new counts at a new threshold.

## What would change in the paper if the rescore produces materially different results

If the local-window `CenterMaskScorer(SPLICE_SITE_USAGE, 501)` scores produce materially different rankings (different top-candidate variants, different concordance with SpliceAI), the following would change:

The paper's Phase 2 section currently presents 728–693 "discordant" variants flagged by AlphaGenome but not SpliceAI. The 14a finding already establishes that this discordance does not exceed chance. If the rescore also reveals that the gene-mask quantile does not rank variants according to local splice disruption (confirmed by Check 12 for 88/145 groups), then the Phase 2 splicing analysis requires complete replacement: new scorer, new raw scores, new threshold (not quantile-based), new counts. The 693, 18, 58 figures are specific to the gene-mask quantile approach and cannot survive a scorer change.

The 7-variant analysis (Phase 1 priority candidates) is unaffected — it used `predict_variant` with full per-bin outputs and log2FC summaries, not gene-mask quantiles.

The AlphaMissense results (AUC 0.946, comparator benchmarks) are completely unaffected — they use a different model and pipeline.

The ATAC quantile results are also affected by this analysis (88 groups with identical ATAC raw_max). However, ATAC has no mechanistic reason to correlate with splicing (confirmed: rho = −0.026, p = 0.36), so the ATAC findings are not driven by splice-confounding. The ATAC score is also a gene-mask score (DIFF_LOG2_SUM, width not applicable to gene-mask). The same structural argument applies: local ATAC changes are dominated by shared background CFTR gene-body effects.
