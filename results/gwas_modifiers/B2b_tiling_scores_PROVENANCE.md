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

## Missing provenance to add in future runs

The following fields are absent from the CSV and should be recorded as columns
or in an accompanying metadata file for full reproducibility:

- **API run date** — the date the AlphaGenome API calls were made
- **Scorer version / model checkpoint** — if the API backend changes, raw scores may shift
- **Tiling step size** — currently derivable but should be explicit
