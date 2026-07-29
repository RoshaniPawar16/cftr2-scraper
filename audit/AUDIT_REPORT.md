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

**Conclusion:** A draft could be written from this repository, citing the CSV files and scripts rather than the notebook outputs. The paper would need to be honest about the SpliceAI 0.0 ambiguity and the AP evidence gap. Before submission, both primary notebooks should be cleared of stored outputs and re-run end-to-end against the committed data files, and the generating code for `alphagenome_rescue_variants.csv` should be committed.
