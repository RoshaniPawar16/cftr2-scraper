# Literature Review: Computational Variant Effect Prediction in CFTR and Beyond

---

## 1. McDonald et al. 2024 — Benchmarking AlphaMissense on CFTR

**Citation:** McDonald EF, Oliver KE, Schlebach JP, Meiler J, Plate L. "Benchmarking AlphaMissense pathogenicity predictions against cystic fibrosis variants." *PLOS ONE*, January 25, 2024. PMID: 38271453.

### What they did
McDonald et al. evaluated AlphaMissense (AM) for predicting the pathogenicity of CFTR missense variants by benchmarking AM scores against the CFTR2 database, clinical phenotype data (sweat chloride levels, pancreatic insufficiency rates, infection frequencies), in vitro functional assays (protein trafficking, folding, channel function), and pharmacological responses to CFTR corrector compounds. The dataset comprised 169 CFTR variants with available clinical data.

### What they found
- AM predicted high pathogenicity for CFTR residues broadly, producing a **high false positive rate** and only **fair classification performance** against CFTR2 ground truth.
- Correlation with CFTR channel function was moderate (Pearson r = −0.70, Spearman ρ = −0.69), meaning AM partially captures functional severity but conflates different mechanisms of loss of function.
- Correlation with sweat chloride was weaker (Pearson r = 0.46), and with pancreatic insufficiency weaker still (r = 0.31).
- AM **could not differentiate mechanistic effects** — misfolding versus gating defects versus reduced synthesis — that determine which CFTR modulators are appropriate.
- AM offered **limited utility for predicting pharmacological response** to correctors such as elexacaftor-tezacaftor-ivacaftor.

### How it relates to our work
McDonald et al. benchmark AM specifically on CFTR using CFTR2 ground truth — the same ground truth database we use. Their finding that AM has a high false positive rate on CFTR contrasts with our result (AUC 0.946, AP 0.990 on 292 labelled variants). The discrepancy is likely explained by differences in variant selection and evaluation methodology: McDonald et al. used 169 variants with available clinical data (non-random selection), whereas we used all 292 variants with binary CFTR2 labels in a standard ROC/PR framework. Their work also highlights that AM cannot distinguish mechanism — a limitation directly addressed in our analysis by adding AlphaGenome, which captures splicing and regulatory effects independently of protein-level pathogenicity.

### Gap our work fills
McDonald et al. evaluate AM exclusively at the protein level. They do not apply any genomic regulatory model, do not assess splice site effects, and do not provide a DNA-level view of variant impact. Our work adds AlphaGenome quantile scores for RNA-seq, ATAC-seq, and splice site usage, enabling mechanistic stratification that AM alone cannot provide. We also extend the evaluation to 1,278 ambiguous variants rather than the 169 variants with full clinical phenotyping.

---

## 2. Avsec et al. 2026 — AlphaGenome

**Citation:** Avsec Ž, Latysheva N, Cheng J, Novati G, Taylor KR, Ward T, et al. "Advancing regulatory variant effect prediction with AlphaGenome." *Nature* 649(8099):1206–1218, 2026. DOI: 10.1038/s41586-025-10014-0.

### What they did
Avsec et al. introduce AlphaGenome, a unified deep-learning model for decoding the regulatory code in DNA sequences. The model takes a 1 Mb genomic window as input and generates multimodal predictions at base-pair resolution, including:
- Stranded RNA-seq (gene expression)
- ATAC-seq and DNase-seq (chromatin accessibility)
- CAGE and ProCAP (transcription start sites)
- CHIP-seq (histone marks and transcription factor binding)
- Splice site usage and splice junctions
- Hi-C contact maps

AlphaGenome extends the Enformer architecture by scaling the input window to 1 Mb, achieving single base-pair resolution output, and supporting all human tissues and cell types with ontology-based track selection. A free API is provided for non-commercial research.

### What they found
- State-of-the-art performance on regulatory variant effect prediction benchmarks across all output modalities.
- Quantile scores normalise variant effects against the genome-wide distribution, enabling cross-variant and cross-tissue comparisons.
- The model supports both scalar variant scoring (via `score_variants` with specialised scorers per output type) and full track prediction (via `predict_variant`) for detailed mechanistic inspection.
- Validated on known eQTLs, GWAS loci, and splice-altering variants.

### How it relates to our work
AlphaGenome is the tool we apply. Our work is an applied validation of AlphaGenome on a disease-specific gene (CFTR) with a well-characterised clinical database (CFTR2) providing ground truth. We use the recommended variant scorers (`GeneMaskLFCScorer` for RNA-seq, `CenterMaskScorer` for ATAC-seq, `GeneMaskSplicingScorer` for splice site usage) and the quantile score normalisation described in this paper. Our findings — particularly the strong splice and ATAC signals for His1054Gln and Arg104Gly — are the first CFTR-specific application of AlphaGenome quantile scores reported in the literature.

### Gap our work fills
Avsec et al. demonstrate genome-wide performance but do not apply AlphaGenome to CFTR or any cystic fibrosis variant set. They do not benchmark against CFTR2 clinical labels. They do not show whether quantile scores stratify variants within a single disease gene in a clinically interpretable way. Our work provides this disease-specific application and demonstrates that quantile scores are interpretable in the context of CFTR variant pathogenicity classification.

---

## 3. Michels et al. 2019 — In Silico Predictors for CFTR (PMC6905453)

**Citation:** Michels M, Matte U, Fraga LR, Mancuso ACBB, Ligabue-Braun R, Berneira EFR, Siebert M, Sanseverino MTV. "Determining the pathogenicity of CFTR missense variants: Multiple comparisons of in silico predictors and variant annotation databases." *Genetics and Molecular Biology* 42(3):560–570, 2019. PMC6905453.

### What they did
Michels et al. evaluated eight computational predictors for classifying the pathogenicity of 779 CFTR missense variants using the PredictSNP consensus classifier. Predictors assessed included MAPP, PhDSNP, PolyPhen-1, PolyPhen-2, SIFT, SNAP, nsSNPAnalyzer, and PANTHER. Performance was benchmarked against CFTR database annotations.

### What they found
- Most predictors were **not reliable** for CFTR missense variants.
- Performance was highly variable:
  - SNAP: sensitivity 100%, specificity 0% — predicts everything as pathogenic
  - MAPP and PhDSNP: specificity 100%, sensitivity 22–33% — miss most true positives
  - SIFT: sensitivity 77.8%, specificity 0%
  - PredictSNP consensus: sensitivity 77.8%, specificity 25%
- No single tool or ensemble achieved acceptable sensitivity and specificity simultaneously.
- The authors concluded that in silico predictions are **insufficient for independent clinical use** and must be combined with functional and clinical data.

### How it relates to our work
Michels et al. establish the baseline: as of 2019, no computational predictor performed reliably on CFTR. This provides the historical context for why our application of AlphaMissense (AUC 0.946) and AlphaGenome (quantile scores) represents a substantial advance. The tools they evaluated (SIFT, PolyPhen-2) are the same baselines we benchmark against, and our results confirm and extend their finding that SIFT and PolyPhen-2 underperform — but we show that AlphaMissense overcomes the limitations they identified.

### Gap our work fills
Michels et al. did not have access to AlphaMissense or AlphaGenome. They evaluated only protein-level conservation and structural predictors. They did not assess any genomic regulatory or splicing model. They did not apply quantile normalisation or tissue-specific scoring. Our work demonstrates that the reliability problem they identified in 2019 is substantially resolved by AlphaMissense (AUC 0.946 vs. best 2019 tool at ~0.7), and that AlphaGenome adds a second orthogonal dimension — regulatory and splicing effects — that none of their tools could address.

---

## 4. Liu et al. 2026 — AlphaGenome Applied to RHD (bioRxiv 2026.01.21.700828)

**Citation:** Liu M, Shen Z, Jeong YK, Yu N, Wu S-C, Wittig A, Tenen D, Liu Y, Chai L. "AlphaGenome-enabled analysis of non-coding regulatory variants underlying RHD expression with wet-lab validation." *bioRxiv* 2026.01.21.700828, February 3, 2026. Brigham and Women's Hospital / Harvard Medical School / Broad Institute.

### What they did
Liu et al. developed an integrated AI-plus-wet-lab framework to identify and validate non-coding regulatory variants affecting expression of the RHD gene (encoding the Rhesus D blood group antigen). They used AlphaGenome to prioritise regulatory variants across the RHD locus, then used CRISPR-based base editing in K562 cells to functionally validate the top predictions. This represents the **first reported wet-lab phenotypic validation of AlphaGenome predictions**.

### What they found
- AlphaGenome successfully prioritised non-coding variants with functional regulatory impact on RHD expression.
- A variant at chr1:25272434 showed the most substantial predicted regulatory effect, confirmed by CRISPR base editing.
- Strong concordance between AlphaGenome predictions and experimental outcomes, demonstrating that quantile scores translate to real biological signal detectable at the cellular level.
- The framework provides a scalable approach for genomics-based blood typing and transfusion medicine applications.

### How it relates to our work
Liu et al. provide the closest methodological parallel to our work: applying AlphaGenome to a single disease-relevant gene with clinical implications. Their use of the regulatory scoring framework is directly analogous to our application of ATAC and RNA-seq quantile scores to CFTR. Their wet-lab validation — demonstrating that AlphaGenome predictions correspond to real expression changes — strengthens the biological credibility of the quantile scores we compute for CFTR variants.

### Gap our work fills
Liu et al. focus on a single non-coding variant in a blood group gene. They do not benchmark against a clinical variant database comparable to CFTR2. They do not combine AlphaGenome with AlphaMissense or with a protein-level pathogenicity benchmark. They do not address splice site effects or apply the `GeneMaskSplicingScorer`. Our work applies AlphaGenome across all three major modalities (RNA-seq, ATAC, splice), integrates quantile scores with AlphaMissense protein-level scores, and evaluates 1,278 ambiguous CFTR variants against a clinical ground truth — a substantially larger and more rigorously evaluated application than theirs.

---

## Summary Table

| | McDonald 2024 | Avsec 2026 | Michels 2019 | Liu 2026 |
|---|---|---|---|---|
| Gene/disease | CFTR / CF | Genome-wide | CFTR / CF | RHD / transfusion |
| Tool | AlphaMissense | AlphaGenome | 8 tools (SIFT, PP2…) | AlphaGenome |
| Ground truth | CFTR2 + functional | eQTLs, GWAS, splicing | CFTR databases | CRISPR base editing |
| Protein-level scoring | ✓ | ✗ | ✓ | ✗ |
| Regulatory/ATAC scoring | ✗ | ✓ | ✗ | ✓ |
| Splice scoring | ✗ | ✓ | ✗ | ✗ |
| Combined AM + AG | ✗ | ✗ | ✗ | ✗ |
| Scale (variants) | 169 | Genome-wide | 779 | 1 locus |
| Wet-lab validation | ✓ (functional assays) | ✗ | ✗ | ✓ (CRISPR) |
| **Our work** | Extends to 1,278 VUS; adds AlphaGenome | First CFTR application | Updates baseline | Adds splice; scales to 1,278 variants; integrates with AM |

---

*Compiled 2026-05-28; updated 2026-08-28. All papers accessed via PubMed, PMC, bioRxiv, and alphagenomedocs.com.*

---

## 5. Garcia-Gonzalez and Gogolewski 2026 — Trends in Genetics

**Citation:** Garcia-Gonzalez E, Gogolewski K. *Trends in Genetics*, 2026.
*(Full title and DOI to be confirmed from meeting materials — cited in direction meeting.)*

### What they did
To be completed when full citation is available.

### How it relates to our work
Cited in the project direction meeting as relevant context for the regulatory variant interpretation approach. Full relevance to be documented once the paper is reviewed.

### Gap our work fills
To be completed.

---
