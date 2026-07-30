# Integrity Audit Report
**Repository:** github.com/RoshaniPawar16/alphamissense-cftr  
**Branch:** integrity-audit-2026-07  
**Date:** 2026-07-29  
**Auditor:** Claude Code (Sonnet 4.6)

---

## 1. Claim counts by status

| Status | Count |
|---|---|
| VERIFIED | 35 |
| VERIFIED_ROUNDED | 17 |
| CONTRADICTED | 1 |
| NO_EVIDENCE | 1 |
| NOT_CHECKABLE | 1 |
| **Total claims** | **55** |

---

## 2. CONTRADICTED claims

### C64 — `notebooks/alphamissense.ipynb` cell 20 stored output vs committed data

**Documented value (all docs):** 72 CFTR2 variants of varying clinical consequence; of those, 41 likely_pathogenic / 19 ambiguous / 12 likely_benign.

**Stored notebook output (cell 20):** "Total varying clinical consequence: 82 / likely_pathogenic: 50 / ambiguous: 19 / likely_benign: 13."

**Evidence for correct value:** `data/cftr2_results.csv` (72 rows with `determination_2026='Varying clinical consequence'`); `data/varying_consequence_am.csv` (72 rows, 41 LP). Query: `cftr2_results.csv` → `Counter(determination_2026)` → `'Varying clinical consequence': 72`. The documentation and CSV files are mutually consistent at 72 / 41.

**Root cause:** The notebook was run at some point against data that contained 82 VCC variants. The data was subsequently updated (or filtered) and the committed `cftr2_results.csv` has 72. Cell 20's stored output was not re-run after the data change. The notebook is confirmed out-of-sequence (cell 48, the last cell, has execution_count=2 — a different kernel session from the rest of the notebook).

**Impact:** The 72 / 41 numbers are in the paper abstract, results table, and domain analysis. Those numbers are supported by the committed CSV files. The notebook is not the primary evidence for these figures; the CSV files are. The paper can proceed with 72 / 41. However, the notebook must be re-run cleanly before submission to ensure all stored outputs reflect the committed data.

---

## 3. NO_EVIDENCE claims

### C41 — Average Precision 0.990 attributed to the 292-variant validation (`docs/REPORT.md:96`)

`docs/REPORT.md` section 3.2 presents a table labelled "292 variants" that includes "Average Precision | 0.990". The `alphamissense.ipynb` cell 9 computes AUC = 0.946 on 292 variants but does not compute AP. The AP value 0.990 is stored only in `comparison.ipynb` cell 15, where it is computed on 286 variants (the subset with all four predictor scores).

The value 0.990 is real and verified for the 286-variant set. It is not independently computed in any stored artifact for the 292-variant set. The claim in REPORT.md section 3.2 that AP was computed on 292 variants has no evidential support in the committed notebooks. This appears to be a copy of the benchmarking-set AP into the validation-set table.

**Impact on paper:** Either (a) the alphamissense.ipynb should be extended to compute AP on 292 variants and the value confirmed, or (b) the REPORT.md table should clarify that AP comes from the 286-variant benchmarking set. If AP differs between 292 and 286 variants, the paper has a numeric error.

---

## 4. Fabrication findings

None. No hardcoded headline figures found in scripts. No synthetic or randomly-generated data found. See SYNTHETIC_SWEEP.md for full sweep details.

The one methodology concern flagged (F04 in SYNTHETIC_SWEEP.md) is that `fix_spliceai_scores.py` writes `0.0` for variants where Ensembl VEP returned a response but no SpliceAI transcript annotation. This makes "confirmed zero splice effect" and "no SpliceAI data available" indistinguishable in the output. This is not fabrication, but it must be disclosed in the paper's methods section.

---

## 5. Headline number survival

| Claim | Documented | Recomputed | Status |
|---|---|---|---|
| AlphaMissense AUC | 0.946 | 0.946 | VERIFIED |
| AlphaMissense AP (286 variants, comparison set) | 0.990 | 0.990 | VERIFIED |
| AlphaMissense AP (292 variants, validation — REPORT.md 3.2) | 0.990 | not stored | NO_EVIDENCE |
| Labelled set is n=292 (not ≈292) | 292 | 292 | VERIFIED |
| CADD AUC | 0.776 | 0.776 | VERIFIED |
| PolyPhen AUC | 0.826 | 0.826 | VERIFIED |
| SIFT AUC | 0.678 | 0.678 | VERIFIED |
| Ensemble AUC | 0.927 | 0.927 | VERIFIED |
| Feature weights (+1.907, +0.279, -0.117) | three values | three values exact | VERIFIED |
| DeLong p-values (0.0040, 0.0011, <0.0001) | three values | three values exact | VERIFIED |
| 1,278 ambiguous variants with real returned values | 1,278 | 1,278 (0 missing) | VERIFIED |
| 693 discordant (AG splice > 0.95 AND SpliceAI < 0.2) | 693 | 693 | VERIFIED |
| 18 multi-tool confirmed | 18 | 18 | VERIFIED |
| 58 AlphaGenome rescue | 58 | 58 | VERIFIED |
| 73% MSD1/MSD2, R-domain = 0 | 73% / 0 | 73.2% / 0 | VERIFIED / VERIFIED |
| CADD mean PHRED 24.5 | 24.5 | 24.496 | VERIFIED_ROUNDED |
| SpliceAI > 0.2: 52; > 0.5: 19 | 52 / 19 | 52 / 19 | VERIFIED |

**On the 693 number specifically:** The count recomputes exactly from committed data. There are **zero missing SpliceAI values** in `comparator_analysis.csv`. However, `fix_spliceai_scores.py` substitutes `0.0` for variants where VEP returned no SpliceAI annotation. Of the 1,278 variants, 766 have `SpliceAI_max_delta = 0.0`. An unknown fraction of those 766 may represent "no data returned" rather than "confirmed zero." The 693 discordant count is numerically correct, but the paper should disclose that SpliceAI 0.0 values conflate "confirmed no splice effect" and "no SpliceAI record available from VEP."

---

## 6. Documentation requiring revision

1. **`docs/REPORT.md` section 3.2:** The validation table lists "Average Precision | 0.990" alongside "Variants | 292." No stored computation supports AP for the 292-variant validation. Either compute and verify it, or clarify the table refers to the 286-variant benchmarking set.

2. **`docs/REPORT.md` section 3.3 and throughout / `README.md`:** The comparator table shows "AlphaMissense | 0.946 | 0.990" as if the AP were independently computed on the benchmarking set. This is correct — it is the 286-variant AP. But it conflicts with the same value appearing in the 292-variant validation table. The two tables should clearly specify their respective n.

3. **`docs/comparator_analysis_report.md` section 4.3 (and paper methods):** The SpliceAI < 0.2 threshold used to define the discordant group must disclose that 0.0 values in the data conflate genuine zeros and VEP no-return cases. The exact number of variants with no SpliceAI record vs genuine 0.0 is not recoverable from committed artifacts.

4. **No document discloses the orphan status of `alphagenome_rescue_variants.csv`.** The batch report cites it as a source file but no generating script is committed. Before submission, either commit the generating code or note in methods that the file was produced by an ad-hoc analysis not versioned in the repository.

---

## 7. Repository state judgement

The headline numbers that will go into a paper are, with two exceptions, verified or verified-rounded against committed CSV data. The computation pipeline from raw inputs to those numbers is traceable via committed scripts. No fabricated data was found.

The two exceptions matter:

The **AP 0.990 in the 292-variant validation** (REPORT.md section 3.2) lacks a stored computation. The value is likely correct — AlphaMissense's AP on 286 vs 292 variants is probably identical to three decimal places — but it is currently an unchecked assumption. A one-cell addition to `alphamissense.ipynb` would resolve this.

The **stale notebook cell 20** (82 vs 72 VCC variants) is more significant. `alphamissense.ipynb` contains at least one stored output that pre-dates the committed data. Both notebooks used for the primary analysis (`alphamissense.ipynb` and `comparison.ipynb`) are out-of-sequence, meaning their stored outputs cannot be trusted as a coherent record of a single clean run. The CSV files and scripts are the repository's ground truth; the notebooks are not currently in a state where they can serve as a reproducibility record.

**Conclusion (Part A, superseded by Part A2 below):** A draft could be written from this repository, citing the CSV files and scripts rather than the notebook outputs. The paper would need to be honest about the SpliceAI 0.0 ambiguity and the AP evidence gap. Before submission, both primary notebooks should be cleared of stored outputs and re-run end-to-end against the committed data files, and the generating code for `alphagenome_rescue_variants.csv` should be committed.

---

## Part A2 — Blocker Resolution
**Date:** 2026-07-30

### Revised claim counts

| Status | Part A | Part A2 | Change |
|---|---|---|---|
| VERIFIED | 35 | 15 | −20 |
| VERIFIED_ROUNDED | 17 | 16 | −1 |
| CONTRADICTED | 1 | 1 | — |
| NO_EVIDENCE | 1 | 1 | — |
| NOT_CHECKABLE | 1 | 22 | +21 |
| **Total** | **55** | **55** | — |

21 claims moved to NOT_CHECKABLE: 20 from VERIFIED (C03–C07, C10–C14, C17–C20, C36–C39, C42–C43) and 1 from VERIFIED_ROUNDED (C44). All 21 are from `alphamissense.ipynb` (out-of-sequence) or `comparison.ipynb` (out-of-sequence); their only committed evidence is stored outputs from notebooks that cannot be trusted as complete coherent runs.

---

### Blocker 1 — SpliceAI 0.0 conflation: RESOLVED

**Code path producing 0.0** (`scripts/fix_spliceai_scores.py:87–100`):

```python
best_sa, best_max = {}, -1.0                          # line 87: initialised for each entry
for tc in entry.get('transcript_consequences', []):
    if 'spliceai' in tc:                              # line 89: only updates if key present
        sa = tc['spliceai']
        ds_max = max(float(sa.get(k, 0) or 0) for k in ['DS_AG','DS_AL','DS_DG','DS_DL'])
        if ds_max > best_max:
            best_max, best_sa = ds_max, sa
results[idx] = {
    ...
    'SpliceAI_max_delta': best_max if best_max >= 0 else 0.0,  # line 100: substitutes 0.0
}
```

Two conditions reach the substitution: (a) SpliceAI record present with max component = 0.000, or (b) no `spliceai` key in any transcript consequence. Both produce `0.0` in the output.

**Re-query:** Ensembl VEP with SpliceAI plugin was queried for all 766 variants with `SpliceAI_max_delta == 0.0`. 4 batches of 200/200/200/166, 2026-07-30. Results: `results/spliceai_zero_reclassification.csv`.

**Result: ALL 766 ARE GENUINE_ZERO.** Every variant's VEP response contained a SpliceAI record with all four delta components confirmed 0.000. Zero cases of NO_SPLICEAI_RECORD, VEP_ERROR, or VARIANT_NOT_FOUND.

**Crosstab for the 693 discordant:**
- 397 variants: SpliceAI = 0.0 → confirmed GENUINE_ZERO
- 296 variants: SpliceAI > 0.0 and < 0.2 → confirmed non-zero (already in original data)
- Total: 693

**Both figures (as-published and genuine-zero-only) are 693.** The SpliceAI concern is resolved. The framing "SpliceAI does not flag these variants" is available for all 693: SpliceAI returned a positive prediction of no splice effect (not a coverage failure) for every variant in the discordant group. See `docs/spliceai_coverage_analysis.md`.

---

### Blocker 2 — 292 vs 286 cohort mismatch and DeLong validity

**The six excluded variants: identities NOT recoverable from committed artifacts.**

`comparison.ipynb` cell 8 (ec=8) fetches CADD scores via the CADD REST API in-memory and records "CADD scored: 286 / 292." The 6 variants that returned `None` from the API are not identified anywhere — `cftr2_results_annotated.csv` has no CADD column (`scripts` check: no script writes CADD scores to this file). The 6 missing variants cannot be named from committed artifacts.

**n for every reported AUC:**

| Predictor | n | Source | Evidence kind |
|---|---|---|---|
| AlphaMissense | 286 | comparison.ipynb cell 9 output (ec=9, main session) | NOTEBOOK_STORED_OUTPUT |
| CADD | 286 | comparison.ipynb cell 9 output (ec=9, same session) | NOTEBOOK_STORED_OUTPUT |
| PolyPhen | 286 | comparison.ipynb cell 12 output (ec=16, same session) | NOTEBOOK_STORED_OUTPUT |
| SIFT | 286 | comparison.ipynb cell 12 output (ec=16, same session) | NOTEBOOK_STORED_OUTPUT |
| Ensemble (all predictors) | 286 | ensemble.ipynb cell 9 output (ec=?, SEQUENTIAL) | NOTEBOOK_STORED_OUTPUT |

All four benchmarking AUCs were computed in the same main kernel session (ec=2 through ec=17 in comparison.ipynb), on the same n=286. The benchmarking cohort is internally paired. **If the DeLong test were computed in that same session on n=286, the pairing requirement would be met.**

**DeLong cohort: NOT CONFIRMABLE from committed artifacts.**

Cell 16 (ec=2) is in a separate kernel session. Its source re-reads `cftr2_results_annotated.csv`, re-parses SIFT/PolyPhen from the VCF, and re-fetches CADD from the API. The stored output shows the CADD progress counter ("20/292 done" through "280/292 done") but records no "CADD scored: X/292" line. The AUC values in the DeLong output (0.946/0.826/0.776/0.678) exactly match the benchmarking session values — consistent with n=286 — but this inference cannot be confirmed from the stored outputs alone. If the CADD API returned a different 6 failures in the DeLong session, the DeLong test used a different 286 variants than the benchmarking table, which would invalidate the pairing.

**DeLong implementation is incorrect.**

The code in cell 16 computes:

```python
se = np.sqrt(v10_a + v01_a + v10_b + v01_b)
```

The DeLong (1988) test for two **correlated** ROC curves — two predictors measured on the same sample — requires:

```
SE = sqrt(Var(AUC_A) + Var(AUC_B) - 2 * Cov(AUC_A, AUC_B))
```

The covariance term `2 * Cov(AUC_A, AUC_B)` is omitted. Because the predictors are positively correlated on the same sample, `Cov > 0`, so the code's SE is **overestimated**, Z is **underestimated**, and the stated p-values are **inflated** (conservative). The true p-values are smaller than stated, meaning the significance conclusions (AM outperforms all at p < 0.01) hold directionally. However, the specific Z statistics and p-values published in the paper are incorrect as DeLong test results — they come from an implementation that treats the two AUC estimates as independent when they are not.

**Status of DeLong claims:** C42, C43, C44 move to NOT_CHECKABLE. The comparison.ipynb is OOS (first reason), the DeLong n for that session is unconfirmable (second reason), and the implementation omits the covariance term required by the cited method (third reason). All three reasons are independent.

**Implication:** The stated Z and p-values (2.88/0.0040, 3.28/0.0011, 5.87/<0.0001) cannot appear in the paper citing DeLong 1988. A correct implementation must be run and its output committed before submission. The qualitative conclusion (AM outperforms all baselines) is directionally supported, but the test values are wrong.

---

### Blocker 3 — out-of-sequence notebook execution audit

**All notebooks audited for execution-count ordering:**

| Notebook | Cells | Executed | Sequential | Out-of-sequence gaps |
|---|---|---|---|---|
| alphamissense.ipynb | 50 | 36 | **NO** | ec skips at cells 22→23, 29→30, 30→31, 39→40, 40→42; cell 48 (last) has ec=2 (separate session) |
| comparison.ipynb | 18 | 12 | **NO** | ec jumps from cell 6 (ec=5) to cell 7 (ec=7); cell 10 (ec=10) to cell 11 (ec=15); cell 15 (ec=17) to cell 16 (ec=2: separate session) |
| cftr2_scraper.ipynb | 17 | 14 | **NO** | cell 4 (ec=35) to cell 8 (ec=17): backward jump; cell 8 (ec=17) to cell 9 (ec=36) |
| alphagenome_cftr.ipynb | 26 | 12 | Yes | — |
| ensemble.ipynb | 17 | 9 | Yes | — |

Three of five notebooks are out-of-sequence. `cftr2_scraper.ipynb` was not previously reported as OOS. Its OOS status does not affect any claim in the current ledger (no claim references it), but the backward execution counter at cell 4 (ec=35 to ec=17) indicates substantial re-running in non-linear order.

**Claims reclassified by evidence_kind rule:**

Rule: any claim whose sole evidence is `NOTEBOOK_STORED_OUTPUT` from an OOS notebook drops from VERIFIED (or VERIFIED_ROUNDED) to NOT_CHECKABLE.

Claims that stay VERIFIED despite being from OOS notebook outputs: C08 (n=292) and C09 (253/39 split) both have independent RESULTS_CSV confirmation from `data/cftr2_results_annotated.csv`. They retain VERIFIED status.

Claims that stay VERIFIED from SEQUENTIAL notebooks: C15 (Ensemble AUC 0.927/AP 0.983) and C16 (feature weights +1.907/+0.279/−0.117) are from `ensemble.ipynb`, which is sequential. They retain VERIFIED status.

Total claims moving to NOT_CHECKABLE from OOS notebook rule: **21** (C03–C07 from alphamissense.ipynb; C10–C14 from comparison.ipynb; C17–C20 from alphamissense.ipynb; C36–C39 from alphamissense.ipynb; C42–C44 from comparison.ipynb). C40 was already NOT_CHECKABLE.

**Additional finding during Blocker 3 investigation:** `data/flagged_unclassified.csv` has 546 rows, not 705 as documented in README.md line 170. The notebook (alphamissense.ipynb cell 11 stored output) clarifies: "After dedup: 546 unique likely_pathogenic variants." The 705 is the pre-deduplication count; the 546 is the post-dedup file. The README description of this file ("705 unclassified variants") conflates the two counts. This does not affect any CSV-backed claim, but C19 (705 LP) — already NOT_CHECKABLE — has an additional data inconsistency: the closest supporting file has 546 rows, not 705.

---

### Blocker 4 — the unreported NOT_CHECKABLE (Part A omission)

The single NOT_CHECKABLE claim from Part A was **C40**:

> **Claim text:** "AlphaMissense achieves AUC 0.946 and MCC 0.689 on 292 labelled CFTR variants."  
> **Source file and line:** `docs/REPORT.md:95–96`  
> **Why it cannot be checked:** MCC 0.689 appears only in `notebooks/alphamissense.ipynb` cell 48, which has execution_count=2. This places it in a separate kernel session from the cells that computed AUC (cell 9, ec=6). The data state in that session is unknown. Whether 292 variants, or any other count, were used for the MCC computation cannot be confirmed from committed artifacts. The notebook is also out-of-sequence (compounding the issue, but the separate-session problem applies independently).

This claim was listed in `CLAIMS_LEDGER.csv` as NOT_CHECKABLE but was not described in the Part A report body. That was an omission. It is now stated above.

---

### Revised closing judgement

Part A concluded that all headline numbers survive and a draft could be written from this repository. That conclusion no longer holds for the primary analysis numbers.

**Numbers a paper can currently be drafted around (backed by RESULTS_CSV or SCRIPT_RECOMPUTED, or SEQUENTIAL notebook):**
- 1,278 variants scored, 0 missing (alphagenome_full_cftr_results.csv)
- n=292 binary, 253 CF-causing / 39 Non-CF-causing (cftr2_results_annotated.csv)
- Rescue counts: 693 discordant / 18 multi-tool confirmed / 58 AlphaGenome rescue (rescue_analysis.csv, recomputed)
- AlphaGenome-only rescue: 87 regulatory / 728 splicing / 56 dual (recomputable from alphagenome_full_cftr_results.csv)
- 693 discordant confirmed clean — SpliceAI made a genuine prediction for all 693 (spliceai_zero_reclassification.csv)
- 7 priority variant scores: AM scores (priority_candidates.csv), AlphaGenome quantiles (alphagenome_batch_results.csv)
- Domain distribution: 30/41 = 73.2% MSD1+MSD2, R-domain = 0 (varying_consequence_am.csv)
- 72 VCC variants, 41 LP (cftr2_results.csv + varying_consequence_am.csv)
- CADD mean 24.496 / SpliceAI: 52 above 0.2, 19 above 0.5 (comparator_analysis.csv)
- **Ensemble AUC 0.927, AP 0.983, weights +1.907/+0.279/−0.117 (ensemble.ipynb, sequential)**

**Numbers that cannot be drafted around in current form:**
- AUC 0.946 (only from OOS notebook, no committed CSV evidence; must re-run alphamissense.ipynb cleanly)
- AP 0.990 for the 292-variant validation set (no stored computation; must re-run)
- Comparison AUC values: CADD 0.776, PolyPhen 0.826, SIFT 0.678 (only from OOS comparison.ipynb)
- DeLong Z statistics and p-values (OOS notebook + unconfirmable n + incorrect implementation)
- MCC 0.689 (separate kernel session, OOS notebook)
- Counts: 705 LP / 357 ambiguous / 1349 benign / 2411 unclassified scored / 311 nonsense (all from OOS notebook only)

The AlphaGenome and rescue analysis (Phase 2) is in substantially better shape than the AlphaMissense validation (Phase 1). The Phase 2 headline numbers are backed by committed CSVs and are either verified or genuinely recomputable. Phase 1 requires a clean notebook re-run before any figure can be cited in a paper.

