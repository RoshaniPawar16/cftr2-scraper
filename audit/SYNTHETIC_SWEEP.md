# Synthetic Data / Fabrication Sweep
Audit branch: integrity-audit-2026-07 · Date: 2026-07-29

## Search terms applied

Across all `.py`, `.ipynb`, `.csv`, `.md` files (excluding `.venv/`, `.git/`):
`np.random`, `random.`, `rand()`, `randn`, `sample(`, `shuffle`, `make_classification`, `synthetic`, `simulate`, `dummy`, `mock`, `placeholder`, `example_`, `TODO`, `FIXME`, `XXX`, `hardcoded`, `hard-coded`; hardcoded numeric literals matching headline figures (`auc = 0.946`, `= 693`, `= 1278`); try/except blocks substituting default values; results files with no generating script.

---

## Findings

### F01 — `docs/REPORT.md:29` — `simulated variants`
```
CADD integrates over 60 genomic annotations... Training on simulated variants rather than known pathogenic or benign variants is a methodological choice...
```
**Assessment:** Refers to CADD's published training methodology (Kircher et al. 2014), not to synthetic data in this repository. Cleared.

### F02 — `docs/SCRAPER.md:41` — `hardcoded`
```
The spreadsheet URL is hardcoded to the Jan 2026 release.
```
**Assessment:** A maintenance note about a URL in the CFTR2 scraper notebook. No numeric result is affected. Cleared.

### F03 — `scripts/fetch_comparator_scores.py:78` — `except` substituting `np.nan`
```python
except Exception as e:
    log.warning('CADD error attempt %d: %s', attempt, e)
    time.sleep(BASE_BACKOFF)
return np.nan
```
**Assessment:** On CADD API failure after retries the function returns `np.nan`, not a fake score. In `build_comparator_analysis.py` line 59, `merged[CADD].fillna(0)` would treat this as 0 (CADD < 20) and count the variant toward the rescue group. However, the final `comparator_analysis.csv` contains 0 NaN CADD values — all 1278 variants received a real CADD score. The `fillna(0)` had no effect on the committed data. Cleared with caveat: if any future run produced API failures, this code would silently mis-classify affected variants as "CADD < 20."

### F04 — `scripts/fix_spliceai_scores.py:100` — substituting `0.0` for absent SpliceAI data
```python
'SpliceAI_max_delta': best_max if best_max >= 0 else 0.0,
```
**Assessment:** When VEP returns a response for a variant but no transcript consequence contains a `spliceai` key, `best_max` stays at `-1.0` and the script writes `0.0` to `SpliceAI_max_delta`. This makes genuine "zero splice effect" and "no SpliceAI data available" indistinguishable in the output. The final `comparator_analysis.csv` has 766 variants with SpliceAI_max_delta = 0.0 and 0 missing values. An unknown fraction of those 766 zeros may be "no data returned" rather than "confirmed zero." This affects the interpretation of the 693-discordant count (AG splice high AND SpliceAI < 0.2): all 693 have SpliceAI ≤ 0.2, but for a subset of those the 0.0 value may mean "VEP returned no SpliceAI record" rather than "confirmed no splice effect." **This is a methodology limitation, not fabrication.** The zeros are not invented; they are the output of a legitimate, documented query pipeline. The limitation must be stated in any paper that relies on the 693 figure.

### F05 — `scripts/build_comparator_analysis.py:59,73` — `fillna(0)` on CADD and SpliceAI
```python
(merged[CADD].fillna(0) < 20)
(merged[SA].fillna(0) < 0.2)
```
**Assessment:** Defensive coding that treats missing scores as below-threshold. No NaN values exist in the committed CSV, so no effect on results. Same caveat as F03: future runs with API failures would silently treat failures as low-risk calls. Cleared for the committed data; flag as a code quality concern.

### F06 — `scripts/alphagenome_batch.py:88-90` — `except` appending error row
```python
except Exception as e:
    rows.append({'Variant': v['label'], 'Protein': v['protein'], 'AM_score': v['am'], 'error': str(e)})
```
**Assessment:** On AlphaGenome API failure, an error row is appended with an explicit `error` key and missing score fields. No score substitution. Cleared.

### F07 — `scripts/alphagenome_full_cftr.py:164-185` — retry logic on API errors
**Assessment:** Implements exponential backoff for rate-limit errors and logs/gives up on persistent errors. Does not substitute values. Cleared.

### F08 — Hardcoded headline figures in scripts
Search for `auc = 0.946`, `AUC = 0.946`, `= 693`, `= 1278`, `= 0.927` in Python files: **zero hits**. The values `1,278` and `1278` appear in comments and print statements describing what the data contains, not as hardcoded results. The AUC/AP/weight values appear only in notebook cell outputs, computed from the data. Cleared.

### F09 — `results/alphagenome/alphagenome_rescue_variants.csv` — ORPHANED FILE
This file (871 rows, committed 2026-05-31 in commit 75cf885) has no identifying generating script or notebook. The commit added only this file and `docs/alphagenome_batch_report.md`. The rescue group counts (regulatory_rescue=87, splicing_rescue=728, dual_mechanism=56) can be independently recomputed from `results/alphagenome/alphagenome_full_cftr_results.csv` using the criteria in the documentation (ATAC_quantile_max > 0.95 and/or SPLICE_SITE_USAGE_quantile_max > 0.95, am_pathogenicity < 0.56), and they match. The file is therefore **orphaned but not contradicted**. Per audit rules, it is not quarantined. Documented in PROVENANCE.md.

### F10 — `results/gwas_overlap_analysis.csv` — UNTRACKED ORPHAN
This file is not tracked by git and has no generating script. It contains 693 data rows, all showing `nearest_gwas_locus=none_on_same_chromosome` (all CFTR variants are on chr7; no GWAS loci documented in Part B are on chr7). The file appears to be preliminary work for Part B, run before the audit. It does not affect any committed result. Not quarantined (not committed, not contradicted).

### F10 — `notebooks/alphamissense.ipynb` cell 20 stored output — CONTRADICTED NOTEBOOK OUTPUT
Cell 20 stored output: "Total varying clinical consequence: 82 / likely_pathogenic: 50 / ambiguous: 19 / likely_benign: 13." The committed `cftr2_results.csv` contains 72 VCC variants, not 82. The committed `varying_consequence_am.csv` has 72 rows (41 LP, 19 ambiguous, 12 LB), matching the documentation. The cell 20 output pre-dates the current data and was not updated when the data changed. This is a stale notebook output, not fabricated data — but it is the only stored computational artifact in the repo that contradicts the documented numbers. See AUDIT_REPORT.md for full analysis.

---

## np.random / random seeding

No calls to `np.random`, `random.`, `randn`, `rand()`, `make_classification`, or `shuffle` found in any script or notebook source cell. The logistic regression in `ensemble.ipynb` uses scikit-learn `StratifiedKFold` — this uses an internal random state but no explicit seed is set. The CV results are reproducible only if the scikit-learn version and NumPy PRNG state are identical. This is a reproducibility concern, not a fabrication concern.

---

## Summary

No fabricated or synthetic numeric results found. One stale notebook cell output (F10 cell 20) CONTRADICTS the committed CSV and documentation. Two coding patterns (F04, F05) create an ambiguity between "confirmed zero" and "no data" for SpliceAI that must be disclosed in the paper.
