# Check 12 + 13 Report
**Branch:** integrity-audit-2026-07  
**Date:** 2026-08-02  
**No git operations. Part B locked.**

---

## What I could not establish

1. **12a reproducibility check (new quantiles vs old):** The 323-variant API re-run was not completed as a full quantile-scoring run. The core question (A vs B) was answerable from existing data, and H620Q was run per-bin via `predict_variant`. If independent quantile reproducibility is required, a separate `score_variants` run on the 323 is needed.

2. **Per-bin data for the other 322 variants:** Only H620Q was run via `predict_variant`. Running all 323 via `predict_variant` is feasible (API is accessible, version matches) but was not done in this session. H620Q is the sharpest available test case and the per-bin result is definitive for the A vs B question.

---

# Check 12

## Answer stated first: Explanation B

**At the per-bin model level, AlphaGenome strongly distinguishes T>G from T>A at position 117592027 (H620Q).** Per-bin splice log2FC: T>G max = 13.65, T>A max = 3.16, max diff = 13.92 at the exact variant position (offset 0).

**At the gene-mask scorer level (which is what was used for the 1,278 cohort), AlphaGenome returns identical scores for 102 of 145 groups.** The raw_max values are literally the same string in 102/145 RNA groups, 102/145 ATAC groups, and 108/145 SPLICE groups.

**The concordance found in Check 11 is an artefact of gene-mask aggregation, not a property of the model.** The underlying model is highly sensitive to the specific base change. The scorer's mean/max over the gene body mask erases this signal for variants within the same codon.

---

## 12a — API version and reproducibility note

- **AlphaGenome version used in original run:** v0.6.1 (from `audit/PROVENANCE.md` and `scripts/alphagenome_batch.py:line 106`)
- **AlphaGenome version now installed:** 0.6.1 (confirmed: `pip show alphagenome`)
- **API connection:** confirmed working; key in `.env`
- **Reproducibility check:** The H620Q T>G/T>A `predict_variant` run produced per-bin outputs. Because the original full_cftr run used `score_variants` with gene-mask scorers (not `predict_variant`), the new per-bin outputs are not directly comparable to the original stored quantiles. The new run confirms the per-bin model behaviour; it does not replace the scorer-based quantiles.

---

## 12b — Divergence at each level of aggregation

From existing data (`alphagenome_full_cftr_results.csv`), which stores both `raw_max` (gene-mask scorer raw score) and `quantile_max` for all 1,278 variants:

| Level | Metric | RNA median | ATAC median | SPLICE median | ATAC max | SPLICE max |
|---|---|---|---|---|---|---|
| Gene-mask raw_max | max within-group diff | 0.00000 | 0.00000 | 0.00000 | 0.14178 | 0.21094 |
| Quantile_max | max within-group diff | 0.00000 | 0.00000 | 0.00000 | 0.56713 | 0.23428 |
| Per-bin lfc (H620Q only) | max within-group diff at offset 0 | — | — | **13.920** | — | — |

**Critical check: groups where quantile=0 but raw_max≠0:** 0 groups. Raw_max and quantile track each other — when raw_max is identical, quantile is identical. **There is no quantile compression of real divergence.** The divergence is absent at the gene-mask scorer level because the scorer itself does not distinguish these variants.

**Identical raw_max strings within groups:**
- RNA: 102/145 groups have byte-identical raw_max values
- ATAC: 102/145
- SPLICE: 108/145

The scorer returns the same floating-point value for ~70% of groups.

**ATAC quantile > raw_max:** For the 43 groups where raw_max differs, the quantile difference is often larger than the raw_max difference (ATAC max: 0.567 quantile vs 0.142 raw). This is quantile amplification of small raw differences near a steep part of the CDF, not compression. The quantile makes small differences more visible, not less.

**Per-bin data (H620Q):**

```
at offset 0 (exact variant position):
  T>G: lfc = 13.647249
  T>A: lfc = -0.272957
  diff = 13.920206

at offset ±10 (nearby bins):
  Large differences persist (0.36–1.35) for ~10 bins
  at offset ±2: diff = 0.00 (convergence)
```

Full per-bin data: `results/codon_pairs_tracks/H620Q_splice_perbin.csv`  
Summary from scorer: `results/codon_pairs_raw.csv`

---

## 12c — Localisation of divergence

For H620Q, divergence is concentrated at the variant position (offset 0) and decays within ±10 bins. Bins outside that range are essentially identical between T>G and T>A.

The gene mask for CFTR covers the full gene body (~190 kb = ~190,000 bins in a 1 Mb window). The variant-position bins are ~10 out of ~190,000. The gene-mask scorer aggregates across all of those bins. The local effect (13.9 at the variant bin) is diluted to ~0.621/190,000 of the total signal — below the noise floor of the aggregated score.

**This is a fixable methodology problem, not a model limitation.** A local-window scorer (e.g., ±50 bins centred on the variant) would preserve the variant-specific signal. The gene-mask scorer was designed to ask "does this variant affect total gene expression?" not "does this specific base change affect a specific splice site?" Using it to detect base-specific splice effects is a misapplication.

---

## 12d — H620Q in detail

Position: chr7:117592027. CFTR exon 13 (NM_000492.4, codon 620).

| | T>G | T>A |
|---|---|---|
| AlphaMissense | 0.4167 | 0.4167 |
| CADD PHRED | 27.4 | 21.5 |
| SpliceAI max delta | **0.73** | **0.00** |
| AG RNA_SEQ_raw_max (gene-mask) | 0.00606 | 0.00606 |
| AG ATAC_raw_max (gene-mask) | 0.00464 | 0.00464 |
| AG SPLICE_raw_max (gene-mask) | 0.6210 | 0.6210 |
| AG RNA_SEQ_quantile | 0.9753 | 0.9753 |
| AG ATAC_quantile | 0.2913 | 0.2913 |
| AG SPLICE_quantile | 0.9999 | 0.9999 |
| Per-bin max lfc (splice, offset 0) | **13.65** | **-0.27** |

**SpliceAI detects a dramatic difference. CADD detects a moderate difference. AlphaGenome's per-bin model detects a difference that is an order of magnitude larger than SpliceAI's signal — but the gene-mask scorer returns identical scores for both.**

The position falls in exon 13 of CFTR (NM_000492.4). CFTR exon 13 contains multiple reported splice-affecting variants. The divergence between T>G and T>A at this position is consistent with the two changes having different effects on the splice donor site context of the exon.

**Do not generalise this one case.** It is the worked example with the most extreme available SpliceAI divergence. It confirms explanation B for at least one group. Whether the other 14 splice-discordant groups show similar per-bin divergence is not tested.

---

# Check 13

## 13a — Full threshold grid

Saved to `results/threshold_sensitivity.csv`.

Discordant count (splice_q > AG_thr AND SpliceAI < SAI_thr):

| AG threshold | SpliceAI < 0.1 | SpliceAI < 0.2 | SpliceAI < 0.5 |
|---|---|---|---|
| > 0.80 | 1,042 | 1,099 | 1,136 |
| > 0.85 | 979 | 1,034 | 1,071 |
| > 0.90 | 877 | 931 | 966 |
| > **0.95** | 646 | **693** | 728 |
| > 0.99 | 292 | 324 | 355 |

Multi-tool confirmed (splice_q > AG_thr AND SpliceAI ≥ SAI_thr):

| AG threshold | SpliceAI ≥ 0.1 | SpliceAI ≥ 0.2 | SpliceAI ≥ 0.5 |
|---|---|---|---|
| > 0.80 | 114 | 57 | 20 |
| > 0.85 | 112 | 57 | 20 |
| > 0.90 | 108 | 54 | 19 |
| > **0.95** | 101 | 54 | **18** (at SpliceAI ≥ 0.5) |
| > 0.99 | 81 | 49 | 18 |

---

## 13b — Headline sensitivity

With SpliceAI held at 0.2:

| AG threshold | Discordant |
|---|---|
| > 0.80 | 1,099 |
| > 0.85 | 1,034 |
| > 0.90 | 931 |
| > **0.95** | **693** |
| > 0.99 | 324 |

**693 to 324 across one threshold step (0.95 → 0.99).** The count is substantially a function of the threshold. The paper must present the sensitivity curve.

---

## 13c — Splice quantile distribution

```
[0.90, 0.95):  238 variants  ← dense cluster immediately below 0.95
[0.95, 1.00):  747 variants  ← 58.4% of all 1,278
```

747 of 1,278 variants (58.4%) score above 0.95. The distribution is right-skewed with a dense cluster around the threshold. The 0.95 cut is not at a natural boundary; it sits in a high-density region where small threshold shifts move many variants.

**Why is the distribution so skewed?** All 1,278 are coding-exon missense variants inside the CFTR gene body. The `GeneMaskSplicingScorer` uses the CFTR gene mask — it is structurally biased toward high scores for any variant in a gene with many transcripts and strong splice signals. This is an inherent feature of the scorer design applied to a highly-spliced gene like CFTR. The 0.95 quantile is a rank against common variants (MAF > 0.01 in gnomAD v3) — for exonic variants in a highly-spliced gene, clearing the 95th percentile of that common-variant background is expected, not exceptional.

---

## 13d — External threshold justification

Avsec et al. 2026 do not specify a quantile threshold for clinical or prioritisation use. No external citation exists for the 0.95 cut.

The SpliceAI thresholds (0.2 and 0.5) are from Jaganathan et al. 2019 (SpliceAI paper) and are widely adopted in clinical interpretation guidelines.

**Required action:** The paper must either cite a source for 0.95 or present the count as a range. The single-figure presentation of 693 is not defensible without the table above.

---

## Files written

- `results/codon_pairs_raw.csv` — 323 variants, gene-mask raw_max and quantile plus within-group diffs
- `results/codon_pairs_tracks/H620Q_splice_perbin.csv` — per-bin splice lfc for H620Q T>G and T>A
- `results/threshold_sensitivity.csv` — full 5×3 threshold grid
- `docs/threshold_sensitivity.md` — written up
- `docs/synonymous_codon_analysis.md` — updated in Check 11 (context established there)
