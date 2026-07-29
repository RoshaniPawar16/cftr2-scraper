# Provenance Chain
Audit branch: integrity-audit-2026-07 · Date: 2026-07-29

Format: `results/file.csv  <-  generator  (line N)  [inputs: x, API: y]`

---

## Traced results files

```
results/alphagenome/alphagenome_batch_results.csv
    <- scripts/alphagenome_batch.py (line 93: df.to_csv(...))
       [inputs: data/priority_candidates.csv (7 variants); API: AlphaGenome v0.6.1]
    <- scripts/alphagenome_quantile_scores.py (line 122: merged.to_csv(...))
       [inputs: same 7 variants; API: AlphaGenome v0.6.1]
    NOTE: two scripts both write to this path. The committed file has 7 rows with quantile
          columns matching alphagenome_quantile_scores.py output format.

results/alphagenome/alphagenome_quantile_scores_raw.csv
    <- scripts/alphagenome_quantile_scores.py (line 126: lung_df.to_csv(...))
       [inputs: data/priority_candidates.csv; API: AlphaGenome v0.6.1]

results/alphagenome/alphagenome_full_cftr_results.csv
    <- scripts/alphagenome_full_cftr.py (line 210: final_df.to_csv(OUTPUT_CSV))
       [inputs: data/cftr2_results.csv (1278 ambiguous variants filtered from 3220);
        API: AlphaGenome v0.6.1]

results/alphagenome/alphagenome_cftr_f508i_summary.csv
    <- notebooks/alphagenome_cftr.ipynb (cell with to_csv call, line ~646)
       [inputs: AlphaGenome API, F508I variant]

results/comparator_scores.csv
    <- scripts/fetch_comparator_scores.py (line 236: final_scores.to_csv(OUTPUT_CSV))
       THEN OVERWRITTEN BY:
    <- scripts/fix_spliceai_scores.py (line 127: df.to_csv(COMP_CSV))
       [inputs: data/cftr2_results.csv variants; API: CADD v1.7 REST; API: Ensembl VEP SpliceAI plugin]
    NOTE: checkpoint file results/.comparator_scores_checkpoint.csv shows SpliceAI columns
          were empty for some variants before fix_spliceai_scores.py ran.

results/.comparator_scores_checkpoint.csv
    <- scripts/fetch_comparator_scores.py (line 235: final_scores.to_csv(CHECKPOINT))
       [intermediate artifact; SpliceAI columns partially populated]

results/comparator_analysis.csv
    <- scripts/build_comparator_analysis.py (line 44: merged.to_csv(OUT_CSV))
       [inputs: results/alphagenome/alphagenome_full_cftr_results.csv,
                results/comparator_scores.csv]

results/rescue_analysis.csv
    <- scripts/build_comparator_analysis.py (line 83: combined.to_csv(RESCUE))
       [inputs: same as comparator_analysis.csv; three rescue groups concatenated]
```

---

## Orphaned results files (no generating script identified)

```
results/alphagenome/alphagenome_rescue_variants.csv  *** ORPHAN ***
    Committed: 2026-05-31, commit 75cf885 ("add rescue variant analysis (regulatory=87, splicing=728, dual=56)")
    Commit contained only this file and docs/alphagenome_batch_report.md.
    No script in scripts/ produces this file.
    No notebook cell found writing to this path.
    The rescue group counts (87/728/56) are independently recomputable from
    results/alphagenome/alphagenome_full_cftr_results.csv using the criteria
    documented in docs/alphagenome_batch_report.md (ATAC_q>0.95 and/or SPLICE_q>0.95,
    am_pathogenicity<0.56). Recomputation confirms counts match.
    CLASSIFICATION: Orphaned, not contradicted. Stays in place per audit rules.
```

---

## Untracked orphaned files (not in git)

```
results/gwas_overlap_analysis.csv  *** UNTRACKED ORPHAN ***
    Not committed. No generating script found.
    Content: 693 rows, all CFTR variants on chr7 showing 'none_on_same_chromosome'
    for nearest_gwas_locus. Appears to be preliminary Part B work.
    No committed result depends on this file.
    CLASSIFICATION: Untracked, no effect on committed data.
```

---

## Dead scripts (scripts that generate a file not present in the repo)

None identified. All `to_csv()` calls in scripts map to files that exist in the committed tree, or to intermediate files (checkpoint) that exist as working artifacts.

---

## Scripts with no results output

```
scripts/write_comparator_report.py
    Reads: results/rescue_analysis.csv, results/comparator_analysis.csv
    Produces: printed output / markdown string (used to generate docs/comparator_analysis_report.md)
    No CSV output. The report doc was committed separately.
    NOT a dead script — it is a report generator that writes to stdout/docs.
```

---

## Data files with no generating script (inputs, not outputs)

These are input or intermediate files produced outside the repo (downloads, scrapes):
- `data/cftr2_results.csv` — produced by `notebooks/cftr2_scraper.ipynb` (scrapes cftr2.org)
- `data/cftr2_variants.xlsx` — source download from cftr2.org, not generated here
- `data/cftr2_results_annotated.csv` — produced by `notebooks/alphamissense.ipynb`
- `data/cftr_alphamissense.tsv` — produced by `notebooks/alphamissense.ipynb`
- `data/flagged_unclassified.csv` — produced by `notebooks/alphamissense.ipynb`
- `data/flagged_prioritised.csv` — produced by `notebooks/alphamissense.ipynb`
- `data/priority_candidates.csv` — produced by `notebooks/alphamissense.ipynb`
- `data/priority_candidates_clinvar.csv` — produced by `notebooks/alphamissense.ipynb`
- `data/varying_consequence_am.csv` — produced by `notebooks/alphamissense.ipynb`
- `data/nonsense_variants_cftr2.csv` — produced by `notebooks/alphamissense.ipynb`
- `data/All_Variants_VEP.Gene.vcf` — external input (VEP-annotated VCF), not generated here
- `data/AlphaMissense_hg38.tsv.gz` — downloaded from Zenodo record 8208688 (not generated here)

None of these are results files. They are upstream inputs or notebook-produced intermediates. Their absence from git is documented in the README.
