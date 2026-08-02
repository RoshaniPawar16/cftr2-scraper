# AlphaGenome Batch Analysis: 7 Unclassified CFTR Variants

**Model:** AlphaGenome v0.6.1  |  **Genome:** hg38  |  **Tissue:** Lung (UBERON:0002048)
**Outputs scored:** RNA-seq (`GeneMaskLFCScorer`), ATAC-seq (`CenterMaskScorer` 501 bp), Splice site usage (`GeneMaskSplicingScorer`)
**Window:** 1 Mb centred on variant  |  **Scores:** raw + quantile (rank against common variants, MAF > 0.01 in any gnomAD v3 population)

> **Calibration and reproducibility note.** This run was submitted on 28 May 2026. AlphaGenome updated its quantile calibration from chromosome-22-only to genome-wide on 18 June 2026 (announced 11 June; see https://www.alphagenomecommunity.com/t/updating-variant-score-quantiles/929). All quantile values in this document used the chromosome-22 background. Raw scores are unaffected for most variants. Full regeneration (2 August 2026) found 75 of 1,278 variants with changed raw scores; cause not determinable from available records (no API changelog covers SNVs in this period). A determinism test on the 10 most-changed variants scored them twice in the same session, 6 minutes apart: both runs agreed exactly. Longer-interval stability is untested — a rerun at 7-day separation is required before the raw score changes can be attributed unambiguously to a one-time backend change rather than periodic variation. The full 1,278-variant dataset (with `raw_changed` flag) is in `results/alphagenome/quantiles_genomewide_2026-08.csv`.

---

## Variants

| Variant | Protein | hg38 Position | REF>ALT | AlphaMissense |
|---------|---------|---------------|---------|---------------|
| Leu49Pro | L49P | chr7:117,504,345 | T>C | 0.9757 |
| Arg104Gly | R104G | chr7:117,530,935 | A>G | 0.8448 |
| Pro355Leu | P355L | chr7:117,540,294 | C>T | 0.858 |
| Phe650Leu | F650L | chr7:117,592,115 | T>C | 0.8455 |
| Leu986Pro | L986P | chr7:117,606,722 | T>C | 0.8685 |
| His1054Gln | H1054Q | chr7:117,611,603 | T>G | 0.901 |
| Arg1097Cys | R1097C | chr7:117,611,730 | C>T | 0.6513 |

---

## Score Summary

**Quantile score**: rank of the variant effect within a background of common variants (MAF > 0.01 in any gnomAD v3 population) for that output type.  
A quantile of 0.99 means the variant's score matches the 99th percentile of that common-variant background — not of all human variation — tissue-specific.

| Variant | AM | RNA raw | RNA q | ATAC raw | ATAC q | Splice raw | Splice q |
|---------|-----|---------|-------|----------|--------|------------|----------|
| Leu49Pro | 0.9757 | 0.0238 | 0.999 | 0.0021 | 0.081 | 0.0078 | 0.821 |
| Arg104Gly | 0.8448 | 0.0058 | 0.974 | 0.0199 | 0.699 | 0.0273 | 0.993 |
| Pro355Leu | 0.858 | 0.0045 | 0.965 | 0.0107 | 0.537 | 0.0078 | 0.635 |
| Phe650Leu | 0.8455 | 0.0042 | 0.957 | 0.0196 | 0.693 | 0.0078 | 0.640 |
| Leu986Pro | 0.8685 | 0.0043 | 0.958 | 0.0184 | 0.675 | 0.0117 | 0.931 |
| His1054Gln | 0.901 | 0.0083 | 0.991 | 0.0751 | 0.950 | 0.0117 | 0.948 |
| Arg1097Cys | 0.6513 | 0.0054 | 0.968 | 0.0485 | 0.905 | 0.0078 | 0.720 |

---

## Ranked by ATAC Quantile Score

| Rank | Variant | AM Score | ATAC Quantile | ATAC Raw | Bins >0.5 | Flag |
|------|---------|----------|---------------|----------|-----------|------|
| 1 | His1054Gln | 0.901 | 0.950 | 0.0751 | 29 | 🔴 top regulatory signal |
| 2 | Arg1097Cys | 0.6513 | 0.905 | 0.0485 | 16 | 🟡 moderate |
| 3 | Arg104Gly | 0.8448 | 0.699 | 0.0199 | 13 | ⚪ low |
| 4 | Phe650Leu | 0.8455 | 0.693 | 0.0196 | 18 | ⚪ low |
| 5 | Leu986Pro | 0.8685 | 0.675 | 0.0184 | 9 | ⚪ low |
| 6 | Pro355Leu | 0.858 | 0.537 | 0.0107 | 10 | ⚪ low |
| 7 | Leu49Pro | 0.9757 | 0.081 | 0.0021 | 13 | ⚪ low |

---

## Ranked by Splice Quantile Score

| Rank | Variant | AM Score | Splice Quantile | Splice Raw | Bins >0.5 | Flag |
|------|---------|----------|-----------------|------------|-----------|------|
| 1 | Arg104Gly | 0.8448 | 0.993 | 0.0273 | 6 | 🔴 cryptic splice risk |
| 2 | His1054Gln | 0.901 | 0.948 | 0.0117 | 39 | 🟡 moderate |
| 3 | Leu986Pro | 0.8685 | 0.931 | 0.0117 | 5 | 🟡 moderate |
| 4 | Leu49Pro | 0.9757 | 0.821 | 0.0078 | 8 | 🟡 moderate |
| 5 | Arg1097Cys | 0.6513 | 0.720 | 0.0078 | 2 | ⚪ low |
| 6 | Phe650Leu | 0.8455 | 0.640 | 0.0078 | 4 | ⚪ low |
| 7 | Pro355Leu | 0.858 | 0.635 | 0.0078 | 6 | ⚪ low |

---

## Interpretation

### What quantile scores add over raw log2FC

Raw log2FC measures the absolute signal change at a locus. Quantile scores normalise this against the genome-wide distribution of variant effects for that output type, making scores comparable across output types and variants.

- **Quantile ≥ 0.95**: variant effect scores above the 95th percentile of common variants (MAF > 0.01 in gnomAD v3) for that tissue/output — note that coding variants inside gene bodies routinely clear this threshold by construction, so this is not in itself strong evidence of functional impact.
- **Quantile 0.80–0.95**: notable but not extreme — warrants further investigation.
- **Quantile < 0.80**: effect is within typical background variation.

### What AlphaMissense misses

AlphaMissense scores protein-level pathogenicity only. High quantile scores on ATAC or splice outputs identify variants with regulatory or splicing mechanisms that protein-sequence models cannot detect.

> **Historical figures only.** The seven variants below were the original priority candidates. They were subsequently found to have been selected on 1000 Genomes allele frequencies (all singletons or doubletons in 2,504 persons), not gnomAD, and four rank below the 1st percentile of the 1,278 cohort on center-mask rescoring. The quantile scores below used the chromosome-22 calibration (run 28 May 2026, predating the 18 June 2026 genome-wide update). These figures are retained for audit traceability; they are not current priority candidates.

- **His1054Gln** — ATAC quantile 0.950 (chr22-calibrated), splice quantile 0.948. AlphaMissense 0.901.

- **Arg104Gly** — Splice quantile 0.993 (chr22-calibrated). AlphaMissense 0.8448.

- **Arg1097Cys** — ATAC quantile 0.905, splice quantile 0.720 (chr22-calibrated). AlphaMissense 0.6513.

---

## Rescue Variant Analysis (Full 1,278 Ambiguous VUS)

Source: `results/alphagenome/alphagenome_full_cftr_results.csv`  
Full table: `results/alphagenome/alphagenome_rescue_variants.csv`  
Note: Groups below use AlphaGenome scores only. For rescue analysis incorporating CADD v1.7 and SpliceAI v1.3 comparators, see `docs/comparator_analysis_report.md`.

These groups identify variants where AlphaGenome finds functional evidence that AlphaMissense (protein-level) does not flag. All variants have `am_pathogenicity < 0.56` (ambiguous class) but show strong DNA-level signals in lung tissue.

### Regulatory Rescue — 87 variants
**Criterion:** ATAC quantile > 0.95 AND AlphaMissense < 0.56

Strong chromatin accessibility disruption in lung despite sub-pathogenic AM score. Suggests the variant alters a regulatory element — enhancer, promoter, or open chromatin region — independently of protein misfolding.

| Rank | Variant | AM Score | ATAC Quantile | Splice Quantile |
|------|---------|----------|---------------|-----------------|
| 1 | F1413I | 0.488 | 0.999 | 0.996 |
| 2 | Q1411H | 0.357 | 0.999 | 0.960 |
| 3 | E1409K | 0.511 | 0.999 | 0.976 |
| 4 | Q1411L | 0.462 | 0.998 | 0.855 |
| 5 | R1386S | 0.344 | 0.995 | 0.989 |

### Splicing Rescue — 728 variants
**Criterion:** SPLICE quantile > 0.95 AND AlphaMissense < 0.56

The high count (57% of all 1,278 ambiguous variants) reflects expected biology: all variants are exonic, placing them in regions where `GeneMaskSplicingScorer` is sensitive by design. Using a stricter threshold (SPLICE q > 0.99) yields 361 variants.

Top 5 by splice quantile:

| Rank | Variant | AM Score | ATAC Quantile | Splice Quantile |
|------|---------|----------|---------------|-----------------|
| 1 | S1058C | 0.473 | 0.847 | 0.999983 |
| 2 | S1058G | 0.508 | 0.847 | 0.999983 |
| 3 | K464R | 0.549 | 0.758 | 0.999942 |
| 4 | A155G | 0.357 | 0.866 | 0.999941 |
| 5 | G970C | 0.491 | 0.933 | 0.999941 |

### Dual Mechanism — 56 variants
**Criterion:** ATAC quantile > 0.95 AND SPLICE quantile > 0.95 AND AlphaMissense < 0.56

Highest priority group: variants with simultaneous chromatin accessibility and splice site disruption that AlphaMissense does not capture. These warrant functional follow-up (e.g. minigene splicing assay, CRISPR regulatory perturbation).

| Rank | Variant | AM Score | ATAC Quantile | Splice Quantile |
|------|---------|----------|---------------|-----------------|
| 1 | F1413I | 0.488 | 0.999 | 0.996 |
| 2 | Q1411H | 0.357 | 0.999 | 0.960 |
| 3 | E1409K | 0.511 | 0.999 | 0.976 |
| 4 | R1386S | 0.344 | 0.995 | 0.989 |
| 5 | P960H | 0.491 | 0.994 | 0.998 |

### Interpretation

These groups operationalise the core limitation identified in McDonald et al. 2024: AlphaMissense cannot distinguish regulatory or splicing mechanisms from protein-level effects. Variants in the regulatory or dual-mechanism rescue groups may be pathogenic via CFTR expression reduction or aberrant splicing rather than protein misfolding — mechanisms that are relevant for selecting modulators or assessing residual CFTR function.

The 56 dual-mechanism variants used the chromosome-22 calibration and the gene-mask scorer, whose scores are set by the nearest canonical splice site rather than variant-specific effect. These figures are retained as historical context; the group is not interpreted as a priority candidate set.

---

*AlphaGenome v0.6.1 · hg38 · Lung UBERON:0002048 · 2026-05-31*