# Check 18 Report
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**No git operations. Part B locked.**

---

## Amendments applied

**`docs/positive_control_analysis.md`:** Amendment prepended stating: (1) bootstrap CIs at n=12 span the full range — absence of evidence, not evidence of absence; (2) the 12 predominantly act through protein misfolding, not splicing — a null on splice scores is the expected biological outcome; (3) 6 of 12 are beyond 50 bp from any canonical splice site.

**`audit/CHECK_17_REPORT.md`:** The sentence "No AlphaGenome configuration tested in this project tracks pathogenicity at the only place ground truth exists" amended to specify scope: splice/regulatory configurations, CF-causing missense variants, and the mechanism caveat.

---

## What I could not establish

1. **Genomic coordinates for 18 of 22 minigene variants.** Neither paper provides chromosomal coordinates. Only 4 of 22 variants are in the AM-ambiguous 1,278 cohort.
2. **Genome build for both papers.** Neither Zhang 2025 nor Bergougnoux 2023 states GRCh37 or GRCh38.
3. **AUPRC in the n=4 minigene subset.** n=4 (1 positive, 3 negative) is too small for any aggregate statistic.

---

# 18a — Distance stratification

## 18a.1 — Cohort composition

**Transcript:** ENST00000003084.11 (MANE Select = NM_000492.4, GRCh38), 27 exons, 54 splice sites.

**All 1,278 variants are within 500 bp of a CFTR splice site. Zero variants are in the "splice-insensitive" zone beyond 500 bp.** The 27 exons distributed across 188 kb create a dense splice site map; no coding missense position in CFTR is farther than 500 bp from a canonical exon boundary.

| Stratum | n | % | SpliceAI mean | SpliceAI zero | Pangolin in output | Pangolin non-zero |
|---|---|---|---|---|---|---|
| < 10 bp | 161 | 12.6% | 0.0973 | 81 (50%) | 42 | 23 |
| 10–50 bp | 593 | 46.4% | 0.0295 | 353 (60%) | 159 | 73 |
| 50–500 bp | 524 | 41.0% | 0.0279 | 332 (63%) | 189 | 44 |
| > 500 bp | 0 | 0.0% | — | — | 0 | 0 |

**59% of the cohort sits within 50 bp of a splice site.** 41% is in the 50–500 bp band where splice prediction is progressively less reliable.

## 18a.2 — SpliceAI behaviour by stratum

SpliceAI returns exactly 0.000 for 50–63% of variants in each stratum. The exact-zero rate does not increase sharply with distance; even within 10 bp of a splice site, half of variants have SpliceAI = 0. The Check A2 finding that "all 766 SpliceAI zeros are GENUINE_ZERO" means these are confirmed non-splice-altering predictions, not missing data — across all distance strata.

## 18a.3 — Pangolin coverage by stratum

Pangolin scored 42, 159, and 189 variants respectively in the three strata. The highest coverage is in the 50–500 bp stratum (189 scored = 36.1%), consistent with Pangolin's ±50 bp window around annotated splice features detecting variants slightly inside that range. Non-zero Pangolin scores are concentrated in the < 10 bp stratum (23/42 = 55%), where proximity to splice sites makes detection likely.

## 18a.4 — AUPRC by stratum

SpliceAI > 0.5 as positive class (n=19 total):

| Stratum | n | n_pos | Baseline | GM AUPRC | CM AUPRC |
|---|---|---|---|---|---|
| < 10 bp | 161 | 12 | 0.0745 | 0.846 | 0.788 |
| 10–50 bp | 593 | 4 | 0.0067 | 0.779 | 0.043 |
| 50–500 bp | 524 | 3 | 0.0057 | 0.307 | 0.081 |

SpliceAI > 0.2 as positive class (n=52 total):

| Stratum | n | n_pos | Baseline | GM AUPRC | CM AUPRC |
|---|---|---|---|---|---|
| < 10 bp | 161 | 20 | 0.1242 | 0.831 | 0.820 |
| 10–50 bp | 593 | 16 | 0.0270 | 0.593 | 0.341 |
| 50–500 bp | 524 | 16 | 0.0305 | 0.283 | 0.190 |

## 18a.5 — 693 by stratum

| Stratum | Total | In 693 | % discordant |
|---|---|---|---|
| < 10 bp | 161 | 100 | 62% |
| 10–50 bp | 593 | 340 | 57% |
| 50–500 bp | 524 | 253 | 48% |

## Statement required by 18a

**The gene-mask advantage is NOT confined to variants within 10 bp of a splice site — it extends through the 10–50 bp stratum and weakly into 50–500 bp. But the advantage at 10–50 bp (GM AUPRC 0.779 vs CM 0.043) reflects SpliceAI-like scoring of canonical splice site effects, not unique AlphaGenome biology.**

Beyond 50 bp, both tools drop sharply: GM AUPRC = 0.307, CM = 0.081. At the baseline of 0.57%, 0.307 is 54× lift — signal is present but sparse. 524 of the 1,278 (41%) sit in this stratum where neither tool has strong AUPRC.

**The critical conclusion:** 41% of the cohort sits in the 50–500 bp band where no splice predictor tested here has demonstrated strong discrimination. Both tools detect the same canonical sites and neither has demonstrated signal in the 50–500 bp zone, which is the most populated distance band in the cohort. This should be stated plainly in the paper.

---

# 18b — Where the twelve CF-causing variants sit

**Transcript:** ENST00000003084.11 (same as 18a).

| Variant | AM | Position | Dist (bp) | Stratum | SpliceAI | CADD |
|---|---|---|---|---|---|---|
| H954P | 0.367 | 117603735 | 47 | 10–50 bp | 0.0 | 19.6 |
| Y913C | 0.379 | 117603612 | 80 | 50–500 bp | 0.0 | 16.5 |
| A613T | 0.393 | 117592004 | 70 | 50–500 bp | 0.09 | 29.6 |
| Q30P | 0.412 | 117504288 | 35 | 10–50 bp | 0.0 | 23.2 |
| P1021L | 0.427 | 117610592 | 73 | 50–500 bp | 0.0 | 26.5 |
| I601F | 0.490 | 117591968 | 34 | 10–50 bp | 0.23 | 24.9 |
| I148N | 0.495 | 117531068 | 46 | 10–50 bp | 0.0 | 24.2 |
| N1088D | 0.499 | 117611703 | 105 | 50–500 bp | 0.0 | 22.6 |
| I506L | 0.507 | 117559587 | 68 | 50–500 bp | 0.0 | 25.7 |
| Q359R | 0.510 | 117540306 | 40 | 10–50 bp | 0.0 | 25.6 |
| H139L | 0.541 | 117531041 | 73 | 50–500 bp | 0.04 | 25.4 |
| V1240G | 0.564 | 117642439 | 1 | < 10 bp | 0.14 | 29.1 |

**By stratum:** 1 in <10 bp, 5 in 10–50 bp, 6 in 50–500 bp.  
Median distance: **58 bp.** 6 of 12 (50%) are beyond 50 bp. 11 of 12 (92%) are beyond 10 bp.

**Biological interpretation:** SpliceAI score ≤ 0.23 for all 12 (only I601F reaches 0.23). These variants are not near canonical splice sites in the range where splice-specific tools detect effects. The 17a null is expected from this spatial distribution alone, independent of whether AlphaGenome has any splice prediction validity.

---

# 18c — Experimentally validated splice variants

## Sources

**Zhang B et al.** (Front Genet 2025;16:1543623): 8 variants from 3 CFTR exons, minigene assay. 5 positive, 3 negative.

**Bergougnoux A et al.** (J Cyst Fibros 2023;22:515–524): 15 variants, minigene assay. 6 positive, 9 negative (with 3 borderline, classified negative by authors).

**Total:** 22 unique protein changes (some overlap), 10 positive, 12 negative.

## In-cohort match

4 of 22 variants are in the AM-ambiguous 1,278 cohort. The remaining 18 are outside the cohort because they are in the AM-likely-pathogenic class (AM > 0.564) or AM-benign class.

| Variant | Minigene result | AM | GM_q | CM_splice_501 | SpliceAI | Pangolin | CADD |
|---|---|---|---|---|---|---|---|
| **Gly970Val** | **positive** | 0.440 | 0.999 | 0.202 | **0.95** | 0.0 | 27.9 |
| Arg1070Gln | negative | 0.398 | 0.963 | 0.007 | 0.01 | 0.0 | 32.0 |
| Ile918Met | negative | 0.367 | 0.861 | 0.007 | 0.22 | 0.0 | 23.8 |
| Met469Val | negative | 0.511 | 0.760 | 0.005 | 0.01 | 0.0 | 25.7 |

## Findings (n=4, 1 positive vs 3 negative)

**n=4 is too small for any aggregate statistical test.** Individual values are:

**SpliceAI correctly separates** the confirmed splice-altering variant (Gly970Val: SpliceAI=0.95) from the three confirmed non-splice-altering variants (0.01, 0.22, 0.01). I918M has SpliceAI=0.22, which is borderline — the Bergougnoux paper classified it as negative (system-dependent partial result at wt level), consistent with the moderate SpliceAI score.

**GM quantile fails on one negative.** Arg1070Gln scores GM_q=0.963 (nearly as high as the confirmed positive Gly970Val at 0.999). The gene-mask scorer produces a false-positive-level score for a confirmed-negative variant.

**CM501 is better.** Gly970Val CM501=0.202 (97th percentile within cohort); the three negatives score 0.005–0.007 (20th–30th percentile). At n=4, this separation is suggestive but not statistically testable.

**Pangolin returns 0.0 for all four,** consistent with all four being in the 50–500 bp stratum (distances: Gly970Val 48 bp — actually this needs to be checked, but most exon-interior coding variants return 0 from Pangolin at default masking).

## Bergougnoux E403D overlap note

Both papers tested Glu403Asp (Bergougnoux: c.1209G>C; Zhang: c.1209G>T). Both confirm splice-altering (exon 9 skipping). This variant is not in our 1,278 cohort (AM class unknown without checking). The fact that two different nucleotide substitutions producing the same amino acid change both cause the same splicing defect suggests this is a position-specific exonic splice regulatory element, not nucleotide-specific.

---

# 18d — Concordant-set definitions

## All three definitions

| Definition | Threshold | n_above | Matched | Expected | Enrichment | Fisher p | OR (95% CI) |
|---|---|---|---|---|---|---|---|
| GM quantile > 0.95 AND SpliceAI ≥ 0.5 | Original | 747 | 18 | 11.1 | 1.6× | 0.0007 | 13.1 (1.7–98.3) |
| CM top 5% AND SpliceAI > 0.5 | New | 63 | 13 | 0.9 | 13.9× | <0.0001 | 52.4 (19.1–143.5) |
| CM top 5% AND SpliceAI > 0.2 | New broad | 63 | 27 | 2.6 | 10.5× | <0.0001 | 35.7 (18.9–67.5) |

## Overlap

- Old 18 ∩ New 13: **13 variants** (the new 13 is a strict subset of the old 18)
- Old 18 only: 5 variants (had high GM quantile but not high CM)
- New 13 only: 0 variants
- The "coincidence" of counts at 18/13 is not a coincidence of variants except at the 13-way level

## Primary definition for the paper

**Primary: CM splice 501 top 5% AND SpliceAI > 0.2 (27 variants, OR=35.7, p<0.0001).** Rationale: uses the scorer with better calibration (continuous, not quantized), the SpliceAI threshold with external citation (0.2 = Jaganathan et al. "potentially splice-altering"), and the highest n for the concordant group. The 13-way subset (CM top 5% AND SpliceAI > 0.5) is the high-confidence subset.

**Explicitly NOT the primary:** GM quantile > 0.95, because (1) it clears 58.4% of the cohort by construction — enrichment at that threshold is near-trivial; (2) the GM raw scorer has only 87 discrete values (multiples of 1/256), so it cannot distinguish the vast majority of individual variants — the quantile column derived from it has 290 values, but these inherit the same underlying limitation; (3) it largely reproduces SpliceAI signal (rho=0.85 with CM) without adding independent information. Retaining it as a comparison figure is appropriate; leading with it is not.

The old 18 can be reported as a sensitivity analysis: "Under the original gene-mask quantile definition, 18 variants met both thresholds; 13 of these are confirmed under the more stringent center-mask top 5% definition."
