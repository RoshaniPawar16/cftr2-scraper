# Check 10 Report — Phase 1 Benchmark Duplicates
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**No git operations. Part B locked.**

---

## What I could not establish

Nothing material is blocked. All computations completed from committed files.

---

## 10a — Uniqueness in benchmark_cohort.csv

```
$ wc -l results/phase1/benchmark_cohort.csv
293  (292 data rows + 1 header)

Total rows:     292
Unique variants: 259
Duplicate rows:   33  (29 duplicated identifiers)
```

**Every duplicated row carries identical values across all fields** — same label, same AM score, same CADD, same PolyPhen, same SIFT. No row carries differing scores for the same variant name.

**Duplicated identifiers in full:**

| Variant | Count | Label | AM | CADD | PolyPhen | SIFT_inv | Included |
|---|---|---|---|---|---|---|---|
| Met952Ile | 3 | 0 (Non-CF) | 0.8752 | 24.8 | 0.955 | 1.0 | True |
| Ser549Arg | 3 | 1 (CF) | 0.9948 | 27.1 | 1.0 | 1.0 | True |
| Phe311Leu | 3 | 1 (CF) | 0.9751 | 24.1 | 0.868 | 1.0 | True |
| Ser1235Arg | 3 | 0 (Non-CF) | 0.1926 | 20.5 | 0.206 | 0.99 | True |
| Arg1283Ser | 2 | 1 (CF) | 0.9924 | 22.6 | 0.999 | 1.0 | True |
| Arg560Ser | 2 | 1 (CF) | 0.9892 | 24.2 | 1.0 | 1.0 | True |
| Asn1303Lys | 2 | 1 (CF) | 0.9907 | 22.2 | 1.0 | 1.0 | True |
| Gln237His | 2 | 1 (CF) | 0.9058 | 21.9 | 1.0 | 1.0 | True |
| Gly1061Arg | 2 | 1 (CF) | 0.9912 | 32.0 | 1.0 | 1.0 | True |
| Gly1249Arg | 2 | 1 (CF) | 0.9533 | 28.7 | 1.0 | 1.0 | True |
| Gly149Arg | 2 | 1 (CF) | 0.9869 | 33.0 | 1.0 | 1.0 | True |
| Gly178Arg | 2 | 1 (CF) | 0.7577 | 32.0 | 0.997 | 1.0 | True |
| Gly194Arg | 2 | 1 (CF) | 0.9755 | 33.0 | 0.988 | 1.0 | True |
| Gly226Arg | 2 | 1 (CF) | 0.9886 | 31.0 | 0.997 | 1.0 | True |
| Gly27Arg | 2 | 1 (CF) | 0.9823 | 28.6 | 1.0 | 1.0 | True |
| Gly314Arg | 2 | 1 (CF) | 0.9875 | 29.3 | 0.991 | 1.0 | True |
| Gly628Arg | 2 | 1 (CF) | 0.877 | 29.1 | 1.0 | 1.0 | True |
| Gly85Arg | 2 | 1 (CF) | 0.9897 | 28.0 | 0.986 | 1.0 | True |
| Gly91Arg | 2 | 1 (CF) | 0.9474 | 32.0 | 0.941 | 1.0 | True |
| His199Gln | 2 | 1 (CF) | 0.9222 | 23.8 | 1.0 | 1.0 | True |
| Leu997Phe | 2 | 0 (Non-CF) | 0.7409 | 22.3 | 0.991 | 1.0 | True |
| Lys464Asn | 2 | 1 (CF) | 0.9589 | 34.0 | 0.994 | 1.0 | True |
| Met152Leu | 2 | 0 (Non-CF) | 0.1493 | 23.1 | 0.015 | 0.99 | True |
| Trp1098Arg | 2 | 1 (CF) | 0.9798 | 27.8 | 1.0 | 1.0 | True |
| Trp1098Cys | 2 | 1 (CF) | 0.8684 | (empty) | 1.0 | 1.0 | **False** (missing_cadd) |
| Trp1282Arg | 2 | 1 (CF) | 0.9934 | 26.5 | 1.0 | 1.0 | True |
| Trp361Arg | 2 | 1 (CF) | 0.9725 | 34.0 | 0.999 | 1.0 | True |
| Trp496Arg | 2 | 1 (CF) | 0.9959 | 28.1 | 1.0 | 1.0 | True |
| Trp57Arg | 2 | 1 (CF) | 0.997 | 28.3 | 0.982 | 1.0 | True |

**Duplicated by class:** 25 CF-causing identifiers (label=1), 4 Non-CF (label=0).

---

## 10b — Reconciling 292 against 259

`cftr2_results.csv` (the CFTR2 source file) has:
```
CF-causing:   226  (unique)
Non-CF:        33  (unique)
Total binary: 259  (all unique — zero duplicates)
```

`cftr2_results_annotated.csv` (the benchmark input) has:
```
CF-causing:   253  (34 rows above the 226 unique)
Non-CF:        39  (6 rows above the 33 unique)
Total binary: 292  (33 duplicates inflate the 259)
```

The benchmark script (`scripts/phase1_build_cohort.py`) reads `cftr2_results_annotated.csv`, not `cftr2_results.csv`:

```python
# phase1_build_cohort.py, line 56:
ANNOT_CSV = os.path.join(ROOT, 'data', 'cftr2_results_annotated.csv')
# line 60:
binary = [r for r in annotated
          if r['determination_2026'] in ('CF-causing', 'Non CF-causing')
          and r['am_pathogenicity']]
```

No deduplication step exists between the read and the cohort construction. The 292 rows flow directly into the benchmark.

**The gap:** 292 − 259 = 33 rows are duplicates from the annotated file. The 253 CF-causing figure in the benchmark does not come from cftr2_results.csv (which has 226); it comes from the inflated annotated file.

---

## 10c — Origin of the duplication

`cftr2_results_annotated.csv` is produced by `notebooks/alphamissense.ipynb` cell 9:

```python
# cell 9:
cftr_am = pd.read_csv("../data/cftr_alphamissense.tsv", sep="\t")

result = result.merge(
    cftr_am[["protein_variant", "am_pathogenicity", "am_class"]],
    left_on="am_variant",
    right_on="protein_variant",
    how="left"
).drop(columns=["protein_variant"])
```

This is a **left join on protein name** against `cftr_alphamissense.tsv`.

`cftr_alphamissense.tsv` contains:
```
Total rows:         9,721
Unique protein_variant:  8,597
Duplicate protein_variants: 960  (1,124 extra rows)
```

When one protein variant maps to multiple rows in `cftr_alphamissense.tsv` (because two or more distinct nucleotide changes produce the same amino acid substitution), the join produces multiple output rows per input variant. The AM score is identical for all duplicates — AlphaMissense scores protein changes, not nucleotide changes, so the same protein change always gets the same score regardless of which codon produced it.

**Why Gly→Arg and Trp→Arg dominate:** Arginine is encoded by 6 codons (CGU, CGC, CGA, CGG, AGA, AGG). A single codon for Glycine or Tryptophan can be changed to Arginine by two different single-nucleotide substitutions at the same codon position, producing two distinct VCF records with the same protein change.

Examples from `cftr_alphamissense.tsv`:
```
protein_variant='E1194D'  chr7:117627635  G>T  am=0.1303
protein_variant='E1194D'  chr7:117627635  G>C  am=0.1303
protein_variant='C1344S'  chr7:117664754  T>A  am=0.0854
protein_variant='C1344S'  chr7:117664755  G>C  am=0.0854
```

The join is a **one-to-many join** on the right side. It was not caught because the protein-name join key looked unique from the left side, and the AM scores (the main output) are identical across duplicates.

---

## 10d — Metrics: published versus deduplicated

Deduplication method: retain the first occurrence of each variant name in `benchmark_cohort.csv` row order.

### AlphaMissense on all rows

| Population | n | CF | Non-CF | AM AUC | AM AP |
|---|---|---|---|---|---|
| All rows (published) | 292 | 253 | 39 | 0.9459 | 0.9906 |
| Dedup all | 259 | 226 | 33 | **0.9549** | **0.9924** |

### All four predictors (included=True only)

| Population | n | CF | Non-CF | AM AUC | AM AP | CADD AUC | PP AUC | SIFT AUC |
|---|---|---|---|---|---|---|---|---|
| Published (n=286) | 286 | 247 | 39 | 0.9461 | 0.9905 | 0.7763 | 0.8261 | 0.6780 |
| Deduplicated (n=254) | 254 | 221 | 33 | **0.9548** | **0.9923** | **0.7489** | **0.8109** | **0.6701** |

**Direction of change:** AM AUC increases by +0.009 after deduplication. CADD, PolyPhen, and SIFT decrease by 0.016–0.027. This is because the duplicates are predominantly high-AM, high-CADD, high-PolyPhen CF-causing variants (17 Gly/Trp→Arg) — removing them improves AM's relative standing slightly and deflates the comparator AUCs slightly.

**The published headline (0.946) is not inflated by the duplication. It is slightly understated.** The correct deduplicated figure is 0.955. The AM advantage over all three comparators is larger on the deduplicated set, not smaller.

### Corrected DeLong tests

| Comparison | Published Z | Published p | Dedup Z | Dedup p |
|---|---|---|---|---|
| AM vs PolyPhen | 3.320 | 0.000900 | **3.512** | **0.000444** |
| AM vs CADD | 3.557 | 0.000375 | **3.834** | **0.000126** |
| AM vs SIFT | 6.777 | <0.000001 | **6.295** | **<0.000001** |

Significance direction is identical on both sets. The deduplicated DeLong Z-scores are larger for AM vs PolyPhen and CADD, smaller for AM vs SIFT. All remain highly significant.

### Six excluded variants (missing CADD)

These 6 rows are present in the 292 but excluded from the n=286 benchmark:

| Variant | Label | AM | Exclusion reason |
|---|---|---|---|
| Leu137Pro | CF-causing | 0.9444 | missing_cadd |
| Trp496Gly | CF-causing | 0.9260 | missing_cadd+sift+polyphen |
| Thr604Ile | CF-causing | 0.9201 | missing_cadd |
| Gly622Val | CF-causing | 0.8665 | missing_cadd+sift+polyphen |
| Trp1098Cys | CF-causing | 0.8684 | missing_cadd (×2 — duplicate) |

All are CF-causing with high AM scores. Trp1098Cys appears twice (itself a duplicate).

---

## 10e — Phase 2 (1,278 cohort)

```
1,278 cohort (alphagenome_full_cftr_results.csv):
  Total rows:            1,278
  Unique variant_id:     1,278  ← no duplicate variant_ids
  Unique protein_variant: 1,100
  Duplicate protein_variants: 178 extra rows across 145 protein names
```

**The 1,278 has no duplicate variant_ids.** The variant_id column (e.g., `chr7:117665559:T>G`) is unique for all 1,278 rows. The protein_variant column is not — 178 genomic positions produce the same amino acid change as another position — but all downstream counts (693, 18, 58, 87, 728, 56) are computed on unique variant_ids, not on protein names. **The Phase 2 counts are not affected by protein_variant duplication.**

---

## Patient VCF claim — retracted

### Prior wording (retracted)

`audit/COHORT_PROVENANCE.md` contained the following, which has now been amended:

```
- In patient VCF (observed in ≥1 patient in this cohort): 322 (25.2%)
- Not in patient VCF (never observed in this cohort): 956 (74.8%)
```
(Also line 60: "74.8% have never been observed in any patient in this cohort.")  
(Also line 79: "Cross-reference with patient VCF: only those with gnomAD AF > 0")

### What it actually measures

`All_Variants_VEP.Gene.vcf` is the ClinVar CFTR region (February 2025 release), processed as:  
ClinVar download → `bcftools extract chr7:117480000–117670000` → `bcftools normalize` → VEP v115.1 annotation (GRCh38.p14, Ensembl 115).  
Source: `audit/AUDIT_REPORT.md:151`. It carries no patient-level data.

The "322" is the count of 1,278 AM-ambiguous variants that appear in the ClinVar VEP VCF — **presence in a public variant database**, not observation in a patient cohort. The VCF is populated from ClinVar submissions; inclusion means at least one submitter reported the variant to ClinVar, not that it was observed in a specific patient in this project.

### Other files carrying the patient VCF language

All occurrences found:

| File | Line | Language |
|---|---|---|
| `audit/COHORT_PROVENANCE.md` | 43-44, 60, 79 | **Amended in this check** |
| `audit/AUDIT_REPORT.md` | 151, 159 | **Already corrected** — AUDIT_REPORT.md line 151 explicitly identifies it as a ClinVar extract; line 159 states "Both concerns are resolved: it is a public ClinVar database extract" |
| `audit/AUDIT_REPORT.md` | 561-562, 574, 585 | Uses "patient VCF" in quoted/historical text from Part A5, not as current claims — the correction at line 151 supersedes these |
| `docs/REPORT.md` | 9 | "Seven of these have population frequency support from gnomAD" — refers to the 7 priority variants; the "gnomAD" label is inaccurate (it is 1KG/AF_TGP, per Check 4) but the "patient VCF" language is not present here |

No document other than COHORT_PROVENANCE.md requires amendment for the patient VCF claim specifically. The AUDIT_REPORT.md already carries the correction.

---

## Reproducibility scope

### Input file public availability

| File | Public source | Pinnable? | Notes |
|---|---|---|---|
| `AlphaMissense_hg38.tsv.gz` | Zenodo 8208688 | **Yes** — DOI-permanent, md5/sha256 in SOURCE.md | Can be pinned |
| `cftr2_variants.xlsx` | `https://cftr2.org/sites/default/files/CFTR2_30January2026.xlsx` | **Partial** — URL is versioned by date but CFTR2 does not guarantee archival; no DOI | Risk of link rot |
| `gnomAD data` | Queried directly via gnomAD GraphQL API; results saved to `results/gnomad_cftr_lookup.csv` | **Yes** — gnomAD v4 is versioned; the saved CSV is the committed artifact | Version locked to gnomad_r4 at query time |
| `All_Variants_VEP.Gene.vcf` | ClinVar CFTR region (Feb 2025) + VEP v115.1 | **Yes** — ClinVar downloads are versioned by date; VEP is versioned | VEP flags are not recorded; reproducibility requires re-annotation with identical flags |

### What All_Variants_VEP.Gene.vcf is still used for

After gnomAD was queried directly (Check 4), the VCF retains the following consumers:

| Consumer | Field extracted | Can it be replaced? |
|---|---|---|
| `scripts/cftr2_scraper_analysis.py` | Protein variant names (HGVSp) — defines the 3,220-variant universe | **Yes** — ClinVar CFTR VCF is reproducible; protein names derivable from VEP re-annotation |
| `scripts/phase1_fetch_cadd.py` | Genomic coordinates (CHROM, POS, REF, ALT) for CADD REST API queries | **Yes** — coordinates come from ClinVar; can be parsed from a fresh ClinVar download |
| `scripts/phase1_build_cohort.py` | SIFT (CSQ field 31) and PolyPhen (CSQ field 32) scores | **Yes** — Ensembl VEP REST API returns SIFT and PolyPhen for any variant |
| `notebooks/alphamissense.ipynb` | AF (CSQ field 34, 1KG AF) — used to select the 7 priority variants; gnomAD already queried directly | **Yes** — 1KG AF now superseded by gnomAD v4 direct query |
| `notebooks/comparison.ipynb` | SIFT, PolyPhen, population AF | **Yes** — same as above |
| `notebooks/ensemble.ipynb` | SIFT, PolyPhen | **Yes** — same as above |

**Summary:** The VCF's only contributions are ClinVar-derived variant names and coordinates, plus VEP-annotated SIFT/PolyPhen scores and a 1KG AF field (now superseded by gnomAD). All of these are obtainable from public sources:
- Variant universe: ClinVar CFTR region download (Feb 2025 snapshot or later)
- Genomic coordinates: same ClinVar VCF
- SIFT and PolyPhen: Ensembl VEP REST API (or the Ensembl VEP standalone tool)
- Population frequency: gnomAD v4, now in `results/gnomad_cftr_lookup.csv`

**Dropping the VCF would break** the scripts that parse its CSQ fields directly (cftr2_scraper_analysis.py, phase1_build_cohort.py, phase1_fetch_cadd.py, and the notebooks). Those scripts would need to be updated to accept a VCF regenerated from ClinVar. The VEP flags (used to annotate the original VCF) are now known from AUDIT_REPORT.md:151, so regeneration is feasible with VEP v115.1 and GRCh38.p14.

**The VCF is the only unreproducible input only in the sense that the exact VEP flags were not committed alongside it.** Now that the pipeline is documented in AUDIT_REPORT.md:151, reproducibility is achievable. The decision to drop it or commit the regeneration script is yours.
