"""
CHECK 20b: Rescore the first 20 variants from alphagenome_full_cftr_results.csv
using the identical scorer (RECOMMENDED_VARIANT_SCORERS['SPLICE_SITE_USAGE'],
lung UBERON:0002048) and compare raw scores and quantiles against originals.

Interpretation key:
  - Raw identical, quantile differs  → calibration update only (chr22 → genome-wide)
  - Both identical                   → already genome-wide, or change doesn't affect these
  - Raw differs                      → something else changed; stop and report
"""

import os, sys
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from alphagenome.data import genome
from alphagenome.models import dna_client
from alphagenome.models import variant_scorers as vsl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, '.env'))

API_KEY = os.environ.get('ALPHAGENOME_API_KEY', '')
if not API_KEY:
    sys.exit('ERROR: Set ALPHAGENOME_API_KEY in .env')

ORIG_CSV = os.path.join(ROOT, 'results/alphagenome/alphagenome_full_cftr_results.csv')
ONTOLOGY = 'UBERON:0002048'
SCORER   = vsl.RECOMMENDED_VARIANT_SCORERS['SPLICE_SITE_USAGE']
HALF     = dna_client.SEQUENCE_LENGTH_1MB // 2

orig = pd.read_csv(ORIG_CSV)
batch = orig.head(20).copy()

print(f"Scorer: {SCORER}")
print(f"Tissue: {ONTOLOGY}")
print(f"AlphaGenome version: 0.6.1")
print(f"Variants to rescore: {len(batch)}")
print()

model = dna_client.create(API_KEY)

variants = []
intervals = []
for _, r in batch.iterrows():
    chrom, pos_ref_alt = r['variant_id'].split(':', 1)
    pos_str, ref_alt   = pos_ref_alt.split(':', 1)
    ref, alt           = ref_alt.split('>')
    pos = int(pos_str)
    variants.append(genome.Variant(
        chromosome=chrom, position=pos,
        reference_bases=ref, alternate_bases=alt
    ))
    intervals.append(genome.Interval(
        chromosome=chrom,
        start=pos - HALF,
        end=pos + HALF
    ))

print("Submitting to API...")
raw = model.score_variants(
    intervals=intervals,
    variants=variants,
    variant_scorers=[SCORER],
    progress_bar=True,
)
tidy = vsl.tidy_scores(raw)

lung = tidy[tidy['ontology_curie'] == ONTOLOGY].copy()

# --- Comparison table ---
print(f"\n{'variant_id':<40} {'orig_raw':>14} {'new_raw':>14} {'raw_diff':>10} {'orig_q':>10} {'new_q':>10} {'q_diff':>10}")
print("-" * 110)

raw_diffs = []
q_diffs   = []

for _, r in batch.iterrows():
    vid = r['variant_id']
    pos_str = vid.split(':')[1]

    vdf = lung[lung['variant_id'].astype(str).str.contains(pos_str, regex=False)]
    splice_rows = vdf[vdf['output_type'] == 'SPLICE_SITE_USAGE']

    if splice_rows.empty:
        print(f"{vid:<40} {'NO DATA':>14}")
        continue

    new_raw = float(splice_rows['raw_score'].abs().max())
    new_q   = float(splice_rows['quantile_score'].abs().max()) if 'quantile_score' in splice_rows and splice_rows['quantile_score'].notna().any() else float('nan')

    orig_raw = float(r['SPLICE_SITE_USAGE_raw_max'])
    orig_q   = float(r['SPLICE_SITE_USAGE_quantile_max'])

    rd = new_raw - orig_raw
    qd = new_q   - orig_q
    raw_diffs.append(rd)
    q_diffs.append(qd)

    print(f"{vid:<40} {orig_raw:>14.8f} {new_raw:>14.8f} {rd:>+10.6f} {orig_q:>10.6f} {new_q:>10.6f} {qd:>+10.6f}")

print()
if raw_diffs:
    max_raw_diff = max(abs(d) for d in raw_diffs)
    max_q_diff   = max(abs(d) for d in q_diffs)
    print(f"Max |raw_diff|:      {max_raw_diff:.8f}")
    print(f"Max |quantile_diff|: {max_q_diff:.6f}")
    print(f"Mean quantile_diff:  {np.mean(q_diffs):+.6f}")
    print()
    if max_raw_diff < 1e-6:
        if max_q_diff > 0.001:
            print("INTERPRETATION: Raw scores identical, quantiles differ.")
            print("  → Calibration updated. Original quantiles used the chromosome-22 background.")
            print(f"  → All 1,278 variants in alphagenome_full_cftr_results.csv need regenerating.")
        else:
            print("INTERPRETATION: Raw scores AND quantiles identical.")
            print("  → Either our run already used genome-wide calibration, or the change")
            print("    does not affect CFTR (chromosome 7) variants.")
    else:
        print("WARNING: Raw scores differ. Something beyond calibration changed.")
        print("  → Do not proceed with document corrections for this finding.")
