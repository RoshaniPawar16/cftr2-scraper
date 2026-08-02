# Positive Control Analysis: 12 CFTR2-confirmed CF-causing Variants in the AM-ambiguous Set
**Date:** 2026-08-01 (amended 2026-08-02, Check 18)  
**Context:** Of the 1,278 AM-ambiguous CFTR variants scored by AlphaGenome, 12 are classified as CF-causing by CFTR2. AlphaMissense assigned them ambiguous scores (0.34–0.564), placing them in the Phase 2 cohort despite known pathogenicity. They are the only variants in the 1,278 with a confirmed disease label.

**Amendment (Check 18):** The null result in Check 17a must not be interpreted as "no AlphaGenome configuration tracks pathogenicity." Two limitations apply. First, the test was underpowered: bootstrap CIs spanned [−0.92, +0.72], the full range of the rank-biserial. A null at n=12 is absence of evidence, not evidence of absence. Second, and more important: these 12 CF-causing missense variants predominantly act through protein misfolding, trafficking failure, or gating defects — **not through splicing**. Testing whether splice scores separate variants that are pathogenic by non-splicing mechanisms is the wrong experiment, and a null is the expected outcome. Check 18b documents that 6 of the 12 are beyond 50 bp from any canonical CFTR splice site, and all 12 have SpliceAI ≤ 0.23. The correct positive control for splice scoring is experimental minigene data (see Check 18c). The conclusion retracted is: "no AlphaGenome configuration tested tracks pathogenicity." The correct statement is: "no AlphaGenome splice or regulatory configuration tested separates CF-causing missense variants from the AM-ambiguous background — a null expected given the mechanism of most CF-causing missense variants."

---

## The 12 variants

| Variant | AM score | RNA q | ATAC q | SPLICE q | CADD | SpliceAI |
|---|---|---|---|---|---|---|
| H954P | 0.367 | 0.964 | 0.985 | 0.992 | 19.6 | 0.000 |
| Y913C | 0.379 | 0.975 | 0.748 | 0.993 | 16.5 | 0.000 |
| A613T | 0.393 | 0.975 | 0.768 | 0.998 | 29.6 | 0.090 |
| Q30P | 0.412 | 0.996 | 0.035 | 0.725 | 23.2 | 0.000 |
| P1021L | 0.427 | 0.987 | 0.302 | 0.904 | 26.5 | 0.000 |
| I601F | 0.490 | 0.993 | 0.058 | 1.000 | 24.9 | 0.230 |
| I148N | 0.495 | 0.951 | 0.711 | 0.985 | 24.2 | 0.000 |
| N1088D | 0.499 | 0.903 | 0.205 | 0.866 | 22.6 | 0.000 |
| I506L | 0.507 | 0.943 | 0.393 | 0.677 | 25.7 | 0.010 |
| Q359R | 0.510 | 0.927 | 0.711 | 0.949 | 25.6 | 0.000 |
| H139L | 0.541 | 0.981 | 0.877 | 0.996 | 25.4 | 0.040 |
| V1240G | 0.564 | 0.999 | 0.249 | 0.996 | 29.1 | 0.140 |

---

## AlphaGenome quantile comparison: 12 CF-causing vs 1,266 remaining

Mann-Whitney U test (two-sided). n=12 gives approximately 20% power to detect a medium-large effect (d≈0.8) at α=0.05. This is an exploratory analysis; results should not be interpreted as confirming or excluding real differences.

| Metric | Median (n=12) | Median (n=1266) | U | p | rank-biserial r |
|---|---|---|---|---|---|
| RNA quantile | 0.9748 | 0.9804 | 6421 | 0.356 | 0.155 |
| ATAC quantile | 0.5517 | 0.6682 | 5996 | 0.209 | 0.211 |
| SPLICE quantile | 0.9884 | 0.9565 | 8518 | 0.469 | −0.121 |
| CADD PHRED | 25.15 | 24.90 | 7620 | 0.985 | −0.003 |
| SpliceAI delta | 0.000 | 0.000 | 8062 | 0.680 | −0.061 |

**No metric shows a statistically significant difference.** The ATAC quantile shows the largest non-significant effect (r=0.211, p=0.209), with the 12 CF-causing variants having slightly lower ATAC signal than the remaining 1,266. The splice quantile is marginally higher in the 12, but the effect is small and non-significant. Given n=12, absence of significance does not imply absence of effect; the test is severely underpowered.

---

## Group membership

| Group | Observed in 12 | Expected under null | Notes |
|---|---|---|---|
| 693 discordant (AG high SPLICE, SpliceAI low) | 6 (50%) | 5.5 (54.2%) | At null rate |
| 18 multi-tool confirmed (AG + SpliceAI both high) | 0 (0%) | 0.17 (1.4%) | One fewer than expected, not meaningful at n=12 |
| 58 rescue (AG high, CADD<20, SpliceAI<0.2) | 2 (16%) | 0.54 (4.5%) | H954P and Y913C; 3.5× over-represented |

The rescue group over-representation (2 observed vs 0.54 expected) is notable: H954P and Y913C both have CADD < 20 and SpliceAI = 0.0, so AlphaGenome is the only tool flagging them. However, n=2 is too small for any inferential claim. These two variants warrant individual inspection rather than a statistical conclusion.

---

## SpliceAI and CADD: like-for-like

The 12 CF-causing variants have SpliceAI = 0 for 9 of 12 (75%), versus 60% (766/1278) across the full 1278. CADD median 25.2 versus 24.9 — negligible difference, well within rounding.

---

## Implications for the paper

**Result direction:** Negative. AlphaGenome quantiles are not elevated in the 12 CF-causing variants relative to the 1,266 remaining variants. Discordance between AlphaGenome and SpliceAI is equally common in these known-pathogenic variants (50%) as in the full cohort (54.2%). The rescue group shows a slight excess (2/12 vs 0.54 expected) but not at any conventional threshold.

**What this means:** AlphaGenome's signals — high splice quantile, high ATAC quantile — are not specifically elevated in variants with confirmed CFTR2 pathogenicity labels. This is consistent with two interpretations that cannot be distinguished at n=12: (1) AlphaGenome is capturing real biology that is not protein-function-mediated, uniformly distributed across sequence space; or (2) AlphaGenome's high splice/regulatory signals reflect features of the CFTR locus rather than variant-specific effects.

**What this does not mean:** It does not mean AlphaGenome is wrong. The 12 CF-causing variants are in the AM-ambiguous band precisely because AlphaMissense failed on them. If they were in the AM-pathogenic band they would not be in the Phase 2 cohort. The analysis tests whether AlphaGenome provides additional signal beyond AM for these cases; it does not test AlphaGenome's general validity.

**Mandatory disclosures:**
- n=12 is small. This is not a formally powered test.
- These are the only ground-truth-labelled variants in the Phase 2 cohort.
- H954P and Y913C (the rescue members) are CF-causing variants flagged only by AlphaGenome, which is a potential validation signal that warrants individual review and, if taken forward, functional follow-up.
- Results should be reported regardless of direction. The absence of enrichment in the discordant group (6 of 12 at null rate) is a finding, not a null.

---

*Data source: `results/comparator_analysis.csv`, `results/rescue_analysis.csv`, `data/cftr2_results.csv`*  
*Statistical method: Mann-Whitney U (two-sided), rank-biserial r as effect size*  
*Generated: Part A6 integrity audit, 2026-08-01*
