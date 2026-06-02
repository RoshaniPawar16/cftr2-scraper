# AlphaGenome Batch Analysis: 7 Unclassified CFTR Variants

**Model:** AlphaGenome v0.6.1  |  **Genome:** hg38  |  **Tissue:** Lung (UBERON:0002048)
**Outputs scored:** RNA-seq (`GeneMaskLFCScorer`), ATAC-seq (`CenterMaskScorer` 501 bp), Splice site usage (`GeneMaskSplicingScorer`)
**Window:** 1 Mb centred on variant  |  **Scores:** raw + quantile (normalised rank across all human variants)

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

**Quantile score**: normalised rank of the variant effect relative to all human variants for that output type.  
A quantile of 0.99 means the variant's effect is larger than 99% of all scored variants — tissue-specific.

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

- **Quantile ≥ 0.95**: variant effect is in the top 5% of all human variants for that tissue/output — strong evidence of functional impact beyond protein-level effect.
- **Quantile 0.80–0.95**: notable but not extreme — warrants further investigation.
- **Quantile < 0.80**: effect is within typical background variation.

### What AlphaMissense misses

AlphaMissense scores protein-level pathogenicity only. High quantile scores on ATAC or splice outputs identify variants with regulatory or splicing mechanisms that protein-sequence models cannot detect.

- **His1054Gln** — ATAC quantile 0.950: strongest chromatin accessibility signal. AlphaMissense 0.901 — regulatory disruption may contribute independently of protein misfolding.

- **Arg104Gly** — Splice quantile 0.993: highest splicing impact. AlphaMissense score 0.8448 captures protein effect but not this splicing mechanism.

- **Arg1097Cys** — lowest AlphaMissense score (0.6513). ATAC quantile 0.905, splice quantile 0.720. If either is elevated, it provides a regulatory/splicing explanation for pathogenicity that protein scoring alone does not.

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

The 56 dual-mechanism variants are the strongest candidates for reclassification from VUS to likely pathogenic pending functional validation.

---

*AlphaGenome v0.6.1 · hg38 · Lung UBERON:0002048 · 2026-05-31*