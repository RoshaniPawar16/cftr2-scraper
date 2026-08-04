# B2b Tiling Scores — Provenance

**File:** `B2b_tiling_scores.csv`  
**Created:** 2026-08-04 (session: integrity-audit-2026-07; run date of API calls NOT recorded in file — see bug note below)  
**Script:** `scripts/b2b_tiling.py` (or equivalent session script)  
**Scorer:** CenterMaskScorer(ATAC, window=501, metric=L2_DIFF)  
**Tissue:** lung, UBERON:0002048  

---

## Run parameters (derivable from data, not stored as columns)

| Parameter | Value | How derived |
|---|---|---|
| Tiling step | 25 bp | Consecutive positions within each element are 25 bp apart (verified from pos column) |
| Alleles scored | All 3 non-reference substitutions per tiled position | Each unique (chrom, pos) has exactly 3 rows with alt ∈ {A,C,G,T} \ {ref} |
| DHS tiled positions | 150 unique genomic positions × 3 alts = 450 variants | — |
| Control positions | 143 unique genomic positions × 3 alts = 450 variants | Matched to intervals containing no DHS |
| API run date | **NOT RECORDED** | Not present in any column; see bug note |

---

## Source: DHS elements

12 DHS elements from Stolzenburg et al. 2017 (GSE52179), lifted to hg38 from
the published hg19 coordinates. DNase peak scores in the `dnase_score` column
are the GSE52179 DNase peak signal values.

---

## Bug note: pandas NA coercion of `kind='null'`

The original file produced by the scoring script used `kind='null'` as the
string label for control (non-DHS) positions. When read with default pandas
settings (`keep_default_na=True`, the default), the string `'null'` is coerced
to `NaN`, causing all 450 control rows to appear to have a missing `kind` value.

**Fix applied 2026-08-04:** The value `null` was renamed to `control` in the
`kind` column using `sed`. The file now reads correctly under default pandas
settings. Future scripts generating this file should use `control` (not `null`)
as the control label.

This is the **second pandas NA coercion bug in this project.** The first was
`routes_agree='NA'` in B1 liftover output, where the string `'NA'` was coerced
to `NaN` by default pandas CSV reading. In both cases the fix is either
`keep_default_na=False` at read time, or avoiding pandas NA-synonym strings
(`null`, `NA`, `nan`, `None`, `N/A`, etc.) as data values.

---

## Run date recovery attempt (2026-08-04)

Three sources were checked:

| Source | Outcome |
|---|---|
| `git log --follow --diff-filter=A` | First (and only) commit is the 2026-08-04 "rename null→control" fix; file was untracked before that session |
| macOS birth time (`stat -f %SB`) | 2026-08-04 13:07:01 — same as mtime; `sed -i ''` creates a new file, resetting both |
| Shell history | No match for b2b / tiling / alphagenome patterns |
| `.ckpt` files | Only `.B2_scored_variants_ckpt.csv` and `rescore_centermask.csv.ckpt` exist; no B2b tiling checkpoint |

**Conclusion: the original API run date is unrecoverable.** The best bound from
adjacent files (B2_pilot_run1.csv birth time 2026-08-03 21:40) is that the
tiling run occurred on or after 2026-08-03. No tighter bound is available.

## Determinism re-score (2026-08-04T12:15:30Z)

20 positions re-scored (2 per element, elements chr11.2516–chr11.2525) with
identical scorer and tissue. Results:

| Field | Value |
|---|---|
| alphagenome version | 0.6.1 |
| Run UTC | 2026-08-04T12:15:30Z |
| n scored | 20/20 |
| Max \|orig − new\| | 1.11e-16 (floating-point noise, effectively zero) |
| Exact matches (< 1e-6) | 20/20 |

All 20 scores agree to float precision. The backend is in the same state as
the original run. The missing run date does not affect interpretation of the
scores in this file.

## Missing provenance to add in future runs

The following fields are absent from the CSV and should be recorded as columns
or in an accompanying metadata file for full reproducibility:

- **API run date** — the date the AlphaGenome API calls were made (now unrecoverable for this file)
- **alphagenome package version** — added to `b2_pilot.py` and `b2_score_full.py` as `ag_version` column (2026-08-04)
- **Tiling step size** — currently derivable but should be explicit
