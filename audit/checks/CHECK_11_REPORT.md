# Check 11 Report
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**No git operations. Part B locked.**

---

## What I could not establish

Nothing material is blocked. All computations completed.

---

## 11a — Group structure

From `results/alphagenome/alphagenome_full_cftr_results.csv`:

```
Total rows: 1,278
Groups (protein_variant with 2+ distinct variant_ids): 145
  Size 2: 112 groups
  Size 3:  33 groups
Total variants in groups: 323
```

**Distance check:** All 145 groups have all members within ≤10 bp of each other. Zero groups flagged as potentially not same-codon. All 145 are included.

---

## 11b — AM scores within groups

AM scores are **identical within every group** — 0 groups show any within-group difference. Confirmed by construction: AlphaMissense scores the amino acid change, not the nucleotide.

---

## 11c — Within-group divergence

For each group: maximum pairwise absolute difference across all members.

| Tool | Scores | Median | IQR | Max | >0.1 | >0.3 | >0.5 |
|---|---|---|---|---|---|---|---|
| AlphaMissense | amino acid | 0.0000 | [0.00, 0.00] | 0.0000 | 0 | 0 | 0 |
| CADD PHRED | nucleotide | 0.2700 | [0.10, 0.90] | 8.0940 | 109/145 | 70/145 | 52/145 |
| SpliceAI max delta | nucleotide | 0.0100 | [0.00, 0.05] | 0.7300 | 16/145 | 3/145 | 1/145 |
| AlphaGenome ATAC q | nucleotide | 0.0000 | [0.00, 0.062] | 0.5671 | 30/145 | 12/145 | 4/145 |
| AlphaGenome splice q | nucleotide | 0.0000 | [0.00, 0.003] | 0.2343 | 11/145 | 0/145 | 0/145 |
| AlphaGenome RNA q | nucleotide | 0.0000 | [0.00, 0.004] | 0.0947 | 0/145 | 0/145 | 0/145 |

Top 10 groups by splice-quantile divergence: in `docs/synonymous_codon_analysis.md`.

---

## 11d — Null comparison

**n_perm = 20,000.**

Null 1 — random pairs from 1,278.  
Null 2 — proximity-matched pairs (≤5 bp, different amino acid change): 2,245 pairs.

| Metric | Obs median | Rand null median | p (obs ≤ rand) | Prox null median | p (obs ≤ prox) |
|---|---|---|---|---|---|
| AlphaGenome splice q | 0.0000 | 0.0485 | <0.0001 | 0.0324 | <0.0001 |
| AlphaGenome ATAC q | 0.0000 | 0.2516 | <0.0001 | 0.1671 | <0.0001 |
| CADD PHRED | 0.2700 | 2.6000 | — | — | — |
| SpliceAI max delta | 0.0100 | 0.0100 | ≈1.0 | — | — |

**AlphaGenome splice and ATAC:** significantly more concordant within same-amino-acid groups than proximity-matched random pairs (p<0.0001). The within-group constraint exceeds what proximity alone predicts.

**SpliceAI:** observed and null medians are identical. Within-group pairs are **not** more similar than random for SpliceAI. SpliceAI is highly sensitive to the specific base changed — mechanistically expected, not a model failure. Example: H620Q at position 117592027, T>G gives SpliceAI=0.73, T>A gives SpliceAI=0.00.

**Bounded conclusion:** AlphaGenome splice and ATAC outputs are constrained within same-amino-acid groups beyond general proximity effects. This demonstrates information content. It does not establish correctness.

---

## 11e — Cross-boundary discordance

**693 group membership:**

| Membership | Groups |
|---|---|
| Both members in 693 (splice_q>0.95 AND SpliceAI<0.2) | 82 |
| Exactly one member in 693 | 19 |
| Neither in 693 | 44 |

19 groups are split at the 693 boundary. Two variants producing the same amino acid change receive opposite regulatory calls.

**Groups split by splice_q > 0.95:** 15 groups.  
**Groups split by SpliceAI > 0.2:** 8 groups.

Selected split cases:

```
T604S (AM=0.507):
  chr7:117591978:C>G  splice_q=0.9992  SpliceAI=0.14  IN_693
  chr7:117591977:A>T  splice_q=0.8435  SpliceAI=0.00  not in 693
  (1 bp apart; same amino acid; opposite splice_q threshold calls)

H620Q (AM=0.417):
  chr7:117592027:T>G  splice_q=0.9999  SpliceAI=0.73  (not in 693: SpliceAI > 0.2)
  chr7:117592027:T>A  splice_q=0.9999  SpliceAI=0.00  IN_693
  (same position; SpliceAI differs by 0.73; AlphaGenome identical)

K857N (AM=0.349):
  chr7:117595010:G>T  splice_q=0.9988  SpliceAI=0.40  (not in 693: SpliceAI > 0.2)
  chr7:117595010:G>C  splice_q=0.8863  SpliceAI=0.02  not in 693
  (same position; opposite splice_q threshold; SpliceAI splits >0.2 boundary)
```

---

## 11f — Written up

Full analysis is in `docs/synonymous_codon_analysis.md`. The null comparison precedes the interpretation. The document states explicitly that divergence shows the models differ, not that AlphaGenome is correct.

---

## 11g — n behind AUC 0.946

All four cohort definitions, computed from `results/phase1/benchmark_cohort.csv`:

| Cohort | n | CF | Non-CF | AM AUC | AM AP |
|---|---|---|---|---|---|
| Published, all rows | 292 | 253 | 39 | 0.9459 | 0.9906 |
| Published, CADD-complete | 286 | 247 | 39 | 0.9461 | 0.9905 |
| Deduplicated, all | 259 | 226 | 33 | 0.9549 | 0.9924 |
| Deduplicated, CADD-complete | 254 | 221 | 33 | 0.9548 | 0.9923 |

**Both published figures (n=292 and n=286) round to 0.946.** They are consistent with each other.

**Correct headline for AlphaMissense alone:** n=292, AUC=0.9459 (rounds to 0.946). Source: `results/phase1/benchmark_cohort.csv`, all rows with AM scores. The six variants excluded for missing CADD do have AM scores and belong in the AM-only evaluation.

**Correct headline for four-way comparison (AM + CADD + PolyPhen + SIFT):** n=286, AUC=0.9461 (rounds to 0.946). Source: same file, `included==True` rows only.

**In published claims:** both C03/C04 (README lines 13/39: "AUC 0.946 on 292 labelled CFTR variants") and C10 (README line 52: table entry "0.946" for AM in the 286-variant comparison) are computed from these populations respectively and are consistent. Neither claim is wrong.

**Deduplicated figures:** AUC rises to 0.9549 (n=259) or 0.9548 (n=254). The published figure understates the deduplicated result by 0.009. The direction is: published is lower than correct.

---

## 11h — Source of "ClinVar Feb 2025" and "VEP v115.1"

### Check 4 was wrong

Check 4 reported: "No VEP command exists anywhere in the repository. The flags `--af`, `--af_gnomad` etc. are unknown and unrecoverable."

**This was incorrect.** The VEP command and all flags are present in the VCF file header. Check 4 searched repository files for VEP invocation text but did not grep the VCF header for `##VEP` lines.

### Source of claims: VCF header (verbatim)

```
##fileDate=2026-04-15
##source=ClinVar
##reference=GRCh38
##bcftools_viewVersion=1.23.1+htslib-1.23.1
##bcftools_viewCommand=view -r 7:117480000-117670000 -Oz -o cftr.clinvar.vcf.gz clinvar.vcf.gz; Date=Tue Apr 21 14:08:57 2026
##bcftools_normVersion=1.23.1+htslib-1.23.1
##bcftools_normCommand=norm -f Homo_sapiens.GRCh38.dna.chromosome.7.fa -m -both -Oz -o clinvar.norm.vcf.gz cftr.clinvar.vcf.gz; Date=Tue Apr 21 14:12:13 2026
##VEP="v115.1" API="v115" time="2026-04-30 12:33:47" cache="/nfs/.../homo_sapiens/115_GRCh38" db="homo_sapiens_core_115_38@..." 1000genomes="phase3" COSMIC="101" ClinVar="202502" HGMD-PUBLIC="20204" assembly="GRCh38.p14" dbSNP="156" gencode="GENCODE 49" genebuild="GENCODE49" gnomADe="v4.1" gnomADg="v4.1" polyphen="2.2.3" regbuild="1.0" sift="6.2.1"
##VEP-command-line='vep --af --appris --biotype --buffer_size 500 --cache --check_existing --database 0 --dir [PATH]/cache --dir_plugins [PATH]/VEP_plugins --distance 5000 --fasta_dir [PATH]/fasta --force --fork 4 --hgvs --input_file [PATH]/clinvar.norm.vcf --mane --output_file [PATH]/output.vcf --pick --polyphen b --protein --pubmed --quiet --regulatory --safe --show_ref_allele --sift b --stats_text --symbol --transcript_version --tsl --uploaded_allele --vcf'
```

Verified present in `data/All_Variants_VEP.Gene.vcf` via:
```
$ grep "##VEP\|##bcftools\|##fileDate\|##source\|##reference" data/All_Variants_VEP.Gene.vcf
```

### What each claim is sourced from

**"ClinVar Feb 2025":** read from `ClinVar="202502"` in `##VEP=` header line. `202502` = NCBI ClinVar build 202502 = February 2025. This is in the VCF file.

**"VEP v115.1":** read from `##VEP="v115.1"` in VCF file.

**"GRCh38.p14":** from `assembly="GRCh38.p14"` in `##VEP=` line.

**"Ensembl 115":** from `gencode="GENCODE 49" genebuild="GENCODE49"` and cache path ending `115_GRCh38`.

**Both claims were read from the VCF header, not inferred.** AUDIT_REPORT.md:146–147 quoted these lines; they are present verbatim in the file.

### VEP flags in header

The full VEP command line is in `##VEP-command-line`. Flags relevant to frequency and annotation:

- `--af` — adds 1000 Genomes Phase 3 global AF to CSQ field (this is the `AF` field at CSQ index 34, confirmed by Check 4 to be AF_TGP)
- `--check_existing` — checks against existing variants; required for `--af`
- `--polyphen b` — adds PolyPhen-2 scores (CSQ index 32)
- `--sift b` — adds SIFT scores (CSQ index 31)
- `--regulatory` — adds regulatory feature annotations
- `--pubmed` — adds PubMed citations

**No `--af_gnomad`, `--af_gnomade`, `--af_gnomadg`, or `--max_af` flags.** gnomAD v4.1 is referenced in the VEP cache metadata (`gnomADe="v4.1" gnomADg="v4.1"`) but gnomAD-specific AF fields were not requested. The AF at CSQ index 34 is 1000 Genomes only, consistent with Check 4's finding.

**Check 4's conclusion that "flags unknown" is hereby retracted.** The correct statement is: "All VEP flags are recorded in `##VEP-command-line` in the VCF header. gnomAD-specific AF flags were not used. The AF field is 1000 Genomes Phase 3 via `--af`."

### Reproducibility

The pipeline is fully documented in the VCF header and recoverable:
1. Download ClinVar CFTR region (Feb 2025 snapshot, build 202502)
2. `bcftools view -r 7:117480000-117670000`
3. `bcftools norm -f Homo_sapiens.GRCh38.dna.chromosome.7.fa -m -both`
4. VEP v115.1 with the flags in `##VEP-command-line` (paths to local cache redacted; substitutable)

---

## 11i — data/ gitignore and file listing

`.gitignore` entry that excludes `data/`:

```
# input data — not committed (private/large)
data/All_Variants_VEP.Gene.vcf
data/AlphaMissense_hg38.tsv.gz

# downloaded and generated files
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

`data/` directory is not excluded as a glob pattern — every file is listed individually.

All files in `data/` with sizes:

```
$ ls -la data/
-rw-r--r--@  1 roshani  staff    5,368,289  May  1 16:51  All_Variants_VEP.Gene.vcf
-rw-r--r--@  1 roshani  staff  642,961,469  May 14 16:32  AlphaMissense_hg38.tsv.gz
-rw-r--r--@  1 roshani  staff      113,144  May 14 16:43  cftr2_results.csv
-rw-r--r--@  1 roshani  staff      221,714  May 14 18:48  cftr2_results_annotated.csv
-rw-r--r--@  1 roshani  staff      353,148  May 14 16:20  cftr2_variants.xlsx
-rw-r--r--@  1 roshani  staff      757,186  May 14 18:47  cftr_alphamissense.tsv
-rw-r--r--@  1 roshani  staff       31,042  May 14 19:30  flagged_prioritised.csv
-rw-r--r--@  1 roshani  staff       31,042  May 14 18:55  flagged_unclassified.csv
-rw-r--r--@  1 roshani  staff       10,035  May 14 20:11  nonsense_variants_cftr2.csv
-rw-r--r--@  1 roshani  staff          253  May 14 19:32  priority_candidates.csv
-rw-r--r--@  1 roshani  staff          692  May 14 19:59  priority_candidates_clinvar.csv
-rw-r--r--@  1 roshani  staff        2,357  May 14 19:33  varying_consequence_am.csv
```

Total: 12 files. `AlphaMissense_hg38.tsv.gz` (643 MB) is the only file that would be impractical to commit. All others are small enough to version. Decision is yours.
