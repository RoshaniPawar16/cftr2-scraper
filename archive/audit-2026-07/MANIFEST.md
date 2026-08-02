# Archive Manifest — Audit 2026-07

**Branch:** integrity-audit-2026-07  
**Archived:** 2026-08-02  
**Archived by:** closeout pass following twenty-one audit checks  

Nothing was deleted. All files are moved, not removed. The originals
no longer exist at their previous paths; the archive paths below are
the permanent record.

---

## Files archived

| Original path | Archive path | Category | Reason | Producing check |
|---|---|---|---|---|
| `results/gwas_overlap_analysis.csv` | `archive/audit-2026-07/results/gwas_overlap_analysis.csv` | ARCHIVE — superseded | Quarantine manifest (2026-07-29) classified this as untracked and unrelated to any committed result; never referenced by any analysis | None — quarantine disposition |
| `results/alphagenome/l2diff_scores.csv.ckpt` | `archive/audit-2026-07/results/alphagenome/l2diff_scores.csv.ckpt` | ARCHIVE — scratch | Checkpoint file; final output is `results/alphagenome/l2diff_scores.csv` | Check 16 |
| `results/alphagenome/rescore_centermask.csv.ckpt` | `archive/audit-2026-07/results/alphagenome/rescore_centermask.csv.ckpt` | ARCHIVE — scratch | Checkpoint file; final output is `results/alphagenome/rescore_centermask.csv` | Check 15 |
| `results/codon_pairs_tracks/cm_rescore_323_ckpt.csv` | `archive/audit-2026-07/results/codon_pairs_tracks/cm_rescore_323_ckpt.csv` | ARCHIVE — scratch | Checkpoint for 323-variant center-mask rescore; data consolidated in `rescore_centermask.csv` | Check 15 |
| `results/codon_pairs_tracks/predict_variant_ckpt.csv` | `archive/audit-2026-07/results/codon_pairs_tracks/predict_variant_ckpt.csv` | ARCHIVE — scratch | Checkpoint for retracted Check 14b per-bin analysis; the finding it supported was retracted in Check 15 | Check 14 |

---

## Files modified in place (not moved)

| Path | Action | Reason |
|---|---|---|
| `results/codon_pairs_tracks/H620Q_splice_perbin.csv.gz` | Compressed in place from `.csv` (33 MB → 5.8 MB); uncompressed file removed | KEEP — evidence; raw data for the Check 14b retraction; size reduced by gzip, not archived |

---

## Files not archived

All other files created or modified during the audit branch remain at
their original paths. See `audit/checks/INDEX.md` for the check
reports, and `docs/AUDIT_RECORD.md` for the full audit summary.

The following files must never be moved or overwritten, regardless of
future reorganisation:

- `results/alphagenome/alphagenome_full_cftr_results.csv` — the only copy of the chromosome-22 calibration quantiles; evidence for the reproducibility finding
- `results/alphagenome/quantiles_genomewide_2026-08.csv` — paired genome-wide regeneration with `raw_changed` flag
- `results/experimental_benchmark.csv` — 23 experimentally validated CFTR variants; the only such list in the project
- `results/phase1/` (entire directory) — benchmark cohort and all phase 1 inputs and outputs
- `audit/CLAIMS_LEDGER.csv` and `audit/AUDIT_REPORT.md` — master audit record
- `data/` (entire directory) — primary input data, gitignored but present on disk
