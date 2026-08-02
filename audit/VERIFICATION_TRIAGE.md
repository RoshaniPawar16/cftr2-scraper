# VERIFICATION TRIAGE
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**Scope:** Inventory only. No computations performed. No claims answered.

---

## Routing table

| # | Check | Evidence exists? | Where / what is missing | Can Claude Code do it? | Blocker |
|---|---|---|---|---|---|
| 1 | CFTR2 snapshot size and date | PARTIAL | `results/cftr2_results.csv` MISSING. `data/cftr2_results.csv` exists. No git log entry for that file. URL and access date recoverable from notebook. | YES | Path mismatch: file is at `data/`, not `results/` |
| 2 | AlphaMissense training claim (71 million) | PARTIAL | Claim is cited with in-text reference [7] in `README.md:35` and `docs/REPORT.md:35`. Reference list exists in README but [7] resolves to Cheng et al. — the paper itself, not a preprint citing the number. No file explicitly quotes the paper text. | NO — external literature | Verifying what Cheng et al. actually state requires the paper |
| 3 | Ensemble evaluation (fitting call + CV keywords) | YES | `notebooks/ensemble.ipynb`. Fitting for evaluation at Cell 9 (`cross_val_predict`). Separate `pipe.fit` at Cell 13 (weights only). All keywords present. | YES | None |
| 4 | gnomAD source and join | PARTIAL | "7 unclassified": `notebooks/alphamissense.ipynb` cells 17–18. "0 of 1,278": stated as a conclusion in `audit/COHORT_PROVENANCE.md:60,82`; no code computes it. VCF exists. First 3 data lines available. Join keys identified. | YES for most parts | "0 of 1,278" has no generating code — it is an analytical conclusion, not a computed result |
| 5 | AlphaGenome quantile definition | PARTIAL | Phrase "normalised rank across all human variants" appears in `docs/alphagenome_batch_report.md:5,25,26`. `docs/literature_review.md:49` defers to Avsec et al. 2026. No file specifies what the reference set is. | NO — external literature | What AlphaGenome's quantile reference set actually contains requires the paper |
| 6 | log2FC and bins values | YES | `results/alphagenome/alphagenome_batch_results.csv`. All three column families present. All 7 priority variants present (7 data rows). | YES | None |
| 7 | Metric comparison (quantile + log2FC, 7 and 1,278) | PARTIAL | For 7: both in `alphagenome_batch_results.csv` (no join needed). For 1,278: `alphagenome_full_cftr_results.csv` has quantile only — log2FC columns were never computed for 1,278. | YES for 7; BLOCKED for 1,278 | log2FC does not exist for 1,278 variants; the batch script was only run for the 7 priority variants |
| 8 | The 12 CFTR2-labelled variants | PARTIAL | `docs/positive_control_analysis.md` exists but is **untracked** (not committed). Lists all 12 in a table. No committed CSV. CFTR2 labels are not joined to the 1,278 in any committed result file. | YES — but join must be built from scratch | `positive_control_analysis.md` is untracked; the identifying join has no committed script |
| 9 | Pangolin feasibility | BLOCKED | Pangolin not installed. Reference genome FASTA: MISSING. Gene annotation database: MISSING. Network is accessible (HTTP 200 to ncbi.nlm.nih.gov). Input format: unknown. | BLOCKED — see blocker | Three separate blockers: no package, no FASTA, no annotation DB |

---

## Evidence record, item by item

### Item 1 — CFTR2 snapshot size and date

**`results/cftr2_results.csv`**: MISSING.

**`data/cftr2_results.csv`**: EXISTS.

```
$ ls -la /Users/roshani/Downloads/cftr2_scraper/data/cftr2_results.csv
-rw-r--r--@ 1 roshani  staff  113144 May 14 16:43 data/cftr2_results.csv

$ wc -l data/cftr2_results.csv
    3221 data/cftr2_results.csv

$ head -1 data/cftr2_results.csv
variant,protein_name,legacy_name,determination_2026,allele_frequency
```

Class breakdown column name: `determination_2026`.

**Scraper script:** `notebooks/cftr2_scraper.ipynb` exists. Cell 4 uses Selenium on `https://cftr2.org/welcome`. Cell 8 downloads directly:

```python
url = "https://cftr2.org/sites/default/files/CFTR2_30January2026.xlsx"
```

Access date encoded in URL: **30 January 2026**. Downloaded file: `data/cftr2_variants.xlsx`.  
`docs/SCRAPER.md` describes "January 2026 CFTR2 release".

**Git log for `data/cftr2_results.csv`:** No commits found — the file is not tracked in git history under that path (no `--diff-filter=A` result).

**File mtime:** May 14 16:43 (from `ls -la` above).

---

### Item 2 — AlphaMissense training claim

**What the repository says:** `docs/REPORT.md:35` (also `README.md:35`):

> "Pre-computed scores are available for 71 million variants across 19,233 human proteins."

This line carries in-text citation `[7]`. `docs/literature_review.md` section on AlphaMissense references "Cheng et al." and cites the AlphaGenome Avsec et al. paper for the quantile scores. The 71 million figure is attributed to the AlphaMissense paper via `[7]` but no file reproduces the paper's text or page number.

**Source cited in repo:** YES — citation [7] present. **Source verified against paper text:** CANNOT DO — external literature.

---

### Item 3 — Ensemble evaluation

**File:** `notebooks/ensemble.ipynb`  
`ls -la`: `-rw-r--r--@ 1 roshani staff 137351 May 28 11:30`

**Fitting call used for evaluation** (Cell 9):

```python
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=1000, random_state=42))
])

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
ensemble_probs = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba")[:, 1]
```

**Separate fitting call** (Cell 13, used only for weight reporting):

```python
pipe.fit(X, y)
coefs = pipe.named_steps["clf"].coef_[0]
```

**Keywords found in file:**

```
$ grep -n "cross_val\|train_test_split\|KFold\|StratifiedKFold\|cv=" notebooks/ensemble.ipynb
29:    "from sklearn.model_selection import StratifiedKFold, cross_val_predict\n",
266:    "cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)\n",
267:    "ensemble_probs = cross_val_predict(pipe, X, y, cv=cv, method=\"predict_proba\")[:, 1]\n",
```

`train_test_split` and `KFold`: NOT FOUND. `StratifiedKFold`, `cross_val_predict`, `cv=`: present.

---

### Item 4 — gnomAD source and join

**"7 unclassified variants with gnomAD data"**  
Source: `notebooks/alphamissense.ipynb`, cells 17–18.

Cell 17 extracts population AF from the ClinVar VCF CSQ field at index 34:

```python
AF_INDEX = 34
# reads data/All_Variants_VEP.Gene.vcf
```

Cell 18 joins:

```python
flagged_freq["vcf_af"] = flagged_freq["variant"].map(variant_af)
with_freq = flagged_freq[flagged_freq["vcf_af"].notna()]
# Output: "Flagged likely_pathogenic with population frequency: 7"
```

**"0 of 1,278 with gnomAD AF > 0"**  
Source: `audit/COHORT_PROVENANCE.md:60,82`. This is a **conclusion from population source analysis**, not a computed result:

> "None have gnomAD population frequency data." (line 60)  
> "The 1,278 are all AM-ambiguous CFTR variants, including theoretical ones never observed." (line 82)

No script computes "0 of 1,278" — the figure follows from the 1,278 being sourced from `data/cftr_alphamissense.tsv` (AlphaMissense pre-computed scores), which has no gnomAD AF field and was never filtered against the patient VCF.

**Same code path?** NO. The 7 uses the patient VCF via `notebooks/alphamissense.ipynb`. The "0 of 1,278" has no code path; it is an analytical conclusion.

**gnomAD access:** VEP-annotated ClinVar VCF file. gnomAD AF is embedded as field 34 within the VEP CSQ annotation, not from a separate gnomAD download.

**VCF file:**

```
$ ls -la data/All_Variants_VEP.Gene.vcf
-rw-r--r--@ 1 roshani  staff  5368289 May  1 16:51 data/All_Variants_VEP.Gene.vcf

$ wc -l data/All_Variants_VEP.Gene.vcf
    6008 data/All_Variants_VEP.Gene.vcf
```

**First three header lines:**

```
##fileformat=VCFv4.1
##fileDate=2026-04-15
##source=ClinVar
##reference=GRCh38
```

**First three data lines (verbatim):**

```
7	117480132	53845	C	T	.	.	ALLELEID=68512;...CSQ=T|missense_variant|...|p.Ser13Phe|...|deleterious_low_confidence(0)|probably_damaging(0.999)|...
7	117504290	35893	C	T	.	.	AF_ESP=0.00077;AF_EXAC=0.00168;AF_TGP=0.0014;...CSQ=T|...|p.Arg31Cys|...|0.0014|conflicting_classifications...
7	117504291	54087	G	T	.	.	ALLELEID=68754;...CSQ=T|...|p.Arg31Leu|...|uncertain_significance...
```

Genome build declared in header: **GRCh38**.

**Join keys:**  
Left side: `flagged_freq["variant"]` — three-letter protein name string (e.g., `"Arg31Cys"`).  
Right side: protein name extracted from VEP CSQ `p.` notation via regex `r'p\.([A-Z][a-z]{2}\d+[A-Z][a-z]{2})'`, stored as keys in `variant_af` dict.

---

### Item 5 — Quantile score definition

**Repository statements:**

`docs/alphagenome_batch_report.md:5`:
> "**Scores:** raw + quantile (normalised rank across all human variants)"

`docs/alphagenome_batch_report.md:25–26`:
> "**Quantile score**: normalised rank of the variant effect relative to all human variants for that output type. A quantile of 0.99 means the variant's effect is larger than 99% of all scored variants — tissue-specific."

`docs/literature_review.md:49`:
> "quantile score normalisation described in this paper" [Avsec et al. 2026]

**What is not documented in the repository:** The specific composition of "all human variants" in AlphaGenome's reference set (e.g., all possible SNVs genome-wide, a specific panel, or something else). The repository defers to Avsec et al. 2026 but does not reproduce the paper's definition.

---

### Item 6 — log2FC and bins values

**File:** `results/alphagenome/alphagenome_batch_results.csv`

```
$ ls -la results/alphagenome/alphagenome_batch_results.csv
-rw-r--r--@ 1 roshani  staff  2234 May 28 13:26

$ wc -l results/alphagenome/alphagenome_batch_results.csv
       8   (= 1 header + 7 data rows)
```

**Header:**

```
Variant,Protein,Position,REF>ALT,AM_score,
rna_mean_abs_log2fc,rna_max_abs_log2fc,rna_bins_gt05,
atac_mean_abs_log2fc,atac_max_abs_log2fc,atac_bins_gt05,
splice_mean_abs_log2fc,splice_max_abs_log2fc,splice_bins_gt05,
RNA_SEQ_raw,RNA_SEQ_quantile,ATAC_raw,ATAC_quantile,
SPLICE_SITE_USAGE_raw,SPLICE_SITE_USAGE_quantile
```

**Exact column names:**
- Max log2FC: `rna_max_abs_log2fc`, `atac_max_abs_log2fc`, `splice_max_abs_log2fc`
- Mean log2FC: `rna_mean_abs_log2fc`, `atac_mean_abs_log2fc`, `splice_mean_abs_log2fc`
- Bins affected: `rna_bins_gt05`, `atac_bins_gt05`, `splice_bins_gt05`

**All 7 priority variants present:** YES — 7 data rows (Leu49Pro, Arg104Gly, Pro355Leu, Phe650Leu, Leu986Pro, His1054Gln, Arg1097Cys), confirmed from full file content.

---

### Item 7 — Metric comparison

**For the 7 priority variants:**  
Both quantile (`RNA_SEQ_quantile`, `ATAC_quantile`, `SPLICE_SITE_USAGE_quantile`) and max log2FC (`rna_max_abs_log2fc`, `atac_max_abs_log2fc`, `splice_max_abs_log2fc`) are present in **the same file**: `results/alphagenome/alphagenome_batch_results.csv`. No join needed.

**For the 1,278 variants:**  
`results/alphagenome/alphagenome_full_cftr_results.csv` header:

```
variant_id,CHROM,POS,REF,ALT,protein_variant,am_pathogenicity,am_class,
RNA_SEQ_raw_max,RNA_SEQ_quantile_max,ATAC_raw_max,ATAC_quantile_max,
SPLICE_SITE_USAGE_raw_max,SPLICE_SITE_USAGE_quantile_max
```

This file has quantile only. It has **no log2FC columns**. Log2FC was never computed for the 1,278 — the batch script was only run for the 7 priority variants.

**A join would be needed:** Not merely a join — the log2FC data does not exist for 1,278 variants. The AlphaGenome batch scoring would need to be re-run for the full cohort to produce it.

---

### Item 8 — The twelve CFTR2-labelled variants

**`docs/positive_control_analysis.md`:**

```
$ git status docs/positive_control_analysis.md
On branch integrity-audit-2026-07
Untracked files:
    docs/positive_control_analysis.md
```

EXISTS but **UNTRACKED** (not committed to the branch). The file lists all 12 variants in a table. No committed CSV file.

The 12 were identified during audit Part A5 and written to this untracked file. No committed script produces the list.

**CFTR2 classifications joined to the 1,278:** NO. `alphagenome_full_cftr_results.csv` has no `determination_2026` column. The join would need to be built by cross-referencing `alphagenome_full_cftr_results.csv` (`protein_variant` column) against `data/cftr2_results_annotated.csv` (which has `am_variant` and `determination_2026`).

---

### Item 9 — Pangolin feasibility

**Pangolin installed:**

```
$ pip show pangolin
(no output)

$ python3 -c "import pangolin"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import pangolin
```

MISSING. Not installed.

**Reference genome FASTA:**

```
$ find /Users/roshani -name "*.fa" -maxdepth 4
(no output)

$ find /Users/roshani -name "*.fasta" -maxdepth 4
(no output)
```

MISSING.

**Gene annotation database:**

```
$ find /Users/roshani -name "*.gtf" -maxdepth 6
(no output)
```

MISSING.

**Network access:**

```
$ curl -s --max-time 10 -o /dev/null -w "%{http_code}" https://www.ncbi.nlm.nih.gov/
200
```

Network is accessible.

**Input format:** Cannot determine — Pangolin is not installed and cannot be inspected. Pangolin (the splice site predictor by Jaganathan et al.) conventionally requires a VCF, reference genome FASTA, and gene annotation GTF/database.

**Blockers (three separate):**
1. Package not installed
2. Reference genome FASTA absent from this machine
3. Gene annotation database absent from this machine

---

## MISSING items consolidated

Everything below was searched for and not found in this repository:

1. `results/cftr2_results.csv` — file is at `data/cftr2_results.csv`
2. Git log entry for `data/cftr2_results.csv` — file is not tracked in git history
3. A script or log that explicitly verifies the AlphaMissense "71 million" figure against the Cheng et al. paper text
4. Any file that documents what AlphaGenome's quantile reference set contains (deferred entirely to Avsec et al. 2026)
5. log2FC columns in `alphagenome_full_cftr_results.csv` — quantile only, no log2FC for 1,278 variants
6. A committed CSV of the 12 CFTR2 CF-causing variants within the 1,278
7. A committed script that identifies the 12 (the identification is in an untracked `.md` file)
8. A join of CFTR2 `determination_2026` labels onto `alphagenome_full_cftr_results.csv`
9. Pangolin package (`pip show pangolin` returns nothing)
10. Reference genome FASTA (no `.fa` / `.fasta` files anywhere in scope)
11. Gene annotation database (no `.gtf` / `.gff` files anywhere in scope)

---

## Ten bad claims

### CONTRADICTED claims (6)

---

```
claim_id: C05
verbatim claim text: "Accuracy | 0.94"
source file and line: README.md:39
status: CONTRADICTED
documented value: 0.94
actual value: 0.9384 at threshold 0.5 (rounds to 0.94); 0.9247 at threshold 0.564 (rounds to 0.92)
fix: The README table reports threshold-0.564 F1 scores alongside threshold-0.5 accuracy.
     The metrics are not from the same threshold. Correct to 0.92 (threshold 0.564)
     or report all metrics at a single threshold.
```

---

```
claim_id: C07
verbatim claim text: "Non CF-causing F1 | 0.77"
source file and line: README.md:39
status: CONTRADICTED
documented value: 0.77
actual value: 0.7692 at threshold 0.5 (rounds to 0.77); 0.7317 at threshold 0.564 (rounds to 0.73)
fix: Same threshold mismatch as C05. Correct to 0.73 (threshold 0.564)
     or report all metrics at a single threshold.
```

---

```
claim_id: C42
verbatim claim text: "AlphaMissense vs PolyPhen-2 | Z=2.88 | p=0.0040"
source file and line: docs/REPORT.md:116
status: CONTRADICTED
documented value: Z=2.88, p=0.0040
actual value: Z=3.320, p=0.000900 (corrected DeLong implementation, Sun & Xu 2014)
fix: The original implementation omitted the covariance term. Replace with
     corrected values Z=3.320, p=0.0009. Significance direction unchanged.
```

---

```
claim_id: C43
verbatim claim text: "AlphaMissense vs CADD | Z=3.28 | p=0.0011"
source file and line: docs/REPORT.md:117
status: CONTRADICTED
documented value: Z=3.28, p=0.0011
actual value: Z=3.557, p=0.000375 (corrected DeLong)
fix: Replace with Z=3.557, p=0.000375.
```

---

```
claim_id: C44
verbatim claim text: "AlphaMissense vs SIFT | Z=5.87 | p<0.0001"
source file and line: docs/REPORT.md:118
status: CONTRADICTED
documented value: Z=5.87, p<0.0001
actual value: Z=6.777, p<0.000001 (corrected DeLong)
fix: Replace with Z=6.777, p<0.000001. Same qualitative conclusion.
```

---

```
claim_id: C64
verbatim claim text: "Total varying clinical consequence: 82 [with 50 likely_pathogenic 19 ambiguous 13 likely_benign]"
source file and line: notebooks/alphamissense.ipynb cell 20 stored output
status: CONTRADICTED
documented value: 82 VCC total, 50 likely_pathogenic
actual value: 72 VCC total (Counter from data/cftr2_results.csv);
             41 likely_pathogenic, 19 ambiguous, 12 likely_benign (data/varying_consequence_am.csv)
fix: Notebook stored output is stale. Correct values are 72 VCC / 41 LP / 19 amb / 12 LB.
     README lines 115–132 correctly report 72 and match the CSV; the notebook cell is
     the sole source of the contradicted numbers.
```

---

### NOT_REPRODUCIBLE claims (4)

---

```
claim_id: C36
verbatim claim text: "311 variants could not be matched to AlphaMissense because they are nonsense mutations."
source file and line: README.md:147
status: NOT_REPRODUCIBLE
documented value: 311
actual value: Not reproduced — no committed script applies the nonsense exclusion filter.
              Notebook cell 36 stores output "Total nonsense variants in VCF: 311"
              but the generating kernel session is not reproducible from committed artifacts.
fix: Add a committed script that applies the nonsense filter to data/All_Variants_VEP.Gene.vcf
     and reproduces the 311 count.
```

---

```
claim_id: C37
verbatim claim text: "232 of 311 matched CFTR2."
source file and line: README.md:148
status: NOT_REPRODUCIBLE
documented value: 232
actual value: Not reproduced — same notebook OOS issue as C36.
fix: Same fix as C36; the script must also produce the CFTR2-matched subset.
```

---

```
claim_id: C38
verbatim claim text: "225 are CF-causing"
source file and line: README.md:148
status: NOT_REPRODUCIBLE
documented value: 225
actual value: Not reproduced — same notebook OOS issue as C36–C37.
fix: Same fix as C36.
```

---

```
claim_id: C39
verbatim claim text: "89 nonsense variants have no CFTR2 classification."
source file and line: README.md:153
status: NOT_REPRODUCIBLE
documented value: 89
actual value: Not reproduced — same notebook OOS issue as C36–C38.
fix: Same fix as C36. The 89 = 311 − 232, so it follows arithmetically
     once 311 and 232 are reproduced.
```
