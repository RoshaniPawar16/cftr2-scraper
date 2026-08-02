# SpliceAI Coverage Analysis
**Date:** 2026-07-30  
**Source:** `results/spliceai_zero_reclassification.csv`  
**Method:** Re-query of Ensembl VEP REST API (SpliceAI plugin) for all 766 variants with `SpliceAI_max_delta == 0.0` in `results/comparator_analysis.csv`

---

## Background

`fix_spliceai_scores.py` initialises `best_max = -1.0` for each variant and sets `SpliceAI_max_delta = 0.0` in two distinct situations:

1. VEP returns a response containing a SpliceAI record with all four components (DS_AG, DS_AL, DS_DG, DS_DL) equal to 0.000 — a **confirmed prediction of no splice effect**
2. VEP returns a response but no transcript consequence contains a `spliceai` key — **no SpliceAI prediction available** for this variant

(Script reference: `scripts/fix_spliceai_scores.py:87-100`)

```python
best_sa, best_max = {}, -1.0         # line 87: initialised to -1.0
for tc in entry.get('transcript_consequences', []):
    if 'spliceai' in tc:             # line 89: only updates if spliceai key present
        ...
        if ds_max > best_max:
            best_max, best_sa = ds_max, sa
results[idx] = {
    ...
    'SpliceAI_max_delta': best_max if best_max >= 0 else 0.0,   # line 100: substitutes 0.0
}
```

Both conditions produce `0.0` in the output. The 766 variants with `SpliceAI_max_delta == 0.0` could belong to either case, making it impossible to determine from the original data alone whether `0.0` means "confirmed zero" or "no prediction returned."

---

## Re-query results

All 766 variants were re-queried against Ensembl VEP with the SpliceAI plugin enabled (batch size 200, 2026-07-30).

| Classification | Count |
|---|---|
| GENUINE_ZERO | 766 |
| NO_SPLICEAI_RECORD | 0 |
| VEP_ERROR | 0 |
| VARIANT_NOT_FOUND | 0 |

**All 766 variants are GENUINE_ZERO.** Every variant's VEP response contained a SpliceAI record with all four delta scores (DS_AG, DS_AL, DS_DG, DS_DL) confirmed as 0.000. No variant fell into the "no SpliceAI record" category.

---

## Implication for the 693-discordant figure

Of the 693 discordant variants (AlphaGenome SPLICE quantile > 0.95 AND SpliceAI delta < 0.2):

| SpliceAI status | Count |
|---|---|
| SpliceAI = 0.0 (GENUINE_ZERO, confirmed by re-query) | 397 |
| SpliceAI > 0.0 and < 0.2 (non-zero, below threshold) | 296 |
| **Total discordant** | **693** |

**Both figures support the same conclusion.** The 397 variants with SpliceAI = 0.0 received a confirmed prediction of no splice effect, not a coverage failure. The 296 with non-zero sub-threshold SpliceAI received a positive prediction below the 0.2 significance threshold. SpliceAI made a prediction for every one of the 693 discordant variants; none are excluded from analysis due to missing data.

---

## As-published versus genuine-zero-only recomputation

| Group | As-published (missing treated as < 0.2) | Genuine-zero-only (missing excluded) |
|---|---|---|
| Discordant (AG SPLICE > 0.95 AND SpliceAI < 0.2) | **693** | **693** |
| Multi-tool confirmed (AG SPLICE > 0.95 AND SpliceAI > 0.5) | 18 | 18 |
| AlphaGenome rescue (AG ATAC or SPLICE > 0.95 AND CADD < 20 AND SpliceAI < 0.2) | 58 | 58 |

The two computations are identical. Because there are no `NO_SPLICEAI_RECORD` cases, the "missing treated as < 0.2" and "genuine-zero-only" groups are the same set.

---

## What the coverage finding supports — and what it does not

**The SpliceAI coverage finding stands.** All 766 variants with `SpliceAI_max_delta == 0.0` are GENUINE_ZERO: VEP returned a SpliceAI record with all four delta scores confirmed as 0.000. No variant in the 693 discordant group has a missing SpliceAI prediction. The comparison is complete; the 693 count is not a coverage artefact.

**The 693 discordant figure is retracted as a finding.** Under the independence model, 717 variants are expected to satisfy (SPLICE quantile > 0.95 AND SpliceAI < 0.2) given the marginal distributions. Observed is 693. The discordant group sits below the independence expectation (χ² p = 0.20); it is not evidence that AlphaGenome and SpliceAI capture different signals. Additionally, the 0.95 threshold clears 58.4% of the cohort because it compares rare coding variants against a common-variant background — the discordant count is the expected consequence of that background mismatch, not a result.

The coverage re-query (this document) confirms the 693 is a clean count with no missing data. A separate audit check (Check 12, `audit/checks/CHECK_12_13_REPORT.md`) establishes that the count is at chance. Both findings are needed to describe what the 693 is and is not.

---

*Re-query script: `scripts/reclassify_spliceai_zeros.py`*  
*Raw results: `results/spliceai_zero_reclassification.csv`*  
*Blocker 1 of audit/AUDIT_REPORT.md Part A2*
