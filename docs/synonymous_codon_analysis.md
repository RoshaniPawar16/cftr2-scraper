# Synonymous Codon Analysis: AlphaGenome Sensitivity to Nucleotide Identity

**Date:** 2026-08-02  
**Branch:** integrity-audit-2026-07  
**Status:** Diagnosis and quantification only. Findings are reported without inference beyond what the null comparison supports.

---

## Background

`cftr_alphamissense.tsv` contains 9,721 nucleotide variants mapping to 8,597 unique protein variants. Of these, 145 protein variants within the 1,278 AM-ambiguous cohort are reachable by two or more distinct single-nucleotide variants. Each such group is a controlled comparison: AlphaMissense assigns identical scores by construction (it scores the amino acid change), while CADD, SpliceAI, and AlphaGenome score the nucleotide.

This analysis tests whether AlphaGenome outputs diverge within these groups and, if so, whether the divergence exceeds what would be expected from general model variability at this genomic scale.

**This analysis tests information content, not accuracy.** Divergence within a group demonstrates that the models differ; it does not establish which call is correct. No ground truth is available for most of these variants. The control is internal.

**Sample size:** 145 groups is a reasonable n for this comparison. Unlike the twelve-variant positive control (Check 8, severely underpowered), this comparison has sufficient groups to characterise the distribution of within-group divergence and compare it to a null.

---

## Group structure

- **145 groups** with two or more distinct variant_ids sharing a protein_variant
  - 112 groups of size 2
  - 33 groups of size 3
- **323 total variants** involved
- **All groups within ≤10 bp** of each other (no group excluded for distance). All represent variants in the same or adjacent codon positions. The comparison holds for all 145 groups.

AlphaMissense scores are **identical within every group** (0 groups with any within-group difference). Confirmed by construction.

---

## Within-group divergence

For each group, the maximum pairwise absolute difference was computed across all members. Modalities are listed in order of decreasing median divergence.

| Tool | Scores | Median within-group diff | IQR | Max | Groups >0.1 | Groups >0.3 | Groups >0.5 |
|---|---|---|---|---|---|---|---|
| AlphaMissense | amino acid | 0.0000 | [0.00, 0.00] | 0.0000 | 0 | 0 | 0 |
| CADD PHRED | nucleotide | **0.2700** | [0.10, 0.90] | 8.0940 | 109/145 | 70/145 | 52/145 |
| SpliceAI max delta | nucleotide | **0.0100** | [0.00, 0.05] | 0.7300 | 16/145 | 3/145 | 1/145 |
| AlphaGenome ATAC quantile | nucleotide | **0.0000** | [0.00, 0.062] | 0.5671 | 30/145 | 12/145 | 4/145 |
| AlphaGenome splice quantile | nucleotide | **0.0000** | [0.00, 0.003] | 0.2343 | 11/145 | 0/145 | 0/145 |
| AlphaGenome RNA quantile | nucleotide | **0.0000** | [0.00, 0.004] | 0.0947 | 0/145 | 0/145 | 0/145 |

**Interpretation bounded by null comparison below.**

---

## Null comparison

### Construction

Two null distributions were constructed:

1. **Random pairs** (20,000 permutations): random pairs drawn without replacement from the full 1,278 cohort.
2. **Proximity-matched pairs** (2,245 pairs): pairs of variants within ≤5 bp of each other that do **not** produce the same amino acid change. These test whether AlphaGenome is generally concordant at short genomic distances, independent of shared protein consequence.

### Results

All permutation tests used 20,000 samples.

| Metric | Observed median | Random null median | p (obs ≤ null) | Proximity null median | p (obs ≤ prox) |
|---|---|---|---|---|---|
| AlphaGenome splice quantile | 0.0000 | 0.0485 | <0.0001 | 0.0324 | <0.0001 |
| AlphaGenome ATAC quantile | 0.0000 | 0.2516 | <0.0001 | 0.1671 | <0.0001 |
| CADD PHRED | 0.2700 | 2.6000 | (not computed) | — | — |
| SpliceAI max delta | 0.0100 | 0.0100 | ≈1.0 | — | — |

### Interpretation

**AlphaGenome splice and ATAC:** Within-group pairs are significantly more concordant than both random pairs and proximity-matched random pairs (p<0.0001 in all four tests). The median within-group difference is zero for both modalities. This is not simply a property of genomic proximity — proximity-matched pairs at the same scale show substantially larger median differences (0.032 splice, 0.167 ATAC). The within-group constraint is attributable to shared amino acid context.

**CADD:** Within-group pairs are much more similar than random (median 0.27 vs 2.60) but still show substantial within-group variation (52/145 groups differ by >0.5 PHRED). CADD is a nucleotide-level model and its within-group variation is expected and large.

**SpliceAI:** Observed and random-null medians are identical (0.01). Within-group pairs are **not more similar than randomly chosen pairs** for SpliceAI. This does not mean SpliceAI is noisy overall; it means SpliceAI treats synonymous codon variants as having potentially very different splice consequences, which is mechanistically plausible (splice predictions depend on the specific nucleotide, not the amino acid). One group (H620Q: T>G vs T>A at position 117592027) has SpliceAI 0.73 vs 0.00 at the same genomic position — the specific base matters entirely for that prediction.

**Conclusion bounded by null:** AlphaGenome's splice and ATAC quantiles are substantially more concordant within same-amino-acid groups than within proximity-matched different-amino-acid groups. The within-group constraint is real and statistically distinguishable from the null. **This shows that AlphaGenome outputs contain signal that is shared between synonymous nucleotide variants producing the same amino acid change, over and above general proximity effects.** It does not establish that AlphaGenome is correct; it establishes that its predictions are constrained by sequence context in a way that correlates with the amino acid substitution.

---

## Top 10 groups by splice-quantile divergence

Groups with the largest within-group splice quantile difference, in full.

| Protein | AM | Variant_id | Change | RNA_q | ATAC_q | SPLICE_q | Splice diff |
|---|---|---|---|---|---|---|---|
| F1257L | 0.4239 | chr7:117642491:T>G | T>G | 0.9391 | 0.8264 | 0.7013 | 0.2343 |
| | | chr7:117642489:T>C | T>C | 0.9748 | 0.8227 | 0.9356 | |
| | | chr7:117642491:T>A | T>A | 0.9730 | 0.6067 | 0.8435 | |
| F229L | 0.4205 | chr7:117535355:C>A | C>A | 0.9821 | 0.7862 | 0.7295 | 0.2280 |
| | | chr7:117535355:C>G | C>G | 0.9821 | 0.7862 | 0.7295 | |
| | | chr7:117535353:T>C | T>C | 0.9491 | 0.7273 | 0.9575 | |
| S1456R | 0.3577 | chr7:117667033:C>A | C>A | 0.9825 | 0.7379 | 0.9525 | 0.2185 |
| | | chr7:117667033:C>G | C>G | 0.9825 | 0.7379 | 0.9525 | |
| | | chr7:117667031:A>C | A>C | 0.9844 | 0.6746 | 0.7340 | |
| T604S | 0.5065 | chr7:117591978:C>G | C>G | 0.9524 | 0.5370 | 0.9992 | 0.1557 |
| | | chr7:117591977:A>T | A>T | 0.9717 | 0.0920 | 0.8435 | |
| T1036S | 0.4239 | chr7:117610636:A>T | A>T | 0.9790 | 0.8712 | 0.9575 | 0.1541 |
| | | chr7:117610637:C>G | C>G | 0.9363 | 0.5994 | 0.8034 | |
| F693L | 0.4856 | chr7:117592244:T>C | T>C | 0.9887 | 0.5994 | 0.8309 | 0.1488 |
| | | chr7:117592246:T>G | T>G | 0.9944 | 0.5370 | 0.9797 | |
| | | chr7:117592246:T>A | T>A | 0.9944 | 0.5370 | 0.9797 | |
| F319L | 0.5618 | chr7:117540187:T>G | T>G | 0.9653 | 0.8626 | 0.9556 | 0.1450 |
| | | chr7:117540187:T>A | T>A | 0.9653 | 0.8626 | 0.9556 | |
| | | chr7:117540185:T>C | T>C | 0.9513 | 0.6211 | 0.8105 | |
| K857N | 0.3494 | chr7:117595010:G>T | G>T | 0.9967 | 0.7726 | 0.9988 | 0.1125 |
| | | chr7:117595010:G>C | G>C | 0.9620 | 0.4123 | 0.8863 | |
| F711L | 0.5213 | chr7:117592298:T>C | T>C | 0.9759 | 0.7105 | 0.8373 | 0.1120 |
| | | chr7:117592300:T>A | T>A | 0.9922 | 0.1825 | 0.9493 | |
| | | chr7:117592300:T>G | T>G | 0.9922 | 0.1825 | 0.9493 | |
| F429L | 0.3805 | chr7:117548716:T>C | T>C | 0.9676 | 0.6419 | 0.8886 | 0.1108 |
| | | chr7:117548718:C>A | C>A | 0.9977 | 0.5532 | 0.9994 | |
| | | chr7:117548718:C>G | C>G | 0.9977 | 0.5532 | 0.9994 | |

---

## Discordance at classification boundaries

### 693 discordant group membership

The 693 is defined as SPLICE quantile > 0.95 AND SpliceAI < 0.2.

| Membership | Count |
|---|---|
| Both members in 693 | 82 groups |
| Exactly one member in 693 | 19 groups |
| Neither member in 693 | 44 groups |

19 groups are split across the 693 boundary: two variants producing the same amino acid change receive different regulatory calls from AlphaGenome/SpliceAI. The 82 groups where both members qualify are concordant at the variant level but still carry within-group variation in the underlying quantile.

### Groups split by splice quantile > 0.95

15 groups have at least one member above 0.95 and at least one below.

Selected examples:

**T604S (AM=0.507):** C>G at pos 117591978 gives SPLICE_q=0.9992 (in 693); A>T at pos 117591977 gives SPLICE_q=0.8435 (not in 693). Same amino acid, 1 bp apart, one above threshold.

**K857N (AM=0.349):** G>T at pos 117595010 gives SPLICE_q=0.9988 (SpliceAI=0.4, above 0.2 threshold — not in 693); G>C gives SPLICE_q=0.8863 (SpliceAI=0.02 — not in 693). Neither is in 693, but both cross the splice-quantile boundary.

**T1036S (AM=0.424):** A>T at pos 117610636 gives SPLICE_q=0.9575 (in 693); C>G at pos 117610637 gives SPLICE_q=0.8034 (not in 693). 1 bp apart.

### Groups split by SpliceAI > 0.2

8 groups have at least one member above 0.2 and one below.

**H620Q (AM=0.417):** T>G at pos 117592027 gives SpliceAI=0.73 (not in 693, SPLICE_q=0.9999 exceeds threshold); T>A at the **same position** gives SpliceAI=0.00 (in 693). The most extreme example: identical position, entirely different SpliceAI prediction.

**G366R (AM=0.359):** G>A gives SpliceAI=0.35 (not in 693); G>C gives SpliceAI=0.00 (in 693). Same position, both have SPLICE_q=0.9967.

---

## Limitations

1. **No ground truth.** Divergence within a group shows the models differ; it does not identify which call is correct.
2. **Effect size is modest for AlphaGenome splice.** The maximum within-group splice divergence is 0.234; 134/145 groups have splice divergence ≤0.1. Most groups are highly concordant.
3. **ATAC shows larger within-group variation** (30 groups >0.1, 4 groups >0.5). ATAC quantiles appear more sensitive to the specific nucleotide than splice quantiles.
4. **SpliceAI's within-group variability is equivalent to random pairs.** This is mechanistically expected (splice site recognition is highly nucleotide-specific) but means SpliceAI and AlphaGenome differ in what they are capturing. SpliceAI divergence within a group is not evidence that SpliceAI is wrong.
5. **Sample size is adequate for distribution characterisation** (n=145 groups) but not for per-variant conclusions.
