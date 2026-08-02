# Check 4 Report — Population Frequency Data
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**Status:** Diagnose and report only. No fixes applied beyond 4g amendment.

---

## What I could not establish

1. **Which VEP flags produced the VCF.** No VEP invocation command exists anywhere in the repository. `docs/SCRAPER.md:49` states the VCF was received externally ("Input VCF, VEP-annotated, CFTR gene. Not included, private data."). The flags used — `--af`, `--af_gnomad`, `--af_gnomade`, `--af_gnomadg`, `--max_af`, `--check_existing` — cannot be determined.

2. **The exact source of the CSQ AF value for Leu49Pro.** That variant has AF=0.0002 in CSQ but its INFO fields AF_TGP, AF_ESP, AF_EXAC are all absent. For the other six variants CSQ AF = AF_TGP exactly. Leu49Pro's AF may come from a minority 1KG population group or from a gnomAD annotation layer added during VEP annotation; without the VEP command this cannot be confirmed.

---

## 4a — Identity of CSQ field 34

**CSQ INFO header line (verbatim and complete):**

```
##INFO=<ID=CSQ,Number=.,Type=String,Description="Consequence annotations from Ensembl VEP. Format: Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|REF_ALLELE|UPLOADED_ALLELE|DISTANCE|STRAND|FLAGS|SYMBOL_SOURCE|HGNC_ID|MANE|MANE_SELECT|MANE_PLUS_CLINICAL|TSL|APPRIS|ENSP|SIFT|PolyPhen|HGVS_OFFSET|AF|CLIN_SIG|SOMATIC|PHENO|PUBMED|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|TRANSCRIPTION_FACTORS">
```

**Numbered field list (44 fields total):**

| i0 | i1 | Field name |
|---|---|---|
| 0 | 1 | Allele |
| 1 | 2 | Consequence |
| 2 | 3 | IMPACT |
| 3 | 4 | SYMBOL |
| 4 | 5 | Gene |
| 5 | 6 | Feature_type |
| 6 | 7 | Feature |
| 7 | 8 | BIOTYPE |
| 8 | 9 | EXON |
| 9 | 10 | INTRON |
| 10 | 11 | HGVSc |
| 11 | 12 | HGVSp |
| 12 | 13 | cDNA_position |
| 13 | 14 | CDS_position |
| 14 | 15 | Protein_position |
| 15 | 16 | Amino_acids |
| 16 | 17 | Codons |
| 17 | 18 | Existing_variation |
| 18 | 19 | REF_ALLELE |
| 19 | 20 | UPLOADED_ALLELE |
| 20 | 21 | DISTANCE |
| 21 | 22 | STRAND |
| 22 | 23 | FLAGS |
| 23 | 24 | SYMBOL_SOURCE |
| 24 | 25 | HGNC_ID |
| 25 | 26 | MANE |
| 26 | 27 | MANE_SELECT |
| 27 | 28 | MANE_PLUS_CLINICAL |
| 28 | 29 | TSL |
| 29 | 30 | APPRIS |
| 30 | 31 | ENSP |
| 31 | 32 | SIFT |
| 32 | 33 | PolyPhen |
| 33 | 34 | HGVS_OFFSET |
| **34** | **35** | **AF** ← the field the code reads |
| 35 | 36 | CLIN_SIG |
| 36 | 37 | SOMATIC |
| 37 | 38 | PHENO |
| 38 | 39 | PUBMED |
| 39 | 40 | MOTIF_NAME |
| 40 | 41 | MOTIF_POS |
| 41 | 42 | HIGH_INF_POS |
| 42 | 43 | MOTIF_SCORE_CHANGE |
| 43 | 44 | TRANSCRIPTION_FACTORS |

**The code indexes from 0.** The indexing line in `notebooks/alphamissense.ipynb` cell 17:

```python
AF_INDEX = 34
# ...
af_str = fields[AF_INDEX]   # 0-based; reads field named "AF"
```

**What `AF` is:**  
`AF` is VEP's standard allele frequency annotation, populated by the `--af` flag. Per VEP documentation, `--af` adds the minor allele frequency from 1000 Genomes Phase 3. This is **not gnomAD**. The VCF has no gnomAD-specific CSQ subfields (`gnomADg_AF`, `gnomADe_AF`, `gnomAD_AF`) and no gnomAD INFO fields in its header. The VCF header contains three population frequency INFO fields: `AF_TGP` (1000 Genomes Phase 3), `AF_EXAC` (ExAC), and `AF_ESP` (GO-ESP) — all from ClinVar, not from VEP gnomAD annotation.

**Verification against INFO fields for the 7 variants:**

| Variant | CSQ AF (index 34) | INFO AF_TGP | INFO AF_EXAC | INFO AF_ESP |
|---|---|---|---|---|
| Leu49Pro | 0.0002 | absent | absent | absent |
| Arg104Gly | 0.0002 | 0.0002 | 1e-05 | 8e-05 |
| Pro355Leu | 0.0002 | 0.0002 | 2e-05 | absent |
| Phe650Leu | 0.0002 | 0.0002 | absent | absent |
| Leu986Pro | 0.0004 | 0.0004 | 0.00012 | absent |
| His1054Gln | 0.0002 | 0.0002 | 1e-05 | absent |
| Arg1097Cys | 0.0002 | 0.0002 | 0.00018 | absent |

CSQ AF equals AF_TGP exactly for six of seven variants. For Leu49Pro, AF_TGP is absent but CSQ AF = 0.0002; source unknown without VEP command.

**The project's claim that these variants have "gnomAD population frequency data" is inaccurate.** The actual source is 1000 Genomes Phase 3 (AF_TGP) for six variants and unknown for one.

---

## 4b — Population of field 34 across the VCF

```
Records with CSQ block:                  5,923  (of 6,008 total lines)
CSQ blocks with non-empty AF at index 34:  318
CSQ blocks with empty AF at index 34:    5,605
Unique protein variants with AF > 0:       117  (after max-per-protein dedup, cell-17 logic)
```

Five examples with a non-empty value:
```
AF='0.0014'   protein=Arg31Cys
AF='0.0054'   protein=Arg74Trp
AF='0.0064'   protein=Arg75Gln
AF='0.0014'   protein=Ile148Thr
AF='0.0002'   protein=Arg258Gly
```

Five examples that are empty:
```
AF=''         protein=Ser13Phe
AF=''         protein=Arg31Leu
AF=''         protein=Ser42Phe
AF=''         protein=Asp44Gly
AF=''         protein=Ser50Tyr
```

**The number 7 is a property of the annotation intersected with AM class, not a property of population genetics.** 117 variants in the VCF have any AF value; of the 705 likely_pathogenic unclassified variants, only 7 unique protein names appear in those 117. The 117/5,923 = 2% AF coverage rate reflects 1000 Genomes Phase 3's sparse overlap with rare ClinVar-catalogued variants.

---

## 4c — VEP invocation

No VEP run command found anywhere in the repository. Searched all `.py`, `.sh`, `.md`, `.txt`, and `.ipynb` files for `--af`, `--af_gnomad`, `--max_af`, `--check_existing`, `variant_effect_predictor`, `vep.pl`, and `vep --`.

`docs/SCRAPER.md:49`:
> "`All_Variants_VEP.Gene.vcf` | Input VCF, VEP-annotated, CFTR gene. Not included, private data."

The VCF was received from a third party. The VEP flags used are unknown and unrecoverable from this repository. A methods section cannot describe the frequency annotation source with accuracy.

---

## 4d — VCF coverage of unclassified variants

```
Unique protein names extractable from VCF (all 3,220 input variants):   3,220
Unique likely_pathogenic unclassified variants (flagged_unclassified):     546  (deduped)
  Matched to VCF by protein name:  546 / 546  (100%)

cftr2_results_annotated.csv likely_pathogenic:  705  (includes duplicates)
  Matched to VCF by protein name:  705 / 705  (100%)
```

All 705 (546 unique) likely_pathogenic variants appear in the VCF. **VCF coverage is not the limiting factor.** The 7 were selected from 117 AF-bearing variants filtered to likely_pathogenic AM class — a pool that produces 10 rows (7 unique proteins, with His1054Gln and Phe650Leu duplicated in cftr2_results_annotated.csv).

The statement "7 with population data" is measuring the intersection of three things: (1) AM-likely_pathogenic class, (2) presence in the ClinVar VCF, and (3) 1000 Genomes Phase 3 observation. The 2,564 unclassified variants that are AM-ambiguous or AM-benign are not examined for AF in this code path at all.

---

## 4e — Join mechanics

**Regex (exact, from cell 17 source):**

```python
protein_pattern = re.compile(r'p\.([A-Z][a-z]{2}\d+[A-Z][a-z]{2})')
```

Applied to `fields[11]` (the HGVSp VEP column, e.g., `ENSP00000003084.6:p.Arg31Cys`). The captured group is the three-letter protein name without `p.` prefix (e.g., `Arg31Cys`).

**Left key:** `flagged_freq["variant"]` — three-letter protein name from `cftr2_results_annotated.csv` variant column (e.g., `Arg31Cys`).

**Ten literal left-key examples (from 705 likely_pathogenic set):**

```
left='Ser50Tyr'     in_variant_af_dict=False
left='Met244Lys'    in_variant_af_dict=False
left='Gln353His'    in_variant_af_dict=False
left='Gln353His'    in_variant_af_dict=False  ← duplicate row
left='Arg766Met'    in_variant_af_dict=False
left='Gln1071Pro'   in_variant_af_dict=False
left='Val1397Glu'   in_variant_af_dict=False
left='Ser4Leu'      in_variant_af_dict=False
left='Ser4Trp'      in_variant_af_dict=False
left='Pro5Ser'      in_variant_af_dict=False
```

The regex captures exactly the same three-letter format as the left keys. **The join itself is not broken by formatting differences.** The 695/705 misses are genuine absences from the 1000 Genomes AF pool, not regex failures.

Exact reproduction of cell 18 join (using cftr2_results_annotated.csv, 705 rows):
```
With AF (joined successfully): 10 rows  →  7 unique protein names
Without AF:                   695 rows
```
The 10 rows = 7 proteins because His1054Gln appears twice and Phe650Leu appears three times in the 705-row input.

---

## 4f — gnomAD ground truth

**gnomAD version:** v4.1 (`gnomad_r4`), GRCh38, queried 2026-08-02 via gnomAD GraphQL API.

**Total CFTR variants in gnomAD v4:** 7,577  
**Missense variants:** 2,466

### The 7 priority variants in gnomAD v4

Matched by genomic position (`7-POS-REF-ALT`). All 7 present.

| Variant | VCF CSQ AF | gnomAD exome AF | gnomAD genome AF |
|---|---|---|---|
| Leu49Pro | 0.0002 | absent | 6.56×10⁻⁶ |
| Arg104Gly | 0.0002 | 2.74×10⁻⁶ | 2.63×10⁻⁵ |
| Pro355Leu | 0.0002 | 2.05×10⁻⁶ | 3.28×10⁻⁵ |
| Phe650Leu | 0.0002 | 6.84×10⁻⁶ | 2.63×10⁻⁵ |
| Leu986Pro | 0.0004 | 3.41×10⁻⁵ | 1.31×10⁻⁵ |
| His1054Gln | 0.0002 | 6.17×10⁻⁶ | 6.57×10⁻⁶ |
| Arg1097Cys | 0.0002 | 5.82×10⁻⁵ | 9.21×10⁻⁵ |

The VCF AF values (0.0002 = 1 allele in ~5,000 in 1KG) are 3× to 30× higher than gnomAD v4 frequencies for the same variants. Both confirm extreme rarity. The VCF values are not gnomAD values.

### The 1,278 AM-ambiguous cohort in gnomAD v4

Matched by genomic position (`chr7:POS:REF>ALT` → `7-POS-REF-ALT`).

```
1,278 AM-ambiguous variants:
  Matched to gnomAD v4 by position:  326
  Not in gnomAD v4:                  952
  Matched with AF > 0:               291
  Matched with AF = 0 or absent:      35
```

**The project claim "None have gnomAD population frequency data" (audit/COHORT_PROVENANCE.md:60) is false.**  
**291 of 1,278 AM-ambiguous CFTR variants have gnomAD v4 AF > 0.**

Top 5 by gnomAD max AF:

| Variant | AM score | gnomAD exome AF | gnomAD genome AF | gnomAD max AF |
|---|---|---|---|---|
| D1270N | 0.5027 | absent | 4.16×10⁻³ | 4.16×10⁻³ |
| I285F | 0.5013 | 1.29×10⁻³ | absent | 1.29×10⁻³ |
| V201M | 0.3560 | 4.67×10⁻⁴ | absent | 4.67×10⁻⁴ |
| L1156F | 0.3913 | 4.01×10⁻⁴ | absent | 4.01×10⁻⁴ |
| R1070Q | 0.3980 | 3.09×10⁻⁴ | absent | 3.09×10⁻⁴ |

Results saved to `results/gnomad_cftr_lookup.csv` (1,279 lines: header + 1,278 rows; all 1,278 cohort members included, with gnomAD fields blank for the 952 not found).

---

## 4g — Amendment of the unsourced claim

`audit/COHORT_PROVENANCE.md:60` previously contained:

> "None have gnomAD population frequency data."

This sentence had no generating code. It was an assertion. It is now **RETRACTED and replaced** in COHORT_PROVENANCE.md with:

> **RETRACTED (2026-08-02, Check 4):** The sentence "None have gnomAD population frequency data" was an unsourced assertion with no generating code. It is withdrawn. Computed result from gnomAD v4 (gnomad_r4, GRCh38, position-matched): **291 of 1,278 have gnomAD AF > 0**; 952 are absent from gnomAD v4 entirely. See `results/gnomad_cftr_lookup.csv`. The prior assertion that the 1,278 are all unobserved is false.

The COHORT_PROVENANCE.md file has been amended in place. No other file has been modified; the incorrect language in `docs/alphagenome_batch_report.md` and elsewhere describing these variants as unobserved VUS is not corrected here — those are in the correction queue.

---

## Side item — Confirm 656

```python
# data/cftr2_results.csv
Total rows:                     3,220
Non-empty determination_2026:     656   ← confirmed
Blank determination_2026:       2,564
  CF-causing:                     226
  Varying clinical consequence:    72
  Non CF-causing:                  33
  No interpretation available:    325
  Sum of named categories:        656   ← exact match
```

Filter that produces 656: `determination_2026 != ''` (i.e., any row where the field is non-blank). The 656 figure is correct.

---

## Side item — Git tracking status of input files

```
$ git ls-files data/
(no output — zero tracked files in data/)
```

`data/` is **entirely gitignored**. The `.gitignore` file contains an explicit list:

```
data/All_Variants_VEP.Gene.vcf
data/AlphaMissense_hg38.tsv.gz
data/cftr2_variants.xlsx
data/cftr2_results.csv
data/cftr2_results_annotated.csv
data/cftr_alphamissense.tsv
data/flagged_unclassified.csv
data/flagged_prioritised.csv
data/priority_candidates.csv
data/priority_candidates_clinvar.csv
data/varying_consequence_am.csv
data/nonsense_variants_cftr2.csv
```

Every file used as input to Phase 1 and Phase 2 is unversioned. The consequence:

- **Phase 1 is not reproducible by anyone else.** The starting VCF (`All_Variants_VEP.Gene.vcf`) is described as private external data. The AlphaMissense database (`AlphaMissense_hg38.tsv.gz`) is downloadable from Zenodo but the exact version/checksum is not pinned anywhere.
- **No one can regenerate the cohort without the original VCF.** The 1,278, the 705, the 7, the 292 — all filter from files that are absent from the repository.
- **The VEP flags are unknown**, so even with the FASTA and a VEP install, the VCF cannot be reproduced.

This is a fundamental reproducibility gap. It does not affect the correctness of the committed results files, but it means the pipeline cannot be run from scratch by an independent party.
