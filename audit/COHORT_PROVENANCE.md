# Cohort Provenance
Audit branch: integrity-audit-2026-07 · Date: 2026-07-31

Every cohort described in docs/ or README.md. For each: stated criteria, source file, applied filter, reproduced count, stated count, agrees yes/no.

---

| Cohort | Stated criteria (verbatim) | Source file | Applied filter | Reproduced count | Stated count | Agrees |
|---|---|---|---|---|---|---|
| **n=292** binary validation | "292 variants (253 CF-causing, 39 Non CF-causing)" | `data/cftr2_results_annotated.csv` | `determination_2026 in {CF-causing, Non CF-causing} AND am_pathogenicity not empty` | 292 | 292 | **Yes** |
| **n=286** benchmark | "286 variants with all four scores available" | `data/cftr2_results_annotated.csv` + CADD API + VCF | n=292 minus 6 variants returning no CADD score | 286 | 286 | **Yes** |
| **n=72** VCC | "72 variants in CFTR2 are marked as varying clinical consequence" | `data/cftr2_results.csv` | `determination_2026 == 'Varying clinical consequence'` | 72 | 72 | **Yes** |
| **n=41** LP VCC | "41 of 72 are called likely pathogenic" | `data/varying_consequence_am.csv` | `am_class == 'likely_pathogenic'` | 41 | 41 | **Yes** |
| **n=7** priority | "only 7 had gnomAD population frequency data" | `data/priority_candidates.csv` | AM class likely_pathogenic (score >0.564) AND gnomAD AF present in VCF | 7 | 7 | **Yes** |
| **n=1,278** AM-ambiguous | "1,278 ambiguous-class CFTR missense variants (AlphaMissense score 0.34–0.564)" | `data/cftr_alphamissense.tsv` | `am_class == 'ambiguous'` | 1,278 | 1,278 | **Yes — count correct. Population description WRONG — see below** |
| **n=693** discordant | "693 variants … AG splice quantile > 0.95 AND SpliceAI < 0.2" | `results/rescue_analysis.csv` | `rescue_group == 'discordant_ag_high_splice_low'` | 693 | 693 | **Yes** |
| **n=18** multi-tool | "18 variants … AG splice >0.95 AND SpliceAI >0.5" | `results/rescue_analysis.csv` | `rescue_group == 'multi_tool_confirmed'` | 18 | 18 | **Yes** |
| **n=58** AlphaGenome rescue | "58 variants … (ATAC or SPLICE q>0.95) AND CADD<20 AND SpliceAI<0.2" | `results/rescue_analysis.csv` | `rescue_group == 'alphagenome_rescue'` | 58 | 58 | **Yes** |
| **n=128** McDonald binary | "McDonald's 110 CF-causing and 18 non-CF-causing" | `pone.0297560.s008.xlsx` (McDonald S1) | `Determiniation in {CF-causing, Non CF-causing}` | 128 | 128 | **Yes** |
| **n=87** regulatory rescue | "87 variants … ATAC q>0.95 AND AlphaMissense <0.56" | `results/alphagenome/alphagenome_full_cftr_results.csv` | `ATAC_quantile_max>0.95 AND am_pathogenicity<0.56` | 87 | 87 | **Yes** |
| **n=728** splicing rescue | "728 variants … SPLICE q>0.95 AND AlphaMissense <0.56" | `results/alphagenome/alphagenome_full_cftr_results.csv` | `SPLICE_SITE_USAGE_quantile_max>0.95 AND am_pathogenicity<0.56` | 728 | 728 | **Yes** |
| **n=56** dual mechanism | "56 variants … ATAC q>0.95 AND SPLICE q>0.95 AND AlphaMissense <0.56" | `results/alphagenome/alphagenome_full_cftr_results.csv` | `ATAC>0.95 AND SPLICE>0.95 AND am_pathogenicity<0.56` | 56 | 56 | **Yes** |

---

## The n=1,278 population problem (detail)

**Count verified.** The filter `am_class == 'ambiguous'` applied to `data/cftr_alphamissense.tsv` reproduces 1,278 exactly.

**Population is wrong in docs.** The source file `data/cftr_alphamissense.tsv` is the AlphaMissense pre-computed database filtered to CFTR (UniProt P13569). It contains **all single-nucleotide missense substitutions achievable by a single SNV in CFTR that AlphaMissense has pre-scored** — 9,721 rows in total, covering 1,479 residue positions and 8,597 unique protein changes. No ClinVar filter, no patient-observation filter, no gnomAD filter exists in the generation pipeline (`scripts/alphagenome_full_cftr.py:61`).

**Source file header (verbatim):**
`CHROM\tPOS\tREF\tALT\tgenome\tuniprot_id\ttranscript_id\tprotein_variant\tam_pathogenicity\tam_class`

**Three verbatim data rows:**
```
chr7	117480098	C	G	hg38	P13569	ENST00000003084.10	Q2E	0.1434	likely_benign
chr7	117480098	C	A	hg38	P13569	ENST00000003084.10	Q2K	0.183	likely_benign
chr7	117480099	A	G	hg38	P13569	ENST00000003084.10	Q2R	0.1896	likely_benign
```

**Observation status of the 1,278:**

**RETRACTED (2026-08-02, Check 10):** The phrasing "patient VCF" and "patient cohort" was false. `All_Variants_VEP.Gene.vcf` is not a patient cohort VCF. Per `audit/AUDIT_REPORT.md:151`, it is the CFTR region of the ClinVar variant database (February 2025 release), processed as: ClinVar download → bcftools extract chr7:117480000–117670000 → bcftools normalize → VEP v115.1 annotation (GRCh38.p14, Ensembl 115). It carries no patient-level data.

- In ClinVar VEP VCF: **322 (25.2%)** ← presence in ClinVar CFTR region, not patient observation
- Not in ClinVar VEP VCF: **956 (74.8%)**
- With gnomAD allele frequency > 0: **291 (22.8%)** ← corrected (Check 4; was "0 (0%)", retracted)
- No ClinVar data in committed artifacts (no ClinVar query exists in the path to the 1,278)

**CFTR2 status of the 1,278:**
- CF-causing: **12** (known disease-causing variants where AlphaMissense scored them as ambiguous)
- Non-CF-causing: **1**
- Varying clinical consequence: **19**
- No interpretation available: **42**
- No CFTR2 record: **1,204 (94.2%)**

**The 12 CFTR2 CF-causing variants in the set** (listed by AM score, ascending):
H954P (0.367), Y913C (0.379), A613T (0.393), Q30P (0.412), P1021L (0.427), I601F (0.490), I148N (0.495), N1088D (0.499), I506L (0.507), Q359R (0.510), H139L (0.541), V1240G (0.564).

These 12 are CFTR2-confirmed CF-causing variants that AlphaMissense classified as ambiguous. Any "rescue" finding for these variants from Phase 2 is circular: they are already known to cause disease.

**Accurate description:** The 1,278 are the AM-ambiguous subset of all theoretically possible CFTR missense single-nucleotide variants. 74.8% have never been observed in any patient in this cohort. ClinVar status is unknown for all but a small fraction.

**RETRACTED (2026-08-02, Check 4):** The sentence "None have gnomAD population frequency data" was an unsourced assertion with no generating code. It is withdrawn. Computed result from gnomAD v4 (gnomad_r4, GRCh38, position-matched): **291 of 1,278 have gnomAD AF > 0**; 952 are absent from gnomAD v4 entirely. See `results/gnomad_cftr_lookup.csv` (1,279 lines including header). The prior assertion that the 1,278 are all unobserved is false.

**Inaccurate descriptions in docs (do not edit yet — listed for correction decision):**
- `docs/alphagenome_batch_report.md:90`: "Full 1,278 Ambiguous VUS" — VUS implies clinical observation; 74.8% have no observation record
- `docs/alphagenome_batch_report.md:143`: "strongest candidates for reclassification from VUS to likely pathogenic" — reclassification requires prior clinical submission; most have none
- `docs/comparator_analysis_report.md:3`: "1,278 ambiguous-class CFTR missense variants (AlphaMissense score 0.34–0.564)" — **ACCURATE**, no ClinVar/VUS language here
- `scripts/alphagenome_full_cftr.py:62`: comment "Ambiguous (VUS-equivalent) variants" — developer shorthand, origin of the VUS language

---

## Source pipeline divergence: the 7 and the 1,278

Both populations start from `data/cftr_alphamissense.tsv`.

| | 7 priority variants | 1,278 AM-ambiguous |
|---|---|---|
| AM class filter | `am_class == 'likely_pathogenic'` (score > 0.564) | `am_class == 'ambiguous'` (score 0.34–0.564) |
| Additional filter | Cross-reference with ClinVar VEP VCF: only those with 1KG AF > 0 in CSQ field 34 (mislabelled "gnomAD" in docs; see Check 4) | None |
| AM score range | 0.651–0.976 | 0.340–0.564 |
| Overlap | Zero — disjoint by AM class | — |
| Fraction observed in VCF | 7/7 (100%; that is the selection criterion) | 322/1,278 (25.2%) |

The 7 are the subset of likely-pathogenic CFTR AM variants that have been observed in the general population (gnomAD AF > 0). The 1,278 are all AM-ambiguous CFTR variants, including theoretical ones never observed. They answer different questions and share no variants.

**Text implying the 1,278 is a scale-up of the 7** (file and line; do not edit yet):
- `docs/alphagenome_batch_report.md:90`: Section heading "Rescue Variant Analysis (Full 1,278 Ambiguous VUS)" placed directly after the 7-variant analysis, with no statement that the populations are disjoint or drawn from different AM classes.
