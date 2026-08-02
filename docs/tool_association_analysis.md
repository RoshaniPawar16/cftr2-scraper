# Tool Association Analysis: AlphaGenome Splice Quantile vs SpliceAI
**Date:** 2026-08-02  
**Branch:** integrity-audit-2026-07  
**n = 1,278 AM-ambiguous CFTR variants**

---

## Result

**The discordant count (698, reported in the paper as 693 at a slightly different threshold) does not exceed chance.** Under independence, 716.6 variants are expected to have high AG quantile and low SpliceAI. The observed count is 698. The discordance is 18.6 below the independence expectation.

**The concordant count (49 variants with both AG > 0.95 and SpliceAI > 0.2) significantly exceeds the independence expectation of 30.4.** The association is driven by concordance, not discordance.

The paper's framing — that the 693 discordant variants represent a signal requiring explanation — is incorrect. The 693 is the expected background noise; the 49 concordant variants are the signal.

---

## 2×2 contingency tables

### SpliceAI threshold > 0.2

|  | SpliceAI > 0.2 | SpliceAI ≤ 0.2 | Row total |
|---|---|---|---|
| **AG splice > 0.95** | 49 (exp 30.4) | **698 (exp 716.6)** | 747 |
| **AG splice ≤ 0.95** | 3 (exp 21.6) | 528 (exp 509.4) | 531 |
| **Column total** | 52 | 1,226 | 1,278 |

χ² = 28.57, df=1, p < 0.0001  
OR = 12.36 (95% CI 3.83–39.86)  
Fisher exact p < 0.0001

**Discordant cell (AG high, SpliceAI low): observed 698, expected 716.6, difference −18.6. The discordance is at or below chance.**

**Concordant cell (both high): observed 49, expected 30.4, +61% above chance.** This is where the significant association lies.

The overall chi-square is significant (p < 0.0001), but it is driven by the concordant cell and the AG-low/SpliceAI-high cell (3 observed vs 21.6 expected — a strong deficit). The discordant cell is not the source of the association.

### SpliceAI threshold > 0.5

|  | SpliceAI > 0.5 | SpliceAI ≤ 0.5 | Row total |
|---|---|---|---|
| **AG splice > 0.95** | 18 (exp 11.1) | 729 (exp 735.9) | 747 |
| **AG splice ≤ 0.95** | 1 (exp 7.9) | 530 (exp 523.1) | 531 |
| **Column total** | 19 | 1,259 | 1,278 |

χ² = 10.46, df=1, p = 0.0012  
OR = 13.09 (95% CI 1.74–98.34)  
Fisher exact p = 0.0007

The association is consistent at the stricter threshold.

---

## Continuous relationship: Spearman correlation

| Predictor | SpliceAI delta (rho) | p |
|---|---|---|
| **AG splice quantile** | **0.2869** | **1.2 × 10⁻²⁵** |
| AG ATAC quantile | −0.0255 | 0.36 (n.s.) |
| AG RNA quantile | 0.0556 | 0.047 (marginal) |

The AG splice quantile has a real, statistically significant positive correlation with SpliceAI delta (rho = 0.287, p = 1.2×10⁻²⁵). The ATAC quantile has no correlation with SpliceAI (rho = −0.026, p = 0.36), confirming this is modality-specific rather than generic.

The correlation is positive and modality-specific: AlphaGenome's splice quantile tracks SpliceAI in the same direction. The tools agree more than they disagree, in the continuous sense.

---

## Recovery statistic: high-confidence SpliceAI variants

Of the 19 variants with SpliceAI > 0.5:
- **18 (94.7%) have AG splice quantile > 0.95**
- Base rate of AG > 0.95 across all 1,278: 58.4%
- Expected under independence: 19 × 0.584 = 11.1
- Fisher exact: OR = 13.09 (95% CI 1.74–98.34), p = 0.0007

The 18 multi-tool concordant variants are not explained by the base rate. They are significantly enriched.

---

## Summary

| Result | Observed | Expected (indep.) | Significant? |
|---|---|---|---|
| Discordant (AG hi, SpliceAI lo, >0.2) | 698 | 716.6 | **NO** (below expectation) |
| Concordant both hi (>0.2) | 49 | 30.4 | **YES** p<0.0001 |
| Concordant both hi (>0.5) | 18 | 11.1 | **YES** p=0.0007 |
| Spearman rho (continuous) | 0.287 | — | **YES** p=1.2×10⁻²⁵ |
| ATAC control rho | −0.026 | — | NO (p=0.36) |

**The association between AlphaGenome splice quantile and SpliceAI is real, positive, and modality-specific.** The tools are correlated, not discordant. The 693/698 "discordant" count is noise below the independence expectation. The meaningful finding is the 18 variants flagged by both tools at high confidence.

---

## Implication for the paper

The paper currently presents 693 as the headline discordant count, implying AlphaGenome and SpliceAI capture different signals. That framing is wrong:

1. 693 is below the independence expectation — it is not a signal of discordance, it is the baseline of a right-skewed binary distribution (most variants are below SpliceAI 0.2).
2. The signal in the data is concordance: 49 and 18 variants where both tools agree at above-chance rates.
3. The Spearman correlation (0.287) confirms a continuous positive association.

**The paper should be reframed around the 18 multi-tool confirmed variants**, not the 693 discordant ones. The correct claim is: "18 variants are flagged by both AlphaGenome (splice quantile > 0.95) and SpliceAI (delta > 0.5), significantly more than expected by chance (OR 13.1, p = 0.0007). An additional 693 are flagged by AlphaGenome alone; this count does not exceed chance under independence."
