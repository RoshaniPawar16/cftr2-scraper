# Quarantine Manifest
Audit branch: integrity-audit-2026-07 · Date: 2026-07-29

## Items quarantined

None.

## Rationale

No file in this repository meets the quarantine criteria as defined in the audit instructions:

> Move — do not delete — anything you have classified as fabricated, synthetic, or orphaned-and-contradicted.

The two orphaned files identified (`results/alphagenome/alphagenome_rescue_variants.csv` and the untracked `results/gwas_overlap_analysis.csv`) are orphaned but **not contradicted**:

- `alphagenome_rescue_variants.csv`: The rescue group counts (87/728/56) independently recompute from `alphagenome_full_cftr_results.csv` using the documented criteria. Orphaned, not contradicted. Stays in place.
- `gwas_overlap_analysis.csv`: Untracked and unrelated to any committed result. No action required.

The stale notebook cell output in `notebooks/alphamissense.ipynb` cell 20 (showing 82 VCC vs the correct 72) is a stale output in a notebook file, not a standalone results file. Quarantining the notebook would destroy the verified outputs in other cells. The discrepancy is documented in CLAIMS_LEDGER.csv (claim C64: CONTRADICTED) and AUDIT_REPORT.md.
