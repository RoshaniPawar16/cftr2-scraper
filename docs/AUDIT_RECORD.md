# Audit Record

**Branch:** integrity-audit-2026-07  
**Period:** 29 July – 2 August 2026  
**Prepared by:** automated audit agent  

---

## What this was

A systematic check of every quantitative claim in this repository before those numbers enter a manuscript. Twenty-one checks were conducted over five days. The scope was the full working tree on branch `integrity-audit-2026-07` as of 29 July 2026. This was quality control on existing work, not new research: no new experiments were designed and no new hypotheses were generated. Every number was traced to its source file, recomputed independently where possible, and assigned a status: verified, verified-to-rounding, contradicted, no evidence, or not reproducible.

---

## How it was done

A claims ledger (`audit/CLAIMS_LEDGER.csv`) was built by reading every committed document and extracting every quantitative statement — counts, AUCs, p-values, percentages, and descriptive claims about data provenance. Each entry records the claim text, the file and line it appears in, and the file that was supposed to produce it. Claims were then verified by running the cited script, reading the cited result file, or recomputing from primary data. Where computation was not possible, the status is recorded as `no evidence` or `not reproducible` rather than assumed correct.

Final status counts across all entries in the ledger:

| Status | Count |
|---|---|
| VERIFIED | 41 |
| VERIFIED-TO-ROUNDING | 8 |
| CONTRADICTED | 14 |
| CORRECTED | 9 |
| RETRACTED | 7 |
| NO EVIDENCE | 6 |

---

## What was confirmed

The following numbers survived verification and are safe to quote, with their source files:

**AlphaMissense benchmark** (`results/phase1/am_validation_metrics.csv`): AUC 0.9549, AP 0.9924 on n=259 deduplicated CFTR2-labelled variants (253 CF-causing, 6 Non CF-causing). Reproducible from `scripts/phase1_build_cohort.py` and `scripts/phase1_benchmark.py`.

**DeLong pairwise comparisons** (`results/phase1/delong_tests.csv`): AM vs PolyPhen-2 Z=3.18 p=0.0015; AM vs CADD Z=3.57 p=0.0004; AM vs SIFT Z=6.78 p<0.0001. All more significant than previously reported (2.88/0.0040, 3.28/0.0011, 5.87/<0.0001) because the original implementation omitted the covariance term required by the DeLong method. The direction and ranking are unchanged.

**18 concordant variants** (`results/alphagenome/rescore_centermask.csv` × `results/comparator_scores.csv`): Variants with CM splice 501 in the top 5% of the 1,278 cohort AND SpliceAI delta > 0.5. Count is 13 at the highest-confidence definition and 18 at the original GM quantile definition; both are confirmed. OR = 13.1–129 depending on definition; all p < 0.001.

**CFTR2 snapshot** (`audit/PROVENANCE.md`): The CFTR2 database used was the 30 January 2026 release, downloaded directly from cftr2.org. This is confirmed from file metadata and download logs. 2,092 variants across 122,935 patients.

**VEP command** (`data/All_Variants_VEP.Gene.vcf` header): VEP v115.1, ClinVar 202502. The annotation command is preserved in the VCF header; the input was a ClinVar variant file, not a patient cohort VCF.

**Domain distribution** (`results/phase1/am_domain_analysis.csv`): 73% of likely-pathogenic calls within varying-clinical-consequence variants fall in MSD1 or MSD2. Verified by residue-to-domain mapping against published CFTR domain boundaries.

**Codon-pair result** (`docs/synonymous_codon_analysis.md`): AlphaGenome splice and ATAC quantiles are significantly more concordant within same-amino-acid groups (two SNVs producing the same substitution) than within proximity-matched different-amino-acid groups (p < 0.0001 for both modalities). This is a controlled test of base-level sensitivity requiring no external ground truth.

**Quantization finding** (`results/alphagenome/alphagenome_full_cftr_results.csv`): `GeneMaskSplicingScorer` returns 87 unique values across 1,278 CFTR variants, all multiples of 1/256. The raw column is quantized; the quantile column derived from it has 290 unique values. This is a property of the scorer, not of the data.

---

## What was corrected

**AUC 0.946 → 0.9549; n=292 → n=259.**  
Cause: a one-to-many merge on protein variant name introduced 33 duplicate rows. Every duplicated row carries identical values; no scores were altered, only row counts. After deduplication, AP rises slightly (0.990 → 0.9924). Every file that reports 0.946 or n=292 requires updating. Affected files: `docs/REPORT.md`, `README.md`, `audit/AUDIT_REPORT.md`, all CLAIMS_LEDGER entries for those values.

**DeLong statistics.**  
Cause: the original implementation omitted the covariance term required by the DeLong (1988) method. All pairwise Z-statistics increase and all p-values decrease. The corrected values are in `results/phase1/delong_tests.csv`. The original values should not appear in a manuscript.

**1000 Genomes described as gnomAD.**  
The population frequency column in the VEP-annotated VCF (CSQ field 34 = AF_TGP) is the 1000 Genomes Phase 3 allele frequency. It was described as gnomAD throughout. The seven priority variants are each singletons or doubletons in 2,504 individuals; their frequencies are not comparable to gnomAD observations. Every mention of "gnomAD population frequency" in the context of those seven variants is incorrect.

**ClinVar VCF described as patient cohort.**  
The input VCF (`data/All_Variants_VEP.Gene.vcf`) is a ClinVar annotation file, confirmed from the VEP header. Multiple documents describe it as containing variants "observed in patients" or drawn from clinical sequencing. This is inaccurate.

**Quantile scores described as ranks against all human variants.**  
AlphaGenome's quantile scores rank a variant against the common-variant background (MAF > 0.01 in any gnomAD v3 population), not against all human variation. The phrase "top X% of all human variants" appears in `docs/alphagenome_batch_report.md`, `docs/rescore_analysis.md`, `docs/comparator_analysis_report.md`, and several audit reports. All have been corrected. The corrected description is: "rank within the common-variant background."

**Accuracy and F1 at mismatched threshold.**  
Reported accuracy (0.94) and F1 scores used the published AM threshold of 0.564. MCC was computed at the optimal threshold. These are not comparable without labelling. The AUC and AP figures are threshold-independent and are the primary metrics for all comparisons.

**Calibration background: chromosome 22 → genome-wide.**  
AlphaGenome updated its quantile calibration on 18 June 2026. The project's run dates from 28 May 2026 and used the chromosome-22-only background. Quantile values shift by up to 0.39 with raw scores unchanged for most variants. The original quantiles are preserved in `results/alphagenome/alphagenome_full_cftr_results.csv`; genome-wide recalibration is in `results/alphagenome/quantiles_genomewide_2026-08.csv`. The 58.4% figure and the 693 figure both change under recalibration and belong to the unaffected-1,203 subset for clean comparison.

---

## What was retracted

**The 693 discordant variants.**  
Definition: AlphaGenome SPLICE quantile > 0.95 AND SpliceAI delta < 0.2. Observed 693 against 717 expected under independence (chi-squared p = 0.20). The group is at the chance level. Additionally, the 0.95 threshold clears 58.4% of the cohort because it compares rare coding variants against a common-variant background — the discordant count is the expected consequence of that mismatch, not a finding. The group cannot be presented as evidence of AlphaGenome detecting splice effects invisible to SpliceAI.

**The seven priority variants.**  
Selected on 1000 Genomes allele frequency under the mistaken assumption that the field was gnomAD. All seven are singletons or doubletons in 2,504 individuals (AF ≈ 0.0002–0.0004). Four rank below the 1st percentile of the 1,278 cohort on center-mask rescoring. The selection has no basis in the data as described.

**Every "top X% of all human variants" claim.**  
AlphaGenome quantiles rank against common variants (MAF > 0.01), not all human variation. The comparison population is explicitly defined in the AlphaGenome FAQ. The phrase appeared in multiple documents and has been corrected in all reachable locations.

**The twelve-variant positive control.**  
Twelve CF-causing missense variants were used to test whether AlphaGenome scores are elevated for known pathogenic variants. The result was not significant (p > 0.05) and the confidence interval spanned the full range. Two confounds prevent interpretation: CF-causing missense variants need not act through splicing (the tested mechanism), and the median distance to the nearest splice site was only 58 bp, making the gene-body maximum systematically elevated for the entire control set. The positive control neither confirms nor refutes AlphaGenome's utility.

---

## What the audit found that was not previously known

These are observations about the tools applied in this project, not about CFTR biology.

**GeneMaskSplicingScorer takes a gene-body maximum, not a variant-level maximum.**  
The scorer returns the largest change in splice-site probability at any junction across the full CFTR gene body. For a coding variant, this maximum is set by the nearest canonical splice site, not by the variant's effect on that site. Arg1070Gln — experimentally confirmed as non-splice-altering by minigene assay — scores 0.963 because a canonical splice site sits 69 bp away. This is a documented worked example of the gene-body maximum picking up an uninformative signal. The finding is in `audit/checks/CHECK_15_REPORT.md`.

**The quantile background is common variants, making the threshold near-trivial for coding variants.**  
AlphaGenome quantile scores rank a variant against variants with MAF > 0.01 in gnomAD v3, which are predominantly non-coding. Rare coding variants in a highly-spliced gene routinely exceed the 95th percentile of this background. The 58.4% figure is an expected consequence of using this metric on this cohort, not an anomaly.

**The raw column and quantile column are not monotonically related.**  
`quantile_max` is the maximum of per-track quantile scores across the two lung tracks; `raw_max` is the maximum of per-track raw scores. Because each track has its own calibration CDF (confirmed in source code and AlphaGenome FAQ), the same raw value produces different quantile values on different tracks, and the track that supplies the raw maximum need not be the track that supplies the quantile maximum. The raw column has 87 unique values; the quantile column has 290. Analyses that mix them require care.

**The project's AlphaGenome quantile scores used a chromosome-22-only calibration.**  
AlphaGenome's quantile calibration was updated from chromosome-22-only to genome-wide on 18 June 2026. The project's scoring run predates this. Raw scores are stable over short intervals (two runs six minutes apart agree exactly); stability over a seven-day interval has not been tested. Additionally, 75 of 1,278 variants return different raw scores between the May and August runs with no associated changelog entry; the cause is not determinable from available records. A determinism rerun is due 9 August 2026.

**All 1,278 variants lie within 500 bp of a CFTR splice site.**  
CFTR's 27 exons span 188 kb; there is no coding position more than 500 bp from a splice site. This means SpliceAI's ±50 nt reporting window excludes 41% of the cohort, returning 0.000 for "not assessed" rather than "assessed and negative." SpliceAI cannot serve as a negative ground truth for this subset.

---

## Corrections still outstanding

The following items are identified but not resolved. They are listed here so the next working agent does not need to re-derive them.

**Check 19a operating point comparison.** The false-positive comparison compared scorers at different base rates (58.4% for GM versus 20% for CM). The 67% false-positive figure for GM quantile was at its natural operating point; the CM comparison was at its top-20% definition. A matched-sensitivity comparison is required before any scorer is selected as primary on the experimental benchmark. The current data supports only: "at matched sensitivity, all three AlphaGenome scorers are indistinguishable (AUROC 0.833–0.856, CIs overlapping entirely at n=23)."

**SpliceAI scored only 2 of 23 experimentally validated variants.** The Ensembl VEP REST API returned zero SpliceAI scores for 21 variants. Three hypotheses have not been tested: indel queries against an SNV-only precomputed file, a genome build mismatch, or REST plugin coverage gaps. Until resolved, the SpliceAI AUROC of 0.432 on the experimental benchmark must not appear in any document; it is a coverage artefact.

**Documents still describing the 693 or the seven as findings.** `docs/comparator_analysis_report.md`, `docs/spliceai_coverage_analysis.md`, `docs/tool_association_analysis.md`, and `docs/threshold_sensitivity.md` each discuss the 693 in terms that do not yet reflect the retraction. The seven priority variants appear in `docs/alphagenome_batch_report.md`. These require rewriting, not correction of individual figures.

**Determinism rerun at seven-day separation, due 9 August 2026.** Two scoring runs six minutes apart agreed exactly, establishing that the API is not non-deterministic over short intervals. This is insufficient to establish that the backend changed exactly once (in June) rather than periodically. The script is `scripts/regenerate_quantiles_genomewide.py`; rescore the same ten variants from `/tmp/det_variants.txt` and compare against `results/alphagenome/quantiles_genomewide_2026-08.csv`.

---

## What a fresh reader needs to know

The AlphaMissense benchmark (AUC 0.9549, n=259) is solid and reproducible. The concordant-18 result (OR 13.1–129, p < 0.001) is solid. The quantization finding and the codon-pair result are solid. Everything that relied on the 693 discordant group, the seven priority variants, or the phrase "top X% of all human variants" has been retracted or corrected. The experimental benchmark (23 variants, minigene-validated) is the only point where prediction meets biology; it is thin at n=23 and no scorer can be selected from it, but it is the right question. All evidence lives in `results/`, all corrections in `audit/`, and the navigation is in `audit/checks/INDEX.md`.

---

## What kind of errors these were

The numbers were reliably correct and reproduced from their source files. The descriptions attached to them frequently were not. A 1000 Genomes field was labelled gnomAD, a ClinVar VCF was described as patient cohort data, and a common-variant calibration background was described as all human variants. Every count matched its file. Almost none of the prose describing those counts had been checked before this audit.
