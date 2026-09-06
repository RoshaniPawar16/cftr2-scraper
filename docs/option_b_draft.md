# Option B: Results and Methods Draft

*All numeric claims carry source-file annotations in HTML comments. Strip before submission.*

---

## Methods

### Data sources

**GWAS summary statistics.** Re-imputed meta-analysis summary statistics for five cystic fibrosis lung-disease severity modifier loci were obtained from the danghunccf/CF-GWAS-dataMiningPaper repository (commit eba42429968b9c088b07c598c44bc7e9f837b0b4, cloned 2026-08-02). <!-- audit/gwas_provenance.md --> The original genome-wide association study is Corvol et al. (2015; Nat Commun 6:8382; DOI: 10.1038/ncomms9382). The re-imputation is attributed to Panjwani et al. (2018; NPJ Genom Med 3:8; DOI: 10.1038/s41525-018-0047-6). These summary statistics are not the Corvol published values; both citations are required. The five loci are 3q29 (MUC4/MUC20, chr3), 5p15 (SLC9A3, chr5), 6p21 (HLA-DRA, chr6), 11p13 (EHF/APIP, chr11), and Xq23 (AGTR2/SLC6A14, chrX). A sixth locus present in the source file (chr16) was excluded as it does not correspond to any published Corvol locus and was not taken forward. <!-- results/gwas_modifiers/B1_REPORT.md, Step 2 -->

**Imputation quality limitation.** The Panjwani et al. (2018) method paper describes a chromosome-7-only imputation procedure covering the CFTR locus. The imputation procedure, reference panel, and quality thresholds for the remaining four loci (chrX, chr3, chr5, chr6, chr11) are not documented in any available source. No imputation quality metric (INFO score or r²) is released with these summary statistics. The Corvol lead SNP at 6p21, rs116003090, is absent from this re-imputation; no summary statistics exist for it in these files. <!-- audit/gwas_provenance.md; results/gwas_modifiers/B1_REPORT.md, Step 2, rs116003090 note -->

**DNase hypersensitive sites.** Twelve DHS elements mapped in primary human tracheal epithelium were obtained from Stolzenburg et al. (2017; Nucleic Acids Res 45:8773–8784; GSE52179). <!-- results/gwas_modifiers/B2b_tiling_scores_PROVENANCE.md, Source: DHS elements --> Of the twelve, two are luciferase-confirmed strong enhancers (chr11.2516, DNase peak score 615; chr11.2521, DNase peak score 970), one is luciferase-confirmed with no detectable enhancer activity (chr11.2525, DNase peak score 579), one is a luciferase-confirmed weak enhancer (chr11.2526, DNase peak score 577), and eight are uncharacterised. DHS element coordinates were lifted from hg19 to hg38 prior to scoring.

**AlphaGenome version and calibration.** All scoring used AlphaGenome v0.6.1 with the genome-wide quantile calibration introduced on 18 June 2026. Scoring date for all 574 variant–tissue pairs: 2026-08-04. <!-- results/gwas_modifiers/B2c_summary.csv, ag_version column; results/gwas_modifiers/B2_scored_variants.csv, ag_calibration and ag_run_date columns; results/gwas_modifiers/B2b_tiling_scores_PROVENANCE.md, Determinism re-score section -->

---

### Liftover procedure

The pre-extracted peaks file (`gwasImpute2_hg19_SAKNORM_all_meta_fixed_chrPeaks1mb.txt`) yielded 54,853 variants across the five loci (counts verified against specification). <!-- results/gwas_modifiers/B1_REPORT.md, Step 2 --> Liftover from hg19 to hg38 was performed by two independent routes.

**Route A: UCSC chain.** Coordinates were converted using the UCSC hg19ToHg38 chain file via pyliftover. Of 54,853 variants, 206 failed due to chain gaps: 47 variants in the MUC4 variable-number tandem repeat region (chr3:195,181,736–195,264,241 hg19), 13 SNVs near the chr5 telomere (chr5:18,146–44,430 hg19), and 138 SNVs plus 8 indels in the AGTR2/SLC6A14 region (chrX:114,561,730–116,310,686 hg19), where structural differences between hg19 and hg38 are well documented. <!-- results/gwas_modifiers/B1_REPORT.md, Step 3, Route A -->

**Route B: Ensembl/dbSNP rsID lookup.** For variants carrying a single clean rsID (n = 52,252), hg38 positions were obtained by batch POST to the Ensembl REST API (rest.ensembl.org/variation/homo_sapiens; 200 rsIDs per request, 10 concurrent workers). Of 52,252 queried, 52,061 returned positions; 191 were absent (160 indels, 31 SNVs). <!-- results/gwas_modifiers/B1_REPORT.md, Step 3, Route B -->

**Route comparison.** Comparison was restricted to the 51,870 variants where both routes returned a result. Of 2,139 disagreements, 2,097 involve indels with a one-position offset, reflecting the systematic difference between VCF anchor-base and dbSNP first-variant-base coordinate conventions and not true positional discordance. The 33 genuine SNV discordances cluster in the MUC4 region (chr3:~195.5 Mb hg19) and the AGTR2 region (chrX:~114.6 Mb hg19), consistent with local assembly differences between builds. Two rsIDs show positions that have been remapped or merged in dbSNP between the source hg19 assignment and the current hg38 assignment. <!-- results/gwas_modifiers/B1_REPORT.md, Step 3, Disagree breakdown table -->

---

### Variant filter and genome-wide-significant set

**Clean SNV filter.** Three criteria were applied jointly: (i) `is_snv = YES` (len(REF) = 1 and len(ALT) = 1); (ii) `a_ok = YES` (Route A succeeded); (iii) `routes_agree ∈ {YES, NA}`, where NA indicates no clean rsID was available for Route B lookup and therefore represents the absence of a conflict, not a confirmed conflict. This yielded **49,930 clean SNVs** across the five loci. <!-- results/gwas_modifiers/B1_lifted_hg38.csv.gz; results/gwas_modifiers/B1_REPORT.md, Step 5 and clean SNV exclusion arithmetic -->

Note: the `routes_agree` column encodes the value `'NA'` as a literal string for variants without a clean rsID. Default pandas CSV-reading coerces this to `NaN`; all analyses used `keep_default_na=False` to prevent silent row loss. <!-- results/gwas_modifiers/B2b_tiling_scores_PROVENANCE.md, Bug note -->

**Genome-wide significance.** Variants were classified as genome-wide significant at p.fix < 5 × 10⁻⁸. Before artefact exclusion, 558 GWS SNVs were identified across the five loci. <!-- results/gwas_modifiers/B1_lifted_hg38.csv.gz -->

**Artefact exclusion.** Ten variants absent from both gnomAD v3 and gnomAD v4 were excluded: eight from 5p15 and two from 6p21 (rs28366348, rs28366349). <!-- results/gwas_modifiers/B1_gnomad_absent_nonsex_loci.csv --> Seven of the eight excluded 5p15 variants fall within a 21-bp window at adjacent positions with identical minor allele frequency at neighbouring bases; the cause of their absence from gnomAD is not established from available data and may reflect imputation artefact. After exclusion, **548 GWS SNVs** were taken forward. <!-- results/gwas_modifiers/B1_gnomad_absent_nonsex_loci.csv, absence_cause column -->

**REF/ALT orientation.** Of the 49,930 clean SNVs, 459 have ALT coded as the hg38 reference allele (orientation = ALT_as_hg38ref); an additional 117 are ALT_as_hg38ref and palindromic. (618 and 150 are the counts for all rows with Ensembl data, n = 49,942, per `results/gwas_modifiers/B1_REPORT.md` Step 4; 459 and 117 are the counts within the clean-SNV filter.) Beta sign reversal is required for these variants before any directional analysis. No directional analysis was performed in this work. <!-- results/gwas_modifiers/B1_REPORT.md, Step 4 -->

---

### Scorer and aggregation

The chromatin disruption scorer was CenterMaskScorer(ATAC, window=501, metric=L2_DIFF), AlphaGenome v0.6.1. <!-- results/gwas_modifiers/B2_scored_variants.csv, ag_scorer_chromatin column --> L2_DIFF computes the Euclidean distance between the reference and alternate predicted ATAC accessibility profiles across a 501-bp window centred on the variant. This quantity is unsigned by construction: the scorer does not distinguish between predicted increases and predicted decreases in chromatin accessibility, and the direction of effect is not derivable from this output. Unsigned magnitude was chosen following the rationale applied in Borzoi fine-mapping applications, in which both disruption and creation of accessibility can represent a regulatory event.

No quantile scores are available for CenterMaskScorer(L2_DIFF). All within-cohort comparisons use raw L2_DIFF values. No claim is made about the rank of any variant against a reference population.

A total of **574 variant–tissue pairs** were scored: <!-- results/gwas_modifiers/B2_scored_variants.csv, row count --> 24 GWS variants at 3q29 in lung (UBERON:0002048), 24 at 3q29 in esophagus mucosa (UBERON:0006920), 203 at 5p15 in lung, 28 at 6p21 in B lymphocytes (CL:0000236), 111 at 11p13 in lung, and 184 at Xq23 in lung.

---

### Tissue assignment per locus

No airway epithelium ontology exists in AlphaGenome v0.6.1. Cystic fibrosis lung-disease severity is a disease of the airway epithelium; the closest available proxy in the AlphaGenome track library is lung bulk tissue. This represents an unvalidated tissue substitution for four of the five loci. The analogous limitation — approximating a cell-type-specific regulatory programme with the nearest available bulk tissue — has been noted in applications of sequence-to-expression models to neurodegeneration.

**Lung (UBERON:0002048)** was used as the primary tissue for 3q29 (MUC4/MUC20), 5p15 (SLC9A3), 11p13 (EHF/APIP), and Xq23 (AGTR2/SLC6A14). Esophagus mucosa (UBERON:0006920) was scored as a secondary tissue for 3q29 only. <!-- results/gwas_modifiers/B2_scored_variants.csv, ag_tissue column -->

**B lymphocytes (CL:0000236)** were used for 6p21. The 6p21 association signal resides in the HLA class II region. HLA class II genes are expressed on professional antigen-presenting cells — B lymphocytes, dendritic cells, and macrophages — and are not expressed at meaningful levels in structural airway epithelial cells. Applying a lung bulk-tissue ATAC track to the HLA-DRA locus would assess chromatin disruption in a cell type where the relevant regulatory circuitry is not active. B lymphocytes were selected as the most appropriate available tissue for this locus. This choice is a deliberate departure from disease-tissue matching and has a direct consequence: raw ATAC L2_DIFF scores at 6p21 are not directly comparable to scores at the four lung-scored loci. Comparisons between 6p21 and any other locus using these raw values are not supported. <!-- results/gwas_modifiers/B2_scored_variants.csv, ag_tissue = CL:0000236 for locus 6p21 -->

---

### Splice distance gate

Distances from each GWS variant to the nearest annotated splice site were computed against Ensembl release 116 annotations. A variant was classified as within splice-interpretable distance (`splice_near_transcript = True`) if it fell within 500 bp of a splice site residing within an annotated transcript. <!-- results/gwas_modifiers/B2_splice_distances.csv, splice_near_transcript and dist_to_nearest_splice columns -->

Of the 550 scored GWS variants, **471 (85.6%) lie beyond 500 bp of any annotated exon boundary** and fall outside the splice-interpretable window. <!-- results/gwas_modifiers/B2_splice_distances.csv recomputed against results/gwas_modifiers/B2_scored_variants.csv; per-locus sub-counts verify exactly: 3q29 13/24, 5p15 60/203, 6p21 0/28 --> An earlier version of this analysis reported 403 of 548; this figure could not be reproduced from `B2_splice_distances.csv` and `B2_scored_variants.csv` and has been replaced by the recomputed value throughout.

---

### Control matching design (B2c)

For each of the five loci, genome-wide-significant variants were compared against a 1:1 matched control set sampled by stratified sampling within distance-to-nearest-gene strata. Controls were scored in the same tissue as the corresponding GWS set (lung for 3q29, 5p15, 11p13, and Xq23; B lymphocytes for 6p21). The 3q29 control set is in `B2c_3q29_lung_scores.csv` (tissue UBERON:0002048, n = 24); control sets for the remaining four loci are in `B2c_control_scores.csv`. <!-- results/gwas_modifiers/B2c_summary.csv; results/gwas_modifiers/B2c_3q29_lung_scores.csv; results/gwas_modifiers/B2c_control_scores.csv -->

Statistical comparison used the two-sided Mann–Whitney U test. Effect size is expressed as the rank-biserial correlation coefficient r = 2U / (n₁n₂) − 1, where U is the Mann–Whitney statistic for the GWS group against the control group and n₁, n₂ are the respective sample sizes. A negative rank-biserial indicates that GWS variants tend to score lower than their matched controls; a value of zero indicates no tendency. Medians are reported as the primary summary statistic. Means are not reported because two control outliers at 6p21 (described below) distort locus-level means substantially.

---

### In silico tiling design (B2b)

CenterMaskScorer(ATAC, window=501, metric=L2_DIFF) was applied to all non-reference single-nucleotide substitutions at 150 unique positions (25-bp step) tiled across the 12 DHS elements from Stolzenburg et al. 2017, yielding 450 scored DHS substitutions. <!-- results/gwas_modifiers/B2b_tiling_scores.csv, dhs rows: 150 unique (chrom, pos) × 3 alt substitutions = 450 rows -->

Control positions (143 unique genomic positions, 450 scored substitutions) were selected from intervals containing no annotated DHS element. <!-- results/gwas_modifiers/B2b_tiling_scores.csv, control rows: 143 unique (chrom, pos), 450 rows total (136 positions with 3 substitutions; 7 positions with 6 substitutions, cause not determined from available files) --> Per-element summary statistics use the median of all scored substitutions within that element. Element-level medians are the primary unit; means are not reported.

**Reproducibility note.** The control position selection procedure was written inline during an earlier working session and is not available as committed code. The 143 control positions are hardcoded from the original output in `scripts/b2b_tiling.py`; the script reconstructs the DHS tiling only. All 20 positions tested in a determinism re-score on 2026-08-04 reproduced to floating-point precision (maximum |original − re-score| = 1.11 × 10⁻¹⁶); the original API run date is unrecoverable (best lower bound: 2026-08-03, from adjacent checkpoint file timestamps). <!-- results/gwas_modifiers/B2b_tiling_scores_PROVENANCE.md, Determinism re-score and Run date recovery sections -->

---

### Reproducibility hazards

**Calibration change.** AlphaGenome updated its quantile calibration from a chromosome-22-only background to a genome-wide background on 18 June 2026. All scoring in this project used the post-update calibration. An earlier project run (28 May 2026) used the chromosome-22-only calibration; quantile scores from that run shift by up to 0.39 relative to genome-wide recalibration with raw scores unchanged. The B2 and B2b analyses reported here use only raw L2_DIFF and are therefore unaffected by this calibration difference. <!-- docs/AUDIT_RECORD.md, Calibration background section -->

**Raw-score instability.** Comparison of AlphaGenome scoring runs from 28 May 2026 and 2 August 2026 on an identical input set (same 1,278 CFTR variants, same version, same tracks) revealed that 75 variants returned different raw scores. No changelog entry documents a change between these dates. A determinism rerun at seven-day separation is scheduled for 2026-08-09. <!-- docs/AUDIT_RECORD.md, What the audit found section -->

---

## Results

Results are presented in the following order. Finding 1 characterises what the model can detect (open chromatin positions above background), establishing the operating range within which all subsequent comparisons are made. Finding 2 characterises where the model's discrimination ends (it cannot rank elements by measured enhancer activity), providing context for interpretation of the GWAS comparison. Finding 3 reports the central biological question (whether the association signal concentrates at predicted regulatory positions). Finding 4 provides the genomic context that limits splice-based interpretation of the same variants. Finding 5 records the methodological hazards that qualify findings 1–4.

---

### 1. Predicted chromatin disruption separates DHS element positions from matched background

Across 12 DNase hypersensitive sites mapped in primary tracheal epithelium (Stolzenburg et al. 2017; GSE52179), predicted ATAC disruption separated element positions from matched non-DHS background. The maximum raw L2_DIFF among 450 scored control substitutions was 0.3513 (control median 0.0740, n = 450). <!-- results/gwas_modifiers/B2b_tiling_scores.csv, control rows: ctrl.max() = 0.3513, ctrl.median() = 0.0740 --> Nine of 12 element-level medians exceeded this value; three did not. <!-- results/gwas_modifiers/B2b_tiling_scores.csv, dhs rows, per-element medians; 9 of 12 exceed ctrl.max() --> The three elements below the control maximum were chr11.2522 (uncharacterised, median 0.1339), chr11.2524 (uncharacterised, median 0.2120), and chr11.2525 (median 0.3370). <!-- results/gwas_modifiers/B2b_tiling_scores.csv, element medians --> chr11.2525 is the luciferase-confirmed no-activity element from Stolzenburg et al. 2017; its median falls below the control maximum, consistent with the experimental characterisation. The adjacent element chr11.2517, whose regulatory activity is uncharacterised, scores just above the control threshold (median 0.3700). <!-- results/gwas_modifiers/B2b_tiling_scores.csv, elements chr11.2525 and chr11.2517 -->

---

### 2. Predicted disruption does not track measured enhancer activity

Among the nine elements that exceeded the control maximum, predicted disruption did not track the Stolzenburg et al. (2017) DNase peak signal or luciferase-measured enhancer strength. Four uncharacterised elements (chr11.2519, chr11.2523, chr11.2520, chr11.2518, medians 2.195, 1.280, 1.103, 1.069 respectively) scored above both luciferase-confirmed strong enhancers. <!-- results/gwas_modifiers/B2b_tiling_scores.csv, uncharacterised element medians vs max strong-enhancer median of 0.9378 --> Among the two strong enhancers, the ordering predicted by AlphaGenome was inverted relative to measured activity: the element with the higher DNase peak score (chr11.2521, DNase peak 970, corresponding to the 40–50× luciferase activity class; Stolzenburg et al. 2017) showed a lower element-level median (0.7254) than the element with the lower DNase peak score (chr11.2516, DNase peak 615, 20–40× luciferase activity class; median 0.9378). <!-- results/gwas_modifiers/B2b_tiling_scores.csv, elements chr11.2521 and chr11.2516 --> Across all 12 elements, element-level median was not correlated with DNase peak score (Spearman ρ = −0.119, p = 0.713, n = 12). <!-- results/gwas_modifiers/B2b_tiling_scores.csv, Spearman computed from per-element median vs dnase_score -->

---

### 3. GW-significant variants show no elevated predicted ATAC disruption against matched controls

At all five loci, the rank-biserial correlation was negative, indicating that GW-significant variants tended to score lower on predicted ATAC disruption than their 1:1 matched controls stratified by distance to nearest gene. <!-- results/gwas_modifiers/B2c_summary.csv; results/gwas_modifiers/B2c_3q29_lung_scores.csv; results/gwas_modifiers/B2_scored_variants.csv --> Results by locus are given in Table 1.

**Table 1.** Predicted ATAC disruption (CenterMaskScorer L2_DIFF, raw) at GW-significant variants versus matched controls, by locus. Medians and rank-biserial correlations are reported; means are not reported (see 6p21 note below). All comparisons are within-locus and within-tissue; the 6p21 values (B lymphocytes) are not comparable to the lung-scored loci.

| Locus | n GWS | GWS median | n ctrl | Ctrl median | Rank-biserial | p (two-sided) |
|---|---|---|---|---|---|---|
| 3q29 | 24 | 0.0799 | 24 | 0.1117 | −0.257 | 0.130 |
| 5p15 | 203 | 0.0970 | 203 | 0.1156 | −0.149 | 0.009 |
| 6p21 | 28 | 0.0379 | 28 | 0.0424 † | −0.281 | 0.073 |
| 11p13 | 111 | 0.0679 | 111 | 0.0777 | −0.151 | 0.052 |
| Xq23 | 184 | 0.0624 | 184 | 0.0670 | −0.024 | 0.697 |

<!-- 3q29: computed from results/gwas_modifiers/B2_scored_variants.csv (ag_tissue=UBERON:0002048) and results/gwas_modifiers/B2c_3q29_lung_scores.csv -->
<!-- 5p15, 6p21, 11p13, Xq23: results/gwas_modifiers/B2c_summary.csv -->

† The 6p21 control distribution contains two extreme outliers: rs974357 (position chr6:32,972,117, 527 kb from nearest gene, raw L2_DIFF 47.756) and rs707916 (position chr6:31,729,781, 710 kb from nearest gene, raw L2_DIFF 26.493), against a GW-significant variant maximum of 0.1726. <!-- results/gwas_modifiers/B2c_control_scores.csv, locus 6p21, rows sorted by atac_l2d_raw descending --> No interpretation of the cause of these scores is offered (see tissue limitation above). Excluding these two control variants, the rank-biserial is −0.225 and p = 0.158 (n_ctrl = 26; U-statistic unchanged at 282 because both outlier scores exceed all 28 GWS values). <!-- computed from results/gwas_modifiers/B2c_control_scores.csv and results/gwas_modifiers/B2_scored_variants.csv, locus 6p21 --> The 6p21 comparison is reported in parallel as −0.281, p = 0.073 with outliers included and −0.225, p = 0.158 with outliers excluded; neither figure is presented in isolation.

Only 5p15 reaches p < 0.05 (p = 0.009). The 11p13 comparison (p = 0.052) falls just outside this threshold.

**rs547504 at 11p13.** Among the 111 GW-significant variants scored at 11p13 in lung tissue, rs547504 (hg38 chr11:34,825,678, MAF 0.36, p.fix = 9.95 × 10⁻⁹) carries the highest raw ATAC L2_DIFF among GW-significant variants at this locus (1.244). <!-- results/gwas_modifiers/B2_scored_variants.csv, locus 11p13, ag_atac_l2d_raw sorted descending --> No fine-mapping was performed, no LD reference matched to the study population is available, and rs547504 is not nominated as a causal variant. Twenty-one GW-significant variants within 50 kb of rs547504 share MAF between 0.359 and 0.368, consistent with tagging a shared haplotype. <!-- results/gwas_modifiers/B2_scored_variants.csv, locus 11p13: variants within 50 kb of pos_hg38=34,825,678 with maf_source in [0.359, 0.368] -->

---

### 4. Most GW-significant variants fall outside splice-interpretable distance from annotated exon boundaries

Of the 550 GW-significant variants scored in B2, **471 (85.6%) lie beyond 500 bp of any annotated exon boundary** and fall outside the window within which AlphaGenome splice predictions can be interpreted against transcript annotation (Ensembl release 116). <!-- results/gwas_modifiers/B2_splice_distances.csv recomputed against results/gwas_modifiers/B2_scored_variants.csv --> The per-locus breakdown is given in Table 2.

**Table 2.** GW-significant variants by splice proximity, per locus.

| Locus | n total | Within 500 bp of exon boundary | Beyond 500 bp |
|---|---|---|---|
| 3q29 | 24 | 13 (54%) | 11 (46%) |
| 5p15 | 203 | 60 (30%) | 143 (70%) |
| 6p21 | 28 | 0 (0%) | 28 (100%) |
| 11p13 | 111 | 2 (2%) | 109 (98%) |
| Xq23 | 184 | 4 (2%) | 180 (98%) |
| **Total** | **550** | **79 (14%)** | **471 (86%)** |

<!-- results/gwas_modifiers/B2_splice_distances.csv, splice_near_transcript and dist_to_nearest_splice columns; per-locus sub-counts verified independently -->

Splice interpretation is substantive only at 3q29 and 5p15, where 54% and 30% of GW-significant variants, respectively, lie within the splice-proximity window. At 11p13 and Xq23, the fractions are 2% each. At 6p21, no GW-significant variant lies within 500 bp of any annotated exon boundary; the association signal at this locus cannot be assessed for splice impact at the variant level with AlphaGenome.

---

### 5. Two reproducibility hazards qualify the preceding results

**Calibration change (18 June 2026).** AlphaGenome updated its quantile calibration from chromosome-22-only to genome-wide on 18 June 2026. The B2 and B2b scoring runs in this analysis used the post-update, genome-wide calibration (all 574 pairs scored 2026-08-04). Because the analyses reported here use raw L2_DIFF scores only, not quantile scores, the calibration change does not alter any numeric result above. For completeness: quantile scores computed under the chromosome-22-only calibration shift by up to 0.39 relative to the genome-wide recalibration, with raw scores unchanged for most variants. <!-- docs/AUDIT_RECORD.md, Calibration background section; results/gwas_modifiers/B2_scored_variants.csv, ag_calibration = genomewide_post_2026-06-18 -->

**Raw-score instability (undated).** Comparison of AlphaGenome scoring runs from 28 May 2026 and 2 August 2026, using identical inputs, revealed that 75 of 1,278 CFTR variants returned different raw scores between runs from the same version with no accompanying changelog entry. The cause is not determinable from available records. A determinism rerun at seven-day separation is scheduled for 2026-08-09; this note will be updated when results are available. The 550 GW-significant GWAS variants reported here were all scored on 2026-08-04 with AlphaGenome v0.6.1 and reproduced exactly on the same date in the determinism check reported in the B2b provenance file; the instability observation derives from the separately conducted CFTR-variant benchmark and is recorded here as a known property of the scoring environment. <!-- docs/AUDIT_RECORD.md, What the audit found; results/gwas_modifiers/B2b_tiling_scores_PROVENANCE.md, Determinism re-score -->
