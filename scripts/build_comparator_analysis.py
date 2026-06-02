"""
Merge CADD + SpliceAI scores with AlphaGenome results.
Produce:
  results/comparator_analysis.csv  — full merged table
  results/rescue_analysis.csv      — three rescue groups

Run after fetch_comparator_scores.py completes.
"""

import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AG_CSV   = os.path.join(ROOT, 'results/alphagenome/alphagenome_full_cftr_results.csv')
COMP_CSV = os.path.join(ROOT, 'results/comparator_scores.csv')
OUT_CSV  = os.path.join(ROOT, 'results/comparator_analysis.csv')
RESCUE   = os.path.join(ROOT, 'results/rescue_analysis.csv')

# ── Load and merge ────────────────────────────────────────────────────────────
ag   = pd.read_csv(AG_CSV)
comp = pd.read_csv(COMP_CSV)

merged = ag.merge(
    comp[['variant_id', 'CADD_PHRED', 'SpliceAI_DS_AG', 'SpliceAI_DS_AL',
          'SpliceAI_DS_DG', 'SpliceAI_DS_DL', 'SpliceAI_max_delta']],
    on='variant_id', how='left'
)

# ── Output columns (task spec) ────────────────────────────────────────────────
cols = [
    'protein_variant', 'am_pathogenicity',
    'ATAC_quantile_max', 'SPLICE_SITE_USAGE_quantile_max', 'RNA_SEQ_quantile_max',
    'CADD_PHRED', 'SpliceAI_max_delta',
    # Keep extras for rescue analysis
    'variant_id', 'CHROM', 'POS', 'REF', 'ALT',
    'SpliceAI_DS_AG', 'SpliceAI_DS_AL', 'SpliceAI_DS_DG', 'SpliceAI_DS_DL',
    'RNA_SEQ_raw_max', 'ATAC_raw_max', 'SPLICE_SITE_USAGE_raw_max',
]
cols = [c for c in cols if c in merged.columns]
merged = merged[cols]

merged.to_csv(OUT_CSV, index=False)
print(f'Saved {len(merged)} rows to {OUT_CSV}')

# ── Rescue groups ─────────────────────────────────────────────────────────────
ATAC_Q   = 'ATAC_quantile_max'
SPLICE_Q = 'SPLICE_SITE_USAGE_quantile_max'
AM       = 'am_pathogenicity'
CADD     = 'CADD_PHRED'
SA       = 'SpliceAI_max_delta'

# Group 1: AlphaGenome rescue — high AG, low CADD, low SpliceAI
# Variants that AlphaGenome flags but neither CADD nor SpliceAI would catch
ag_rescue = merged[
    ((merged[ATAC_Q] > 0.95) | (merged[SPLICE_Q] > 0.95)) &
    (merged[CADD].fillna(0) < 20) &
    (merged[SA].fillna(0) < 0.2)
].copy()
ag_rescue['rescue_group'] = 'alphagenome_rescue'

# Group 2: Multi-tool confirmed — AlphaGenome high AND SpliceAI high
multi_confirmed = merged[
    (merged[SPLICE_Q] > 0.95) &
    (merged[SA] > 0.5)
].copy()
multi_confirmed['rescue_group'] = 'multi_tool_confirmed'

# Group 3: Discordant — AlphaGenome high SPLICE but SpliceAI low
discordant = merged[
    (merged[SPLICE_Q] > 0.95) &
    (merged[SA].fillna(0) < 0.2)
].copy()
discordant['rescue_group'] = 'discordant_ag_high_splice_low'

print(f'\nRescue groups:')
print(f'  AlphaGenome rescue (AG high, CADD<20, SpliceAI<0.2): {len(ag_rescue)}')
print(f'  Multi-tool confirmed (AG high, SpliceAI>0.5):         {len(multi_confirmed)}')
print(f'  Discordant (AG SPLICE high, SpliceAI low):            {len(discordant)}')

combined = pd.concat([ag_rescue, multi_confirmed, discordant], ignore_index=True)
combined.to_csv(RESCUE, index=False)
print(f'\nSaved {len(combined)} rows to {RESCUE}')

# ── Per-group summaries for report ────────────────────────────────────────────
print('\n=== AlphaGenome rescue — top 10 by ATAC quantile ===')
top10 = ag_rescue.sort_values(ATAC_Q, ascending=False).head(10)
print(top10[['protein_variant', AM, ATAC_Q, SPLICE_Q, CADD, SA]].to_string(index=False))

print('\n=== Multi-tool confirmed — top 10 by SpliceAI delta ===')
top_multi = multi_confirmed.sort_values(SA, ascending=False).head(10)
print(top_multi[['protein_variant', AM, ATAC_Q, SPLICE_Q, CADD, SA]].to_string(index=False))

print('\n=== Discordant — top 10 by AG SPLICE quantile ===')
top_disc = discordant.sort_values(SPLICE_Q, ascending=False).head(10)
print(top_disc[['protein_variant', AM, ATAC_Q, SPLICE_Q, CADD, SA]].to_string(index=False))

# ── Distribution stats ────────────────────────────────────────────────────────
print('\n=== Score distributions (full 1,278 variants) ===')
for col in [CADD, SA, ATAC_Q, SPLICE_Q]:
    s = merged[col].dropna()
    if len(s):
        print(f'{col}: n={len(s)}  mean={s.mean():.3f}  p25={s.quantile(0.25):.3f}  '
              f'p50={s.median():.3f}  p75={s.quantile(0.75):.3f}  p95={s.quantile(0.95):.3f}')
