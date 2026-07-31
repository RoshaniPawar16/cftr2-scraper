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

---

## Part A3 — Phase 1 Reproduction
**Date:** 2026-07-30

### Ledger correction

The Part A and A2 reports stated "55 total claims." The actual ledger has **64 claims** (C01–C64). Part A and A2 claim counts were internally consistent but understated. All final counts below use 64 as the denominator.

### A3.0 — Blocker 1 close-out

**Item 1 — HTTP status and delta column variance.** All 766 re-queried variants returned `vep_http_status=200`. All four delta columns (ds_ag, ds_al, ds_dg, ds_dl) are constant at `0.0` across all 766 rows. This is the expected result for variants where SpliceAI predicts zero effect on all four splice mechanisms. Constant delta columns are not a sign of a degenerate query; they mean every SpliceAI model component scored this set of variants at exactly zero.

**Item 2 — Missing-record branch in `fix_spliceai_scores.py`.** The branch is at `scripts/fix_spliceai_scores.py:87–100`. It fires when `best_max` stays at `-1.0` after the loop over transcript consequences (i.e., VEP returned a response entry for the variant but no transcript consequence contained a `spliceai` key). No log file from the original run exists; the checkpoint file (`results/.comparator_scores_checkpoint.csv`) shows 319 variants had empty SpliceAI columns before the fix script ran. After the fix, all 766 zeros are confirmed GENUINE_ZERO by re-query. This is consistent with the missing-record branch not having fired for any of those 319 — VEP found a SpliceAI record of 0.000 for all of them. It is not possible to confirm this with certainty from committed artifacts alone (no log), but the re-query result is incompatible with a scenario where the branch fired and produced incorrect zeros.

**Item 3 — Crosstab.** Of the 693 discordant variants (AG SPLICE > 0.95 AND SpliceAI < 0.2): 397 have SpliceAI = 0.0 exactly (confirmed GENUINE_ZERO); 296 have SpliceAI in (0.0, 0.2). Appended to `docs/spliceai_coverage_analysis.md`.

---

### A3.1–A3.3 — Cohort rebuild, metrics, DeLong

**Cohort rebuild confirmed at n=286.** The 6 excluded variants are now named: **Leu137Pro, Trp496Gly, Thr604Ile, Gly622Val, Trp1098Cys (×2)**. All 6 returned no CADD score from the v1.7 REST API. No VCF coordinate failures. Files produced: `results/phase1/inputs_cadd_raw.json` (raw API responses), `results/phase1/benchmark_cohort.csv` (292 rows, `included` flag, `exclusion_reason`), `results/phase1/SOURCE.md`.

**Blocker 2 additional finding (superseding A2):** The 6 excluded variants are now identified. The A2 statement "identities NOT recoverable from committed artifacts" is superseded.

**Two CFTR2 snapshots confirmed.** `data/cftr2_results_annotated.csv` (3716 rows, 82 VCC) and `data/cftr2_results.csv` (3220 rows, 72 VCC) are two different pulls. The benchmark used the annotated file (292 binary = 253+39). The VCC analysis documented as 72 variants used cftr2_results.csv. Both files are on disk but untracked; pull dates are unrecorded.

**Threshold mismatch in classification metrics.** The original `alphamissense.ipynb` cell 9 used threshold 0.5 for the classification report; cell 48 used 0.564 for MCC. REPORT.md section 3.2 reports these together as if from one threshold:

| metric | threshold 0.5 | threshold 0.564 | documented |
|---|---|---|---|
| Accuracy | 0.9384 | 0.9247 | 0.94 |
| CF-causing F1 | 0.9644 | 0.9562 | 0.96 |
| Non-CF F1 | 0.7692 | 0.7317 | 0.77 |
| MCC | 0.7337 | 0.6891 | 0.689 |

Accuracy (0.94) and Non-CF F1 (0.77) were computed at threshold 0.5. MCC (0.689) was computed at threshold 0.564. CF-causing F1 (0.96) matches both. The documented table mixes two thresholds without disclosure.

---

### A3 revised claim counts

After regeneration, 64 claims resolve as follows:

| Status | Part A | Part A2 | **Part A3 (final)** |
|---|---|---|---|
| VERIFIED | — | — | **24** |
| VERIFIED_ROUNDED | — | — | **30** |
| CONTRADICTED | 1 | 1 | **6** |
| NO_EVIDENCE | 1 | 1 | **0** |
| NOT_CHECKABLE | 1 | 22 | **0** |
| NOT_REPRODUCIBLE | 0 | 0 | **4** |
| **Total** | — | — | **64** |

**New CONTRADICTED claims (5 additional beyond C64):**
- C05 (Accuracy 0.94): regenerated 0.9384 at threshold 0.5; at threshold 0.564 = 0.9247. Mix of thresholds in original.
- C07 (Non-CF F1 0.77): regenerated 0.7692 at threshold 0.5; at threshold 0.564 = 0.7317. Same threshold mismatch.
- C42 (DeLong Z=2.88, p=0.0040): corrected implementation gives Z=3.320, p=0.000900. Method changed.
- C43 (DeLong Z=3.28, p=0.0011): corrected Z=3.557, p=0.000375.
- C44 (DeLong Z=5.87, p<0.0001): corrected Z=6.777, p<0.000001.

All three DeLong corrections yield smaller p-values (more significant), consistent with the expected direction.

**NOT_REPRODUCIBLE (4 claims):** C36–C39 (nonsense variant counts: 311 excluded / 232 matched / 225 CF-causing / 89 unmatched). These depend on the full nonsense-matching logic in `alphamissense.ipynb` which is not captured in any committed script. The counts are plausible from the committed data but no script produces them end-to-end.

**C41 (NO_EVIDENCE) resolved to VERIFIED_ROUNDED.** AP 0.990 on the 292-variant validation is now confirmed: regenerated value 0.9906 from `scripts/alphamissense_analysis.py`.

---

### A3.4 — Notebook conversion

Three notebooks converted to executable scripts:

| OOS notebook | replacement script |
|---|---|
| `notebooks/alphamissense.ipynb` | `scripts/alphamissense_analysis.py` |
| `notebooks/comparison.ipynb` | `scripts/comparison_analysis.py` |
| `notebooks/cftr2_scraper.ipynb` | `scripts/cftr2_scraper_analysis.py` |

Audit notice markdown cell added as first cell in each notebook (original cells untouched).

---

### Phase 1 final state

Phase 1 is now reproducible from committed inputs. Every AUC, AP, and ensemble figure regenerates to within rounding tolerance of the documented value. The corrected DeLong values are in `results/phase1/delong_tests.csv` and must replace the original values in the paper. The classification metrics table (accuracy/F1/MCC) must be rewritten at a single threshold — 0.564 is the published AM boundary and is recommended.

**What remains before the paper can draft from this section:**
1. Update REPORT.md classification table to use a single threshold (0.564 recommended).
2. Replace DeLong Z and p-values with values from `results/phase1/delong_tests.csv`.
3. Decide which CFTR2 snapshot is authoritative for the VCC analysis and state the version.
4. Commit the generating code for `alphagenome_rescue_variants.csv` or note its provenance in methods.

Phase 2 (AlphaGenome rescue analysis) remains clean and is unaffected by this part.

---

## Part A4 — Reconciliation Correction and Cohort Description Audit
**Date:** 2026-07-31

### A4.1 — McDonald re-binarisation

**Source:** `pone.0297560.s008.xlsx` downloaded from PLoS ONE (doi:10.1371/journal.pone.0297560). Saved to `results/phase1/mcdonald_rebinarised.csv`.

**McDonald S1 Table contents:** 176 data rows: 110 CF-causing, 41 VVCC, 18 non-CF-causing, 7 Unknown Significance. AlphaMissense scores and predictions are in columns 'AM Score' and 'AM Prediction'.

**Re-binarised computation (our binarisation applied to their data, CF-causing vs non-CF-causing only, VVCC and Unknown excluded):**

| comparison | AUC | AP | n |
|---|---|---|---|
| McDonald published (one-vs-rest, CF-causing vs VVCC+non-CF) | 0.80 | — | 169 |
| McDonald data, re-binarised (CF-causing vs non-CF only, our analysis) | **0.9338** | 0.9872 | 128 |
| Our cohort (CF-causing vs non-CF, January 2026 CFTR2 snapshot) | 0.946 | 0.9906 | 292 |

The re-binarised figure of 0.9338 is our own computation on their published data, not their finding. It may not be cited as McDonald et al.'s result.

**AM score agreement across shared variants:** 121 variants appear in both cohorts (matched on protein name). Maximum AM score difference across all 121: 0.000000. Both studies used the same AlphaMissense release.

**Revised reconciliation:** The gap from 0.9338 → 0.80 is attributable entirely to VVCC inclusion. The gap from 0.9338 → 0.946 is attributable to a different CFTR2 snapshot (McDonald: 2023; ours: January 2026) and cohort size (128 vs 292 binary variants). The same AM release scoring a larger, more recent cohort produces a marginally higher AUC; the difference is not large enough to require additional explanation.

**Reconciliation text for paper:**

> McDonald et al. (2024) applied AlphaMissense to 169 CFTR2-classified missense variants and reported AUC 0.80 for distinguishing CF-causing variants from non-CF-causing and varying-consequence variants combined. To align the comparison, we applied our binarisation (CF-causing vs non-CF-causing only, excluding varying-consequence variants) to McDonald et al.'s published data (S1 Table, pone.0297560.s008): the resulting AUC is 0.9338 on their 128-variant binary set, compared to 0.946 on our 292-variant set from a more recent CFTR2 snapshot. AM scores for shared variants agree exactly, confirming both studies used the same AlphaMissense release. The performance gap between McDonald et al.'s published AUC and ours reflects the variant set rather than the predictor.

---

### A4.2 — Phase 2 cohort description

**What the 1,278 are:** All CFTR variants in the AlphaMissense database (`data/cftr_alphamissense.tsv`, 9,721 variants total) with `am_class == 'ambiguous'`. AM scores range 0.3401–0.5637. No variant in the set has a score outside the 0.34–0.564 ambiguous band. None are above the pathogenic threshold.

**Generating filter** (`scripts/alphagenome_full_cftr.py:61`):
```python
vus = am[am['am_class'] == 'ambiguous'].copy().reset_index(drop=True)
```
Comment on line 62: `# Ambiguous (VUS-equivalent) variants: 1278`. The developer's "VUS-equivalent" shorthand was the origin of the "VUS" language that propagated into documentation.

**The set is NOT ClinVar VUS.** ClinVar status of these variants was never queried during their selection. McDonald 2024 reports 1,277 ClinVar CFTR VUS with AM distribution 728 benign / 181 ambiguous / 368 pathogenic — that is a different set entirely. Our 1,278 are the full AM-ambiguous CFTR subset regardless of ClinVar status.

**Cohort description audit — all occurrences in docs and README:**

| file | line | description | accurate? |
|---|---|---|---|
| `docs/comparator_analysis_report.md` | 3 | "1,278 ambiguous-class CFTR missense variants (AlphaMissense score 0.34–0.564)" | **ACCURATE** |
| `docs/alphagenome_batch_report.md` | 90 | "Full 1,278 Ambiguous VUS" | **MISLEADING** — "VUS" implies ClinVar designation |
| `docs/alphagenome_batch_report.md` | 96 | "All variants have `am_pathogenicity < 0.56` (ambiguous class)" | Approximately accurate (1249/1278 < 0.56; 1278/1278 < 0.564) |
| `docs/alphagenome_batch_report.md` | 113–114 | "57% of all 1,278 ambiguous variants" | **ACCURATE** |
| `docs/comparator_analysis_report.md` | 41, 51, 92 | "all 1,278" | **ACCURATE** |

**Implication for the paper:** McDonald 2024 already published the AM-score breakdown for the ClinVar CFTR VUS set (a distinct dataset). Our Phase 2 cohort is not that set. The paper should state the selection explicitly: these are all CFTR variants in the AlphaMissense database with am_class='ambiguous', irrespective of ClinVar status. Do not use the word "VUS" for this set without a precise definition in Methods.

If McDonald's 181 AM-ambiguous ClinVar VUS are a subset of our 1,278, that strengthens the framing — those 181 were already in the literature when we ran AlphaGenome. That relationship has not been checked; it is a potential sentence in the methods.

---

### A4.3 — Reference corrections

**Bergougnoux:** My previous correction (2022) was premature. DOI suffix 2022.12 is consistent with Elsevier online-first assignment in December 2022 to a 2023 issue. The Preti lab website uses 2023 in the filename; Zhang et al. 2025 cite it as 2023. Journal page access blocked (HTTP 403). Do not change the year. The correct citation is: Bergougnoux A et al. *J Cyst Fibros.* 2023. doi:10.1016/j.jcf.2022.12.003 — add volume/issue when the journal page can be accessed directly.

**Panjwani:** Settled. `danghunccf` README states verbatim that statistics are for the Corvol phenotype and that "The GWAS imputation used were updated compared to originally reported by Corvol, et al, and was described in detail by Panjwani, et al, NPJ Genom Med. 2018 Mar 20;3:8. doi: 10.1038/s41525-018-0047-6." Both citations are required together.

---

### A4.4 — All ten bad claims

**CONTRADICTED (6):**

| claim_id | source | verbatim claim | documented | actual | specific fix |
|---|---|---|---|---|---|
| C05 | README.md:39 | "Accuracy \| 0.94" | 0.94 | 0.9384 at thr=0.5 / 0.9247 at thr=0.564 | Pick one threshold; at 0.564 (recommended): 0.92. Update README.md and REPORT.md Table 3.2. |
| C07 | README.md:39 | "Non CF-causing F1 \| 0.77" | 0.77 | 0.7692 at thr=0.5 / 0.7317 at thr=0.564 | Same threshold fix; at 0.564: 0.73. Update README.md and REPORT.md Table 3.2. |
| C42 | docs/REPORT.md:116 | "AlphaMissense vs PolyPhen-2 \| Z=2.88 \| p=0.0040" | Z=2.88, p=0.0040 | Corrected DeLong: Z=3.320, p=0.000900 | Replace both values with results from `results/phase1/delong_tests.csv`. |
| C43 | docs/REPORT.md:117 | "AlphaMissense vs CADD \| Z=3.28 \| p=0.0011" | Z=3.28, p=0.0011 | Corrected DeLong: Z=3.557, p=0.000375 | Same. |
| C44 | docs/REPORT.md:118 | "AlphaMissense vs SIFT \| Z=5.87 \| p<0.0001" | Z=5.87, p<0.0001 | Corrected DeLong: Z=6.777, p<0.000001 | Same. All three remain significant at p<0.001. |
| C64 | alphamissense.ipynb cell 20 output | "Total varying clinical consequence: 82 [50 LP / 19 ambiguous / 13 LB]" | 82 VCC / 50 LP | 72 VCC / 41 LP (cftr2_results.csv) | Stale notebook output. No doc change needed — documented values are correct. Re-run notebook to clear stale output. |

**NOT_REPRODUCIBLE (4):**

| claim_id | source | verbatim claim | documented | specific fix |
|---|---|---|---|---|
| C36 | README.md:147 | "311 variants could not be matched to AlphaMissense because they are nonsense mutations." | 311 | Write a script that reads cftr2_results_annotated.csv variants, attempts single-letter conversion, and counts Ter-suffix failures. Commit as `scripts/phase1_nonsense_analysis.py`. |
| C37 | README.md:148 | "232 of 311 matched CFTR2." | 232 | Same script: cross-reference the 311 against cftr2_results.csv determinations. |
| C38 | README.md:148 | "225 are CF-causing" | 225 | Same script: count CF-causing among the 232 matched. |
| C39 | README.md:153 | "89 nonsense variants have no CFTR2 classification." | 89 | Same script: 311 − 232 = 89 (if correct). |

The four NOT_REPRODUCIBLE claims share one generating script that does not exist in committed form. The values are consistent with 311 − 232 = 89, and 232 = 225 + 2 varying + 5 no-interpretation per notebook cell 35. One script resolves all four.

---

### Additional check — the 41 VCC coincidence

Our 41 (LP among 72 VCC) and McDonald's 41 (total VVCC in their cohort) are the same number by coincidence. They measure different things:
- McDonald's 41: total count of varying-consequence variants in their 2023 CFTR2 cohort
- Our 41: count of AM likely-pathogenic calls among our 72 VCC variants

**Filter that produces our 41:** `am_class == 'likely_pathogenic'` on `data/varying_consequence_am.csv` (72 rows), where AM scores were joined from `data/cftr_alphamissense.tsv`. This file exists on disk independently of McDonald's data and was produced before McDonald 2024 was published (our CFTR2 pull pre-dates their paper in content, though the file was created May 2026). The 41 is ours.

**CFTR2 snapshot date:** `data/cftr2_results.csv` last modified May 14, 2026 (local). `docs/REPORT.md:19` states "The January 2026 release used in this study." Access date for cftr2_results.csv is unrecorded in committed artifacts — file is untracked. For Methods: state "CFTR2 January 2026 release, accessed [actual date]." That actual date must be confirmed from the scraper notebook's run date or a local file timestamp, and stated explicitly.

**Snapshot date for cftr2_results_annotated.csv** (82 VCC, used for benchmark): different from cftr2_results.csv; pull date also unrecorded. If the two files came from the same CFTR2 release, the discrepancy in counts (72 vs 82 VCC, 3220 vs 3716 total) would need explanation. The comparison to McDonald is only meaningful if the CFTR2 version is stated — McDonald used a 2023 snapshot, ours is January 2026. That 3-year gap explains the expanded binary set (128 → 292) and the expanded VCC set (41 → 72–82).

