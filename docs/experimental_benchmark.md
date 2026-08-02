# Experimental Benchmark: Minigene-Validated CFTR Splice Variants
**Date:** 2026-08-02  
**Branch:** integrity-audit-2026-07  
**Sources:** Zhang B et al., Front Genet 2025;16:1543623; Bergougnoux A et al., J Cyst Fibros 2023;22:515–524

---

## False-positive counts per tool (primary result)

At each tool's own published threshold or the closest internally-derived threshold:

| Tool | Threshold | Sensitivity | Specificity | **FP / 12 negatives** | Source of threshold |
|---|---|---|---|---|---|
| **GM splice quantile** | > 0.95 | 10/11 = 91% | 4/12 = 33% | **8/12 (67%)** | Ours — no external citation |
| CM splice 501 DLS | top-20% cohort | 7/11 = 64% | 8/12 = 67% | 4/12 (33%) | Ours |
| **CM splice 501 L2D** | top-20% cohort | 4/11 = 36% | 12/12 = 100% | **0/12 (0%)** | Ours |
| CM splice 501 L2L | top-20% cohort | 4/11 = 36% | 12/12 = 100% | 0/12 (0%) | Ours |
| SpliceAI | ≥ 0.2 | 1/11 = 9%* | 11/12 = 92% | 1/12 (8%) | Jaganathan et al. 2019 |
| SpliceAI | ≥ 0.5 | 1/11 = 9%* | 12/12 = 100% | 0/12 (0%) | Jaganathan et al. 2019 |
| AlphaMissense | — | — | — | — | not a splice predictor |

*SpliceAI scores are non-zero for only 2/23 variants in this benchmark; see coverage note.

**The gene-mask quantile (GM_q) produces 8 false positives out of 12 confirmed-negative variants.** It correctly identifies 10 of 11 positives but cannot distinguish splice-altering from non-splice-altering variants in this benchmark.

---

## Benchmark composition

22 unique CFTR variants from two minigene studies. 23 rows total (Glu403Asp appears in both papers as c.1209G>T and c.1209G>C — distinct nucleotides, both confirmed positive).

- **Positives (confirmed splice-altering): 11** — at least one paper's minigene assay showed exon skipping or partial deletion
- **Negatives (confirmed non-altering): 12** — tested and showed normal splicing in both systems

Coordinates: GRCh38, derived from NM_000492.4 HGVS notation via Ensembl VEP REST API.

---

## Full benchmark table

| Variant | Result | Source | hg38 pos | Dist(bp) | AM | GM_q | DLS-501 | L2D-501 | SpliceAI | CADD |
|---|---|---|---|---|---|---|---|---|---|---|
| Lys163Met | **POS** | Zhang | 117531113 A>T | 1 | 0.923 | **1.000** | 0.486 | 0.630 | 0.000 | — |
| Asp249Tyr | neg | Zhang | 117536549 G>T | 1 | 0.187 | 0.747 | 0.002 | 0.006 | 0.000 | — |
| Asp373Tyr | **POS** | Zhang | 117542016 G>T | 0 | 0.170 | 0.998 | 0.069 | 0.078 | 0.000 | — |
| Asn396Tyr | neg | Zhang | 117542085 A>T | 23 | 0.216 | 0.993 | 0.019 | 0.023 | 0.000 | — |
| Glu403Asp_T | **POS** | Zhang | 117542108 G>T | 0 | 0.200 | **1.000** | 1.310 | 1.077 | 0.000 | — |
| Thr1053Ser | neg | Zhang | 117611598 A>T | 17 | 0.115 | **1.000** | 0.119 | 0.240 | 0.000 | — |
| Lys1080Arg | **POS** | Zhang | 117611680 A>G | 99 | 0.140 | 0.945 | 0.008 | 0.013 | 0.000 | — |
| Gly1123Arg | **POS** | Zhang | 117611808 G>C | 0 | 0.272 | **1.000** | 1.134 | 1.011 | 0.000 | — |
| Arg55Lys | neg | Bergougnoux | 117504363 G>A | 0 | 0.151 | **1.000** | 0.348 | 0.378 | 0.000 | — |
| Arg74Gln | neg | Bergougnoux | 117509090 G>A | 52 | 0.082 | 0.999 | 0.105 | 0.108 | 0.000 | — |
| Glu92Lys | **POS** | Bergougnoux | 117530899 G>A | 0 | 0.944 | 0.999 | 0.075 | 0.081 | 0.000 | — |
| Ile175Val | **POS** | Bergougnoux | 117534309 A>G | 33 | 0.190 | **1.000** | 0.025 | 1.031 | 0.000 | — |
| Thr351Ser | neg | Bergougnoux | 117540282 C>G | 64 | 0.573 | 0.754 | 0.003 | 0.004 | 0.000 | — |
| Glu403Asp_C | **POS** | Bergougnoux | 117542108 G>C | 0 | 0.200 | **1.000** | 1.182 | 1.016 | 0.000 | — |
| Met469Val | neg | Bergougnoux | 117559476 A>G | 12 | 0.511 | 0.760 | 0.005 | 0.000 | 0.010 | 25.7 |
| Arg560Lys | **POS** | Bergougnoux | 117587833 G>A | 0 | 0.788 | **1.000** | 0.392 | 0.406 | 0.000 | — |
| Ile918Met | neg | Bergougnoux | 117603628 T>G | 96 | 0.367 | 0.861 | 0.007 | 0.000 | 0.220 | 23.8 |
| Gly970Arg | **POS** | Bergougnoux | 117603782 G>C | 0 | 0.657 | **1.000** | 0.897 | 0.858 | 0.000 | — |
| Gly970Val | **POS** | Bergougnoux | 117606674 G>T | 0 | 0.440 | 0.999 | 0.202 | 0.000 | **0.950** | 27.9 |
| Gly970Asp | neg | Bergougnoux | 117606674 G>A | 0 | 0.764 | 0.994 | 0.026 | 0.031 | 0.000 | — |
| Gly1069Arg | neg | Bergougnoux | 117611646 G>A | 65 | 0.311 | 0.962 | 0.002 | 0.014 | 0.000 | — |
| Arg1070Gln | neg | Bergougnoux | 117611650 G>A | 69 | 0.398 | 0.963 | 0.007 | 0.000 | 0.010 | 32.0 |
| Ala1364Val | neg | Bergougnoux | 117664815 C>T | 45 | 0.687 | 0.999 | 0.115 | 0.133 | 0.000 | — |

Bolded GM_q values exceed the 0.95 threshold. Note 8 negatives with GM_q ≥ 0.95.

---

## AUROC and AUPRC (n=23, confidence interval note)

n=23 is too small for reliable bootstrap CIs. AUROC and AUPRC are reported as point estimates only.

| Tool | AUROC | AUPRC | AUPRC baseline | AUPRC lift |
|---|---|---|---|---|
| GM splice quantile | 0.856 | 0.878 | 0.478 | 1.84× |
| CM DLS-501 | 0.849 | 0.868 | 0.478 | 1.82× |
| **CM L2D-501** | **0.833** | **0.895** | 0.526 | **1.70×** |
| CM L2L-501 | 0.833 | 0.895 | 0.526 | 1.70× |
| SpliceAI | **0.432** | 0.526 | 0.478 | **1.10× (near-chance)** |
| AlphaMissense | 0.576 | 0.660 | 0.478 | 1.38× |

**SpliceAI AUROC = 0.432 (below chance).** This reflects a coverage problem, not a prediction failure: SpliceAI returns 0 for 21 of 23 variants. The precomputed SpliceAI scores available via Ensembl VEP REST do not cover most of these exon-interior variants. SpliceAI's two non-zero scores (Gly970Val = 0.95, confirmed positive; Ile918Met = 0.22, confirmed negative) are consistent with its design — but the benchmark cannot fairly evaluate SpliceAI with 21/23 missing scores.

---

## SpliceAI coverage limitation

SpliceAI precomputed scores are not available for 21/23 experimental variants via the Ensembl VEP REST API. These variants are exon-interior missense changes (most at dist ≥ 1 bp from splice sites). SpliceAI's precomputed database covers variants affecting canonical splice site strength; it does not cover all possible exonic variants. The apparent SpliceAI AUROC = 0.432 should not be reported as SpliceAI's performance — it is a coverage artifact.

---

## Arg1070Gln in full

**Variant:** chr7:117611650 G>A, Arg1070Gln, NM_000492.4:c.3209G>A  
**Minigene result (Bergougnoux 2023):** Negative. Partial exon 20 exclusion was observed at wild-type level (background basal skipping, not variant-caused). Authors classify as no deleterious consequence.  
**Distance to nearest splice site:** 69 bp  
**AlphaMissense:** 0.398 (ambiguous — in the 1,278 cohort)  
**GM splice quantile:** 0.963 — **exceeds the 0.95 threshold → false positive**  
**CM DLS-501:** 0.007 — correctly low  
**CM L2D-501:** 0.000 — correctly zero  
**SpliceAI:** 0.01 — correctly low  
**CADD PHRED:** 32.0 — elevated (the missense effect)

The gene-mask scorer scores Arg1070Gln at 0.963 because it detects the maximum gene-body splice junction probability change — which at 69 bp from a splice site is dominated by the gene's background splice activity, not the variant's specific effect. L2D-501 and DLS-501 correctly assign low scores. This case demonstrates the GM scorer's false positive mechanism: it detects the same canonical splice site signal that exists regardless of the specific variant.

---

## Search for additional CFTR experimental data

A search for other CFTR variants with experimental splicing evidence (minigene, patient RT-PCR, RNA-seq) identified:

1. **Zhang B et al. 2025** — 8 variants (this benchmark). PMC11965618.
2. **Bergougnoux A et al. 2023** — 15 variants (this benchmark). J Cyst Fibros 22:515.
3. **Other potential sources:** The CFTR-France consortium and CFTR2 database occasionally report splicing variants, but variant-level minigene results are not systematically published in extractable form. The CFTR mutation database (www.cftr2.org) notes splice mechanism for some variants but does not provide quantitative minigene data. No additional extractable case series were identified in this search that would add to the current 23-variant benchmark.

Full benchmark: `results/experimental_benchmark.csv` (23 rows).
