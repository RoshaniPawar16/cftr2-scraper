# Rescore Analysis: CenterMaskScorer vs GeneMaskSplicingScorer
**Date:** 2026-08-02  
**Branch:** integrity-audit-2026-07  
**Scorer:** CenterMaskScorer(SPLICE_SITE_USAGE, width=501, DIFF_LOG2_SUM) and width=2001  
**Cohort:** 1,278 AM-ambiguous CFTR variants + 7 priority variants = 1,285 total  
**Version:** alphagenome 0.6.1

---

## Summary: the rescore does not materially improve correlation with SpliceAI

**Correlation improvement: gene-mask rho=0.287 → center-mask rho=0.292.** The center-mask scorer recovers almost no additional correlation with SpliceAI over the gene-mask scorer. The ATAC control remains flat (rho=−0.026). The center-mask scorer is better-behaved (994 unique values vs 87 for splice gene-mask) but does not correct the fundamental limitation.

**H620Q under the center-mask scorer:** Both T>G and T>A return identical cm_splice_501=0.0518. The center-mask scorer also does not distinguish these alleles, confirming that the per-bin lfc divergence found in 14b was a numerical artefact of log2(near-zero) at coding-sequence positions, not a measurable splice effect at the DIFF_LOG2_SUM level.

---

## 15c — Correlation comparison

| Scorer | Spearman rho vs SpliceAI | p | Notes |
|---|---|---|---|
| Gene-mask quantile (original) | 0.287 | 1.2×10⁻²⁵ | **290** unique quantile values (raw column: 87, quantized, multiples of 1/256); 58.4% above 0.95 quantile |
| **CM splice 501** | **0.292** | **1.6×10⁻²⁶** | 994 unique values; continuous |
| CM ATAC 501 (control) | −0.026 | 0.36 (n.s.) | Unchanged from original — modality-specific |

**The center-mask splice scorer marginally improves the correlation with SpliceAI (0.292 vs 0.287).** The improvement is 0.005, well within sampling error. The finding from 14a stands: there is a real but weak correlation between AlphaGenome splice predictions and SpliceAI, and it is modality-specific. The center-mask scorer does not substantially change this picture.

---

## Recovery of high-SpliceAI variants

SpliceAI > 0.5 variants (n=19) CM501 percentile within the 1,278 cohort:

| Metric | Value |
|---|---|
| Median percentile | 97.7th |
| Above 75th pctile | 17/19 (89.5%) |
| Above 90th pctile | 14/19 (73.7%) |
| Above 95th pctile | 13/19 (68.4%) |
| Cohort median CM501 | 0.0092 |

13 of 19 high-confidence SpliceAI variants (SpliceAI > 0.5) have CM501 scores in the top 5% of the cohort. This is better than random (5% expected). The recovery is real but imperfect — 6 of 19 fall below the 95th percentile despite having strong SpliceAI signals.

SpliceAI > 0.2 variants (n=52): median at 95.4th percentile, 27/52 (52%) above 95th.

---

## Codon-pair within-group divergence under CM scorer

| Scorer | Median within-group diff | Max | n > 0.001 |
|---|---|---|---|
| Gene-mask raw | 0.000 | 0.211 | 37/145 |
| **CM splice 501** | **0.000** | **0.231** | **27/145** |
| CM splice 2001 | 0.000 | 0.231 | 32/145 |
| Per-bin max lfc (14b) | 0.410 | 10.490 | 144/145 |

**The center-mask scorer shows the same near-zero within-group divergence as the gene-mask scorer.** Both return identical values for H620Q T>G and T>A (cm_splice_501 = 0.0518 for both). The per-bin lfc divergence of 13.92 found in 14b was a numerical artefact: at coding-sequence positions, the reference splice site usage probability is near zero (not an actual splice site), so log2(alt + 1e-8) − log2(ref + 1e-8) can be arbitrarily large even for tiny absolute changes. DIFF_LOG2_SUM aggregates over the 501-bin window and is dominated by real splice sites, correctly ignoring this numerical noise.

**Implication for 14b:** The conclusion "Explanation B confirmed — AlphaGenome distinguishes T>G from T>A at per-bin level" is revised. The distinction was in log2FC of near-zero values, not in splice signal. Under a score that aggregates window-level splice activity (DIFF_LOG2_SUM), both alleles produce the same prediction. Explanation A holds for both the gene-mask and center-mask scorers: AlphaGenome does not meaningfully distinguish these base changes at the splice-activity level.

---

## H620Q as worked example

| | CM_splice_501 | CM_splice_2001 | Gene-mask_raw | SpliceAI |
|---|---|---|---|---|
| T>G (chr7:117592027) | 0.0518 | 0.0366 | 0.621 | **0.73** |
| T>A (chr7:117592027) | 0.0518 | 0.0366 | 0.621 | **0.00** |

Both AlphaGenome scorers return identical predictions. SpliceAI returns 0.73 vs 0.00. AlphaGenome does not capture the base-specific effect that SpliceAI detects at this position. This is explanation A: the model (or at least its scorer outputs) does not distinguish these base changes at the splice-activity aggregation level.

---

## Priority 7 variants under CM scorer

| Variant | CM_splice_501 | CM_atac_501 | CM_rna_501 |
|---|---|---|---|
| Leu49Pro (L49P) | 0.0021 | 0.0021 | 0.0103 |
| Arg104Gly (R104G) | 0.0259 | 0.0199 | 0.0608 |
| Pro355Leu (P355L) | 0.0003 | 0.0107 | 0.0257 |
| Phe650Leu (F650L) | 0.0032 | 0.0196 | 0.0067 |
| Leu986Pro (L986P) | 0.0092 | 0.0184 | 0.0061 |
| His1054Gln (H1054Q) | 0.0044 | 0.0751 | 0.0209 |
| Arg1097Cys (R1097C) | 0.0046 | 0.0485 | 0.0180 |

The CM scorer values are substantially lower than the gene-mask quantile scores that drove the original 7-variant characterisation. The gene-mask quantile approach (0.99, 0.99, 0.96, 0.96, 0.96, 0.99, 0.97) suggested these variants score above the 95th percentile of common variants (MAF > 0.01 in gnomAD v3); the CM raw scores (0.002–0.076) have no such reference context. The CM ATAC scores for H1054Q (0.075) and R1097C (0.048) remain the highest in the group, consistent with the original ATAC signal.

---

## Distribution of CM_splice_501 scores across 1,278

```
Unique values:  994 of 1,278 (77.8%)
Min:   0.000016
Mean:  0.027
P5:    0.001
P95:   0.083
Max:   1.225
```

The distribution is continuous and right-skewed, consistent with most variants having low local splice activity change and a few having high change. This is a marked improvement over the gene-mask scorer's 87 discrete values.

---

## Conclusion

The center-mask splice scorer (CenterMaskScorer, width=501, DIFF_LOG2_SUM) produces a continuous distribution but does not materially improve the correlation with SpliceAI (rho 0.292 vs 0.287). It does not distinguish synonymous codon variants. The 14b conclusion that AlphaGenome "distinguishes base changes at per-bin level" is retracted — the apparent divergence was a numerical artefact of log2(near-zero). Both explanation A and explanation B were incorrect framings; the correct description is that AlphaGenome's scored outputs (at any supported aggregation) do not distinguish the specific nucleotide in a coding position.

The 14a finding is unaffected: the association between AlphaGenome splice scores and SpliceAI is real (rho≈0.29, p<10⁻²⁵), positive, and modality-specific, but the discordant count does not exceed chance and the concordant count is the signal.
