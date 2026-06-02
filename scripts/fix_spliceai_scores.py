"""
Re-query Ensembl VEP for SpliceAI scores on all variants, using correct (pos, ref, alt)
matching to fix the position-collision bug in fetch_comparator_scores.py.

Overwrites the SpliceAI_* columns in results/comparator_scores.csv.

Run after fetch_comparator_scores.py completes.
"""

import os
import sys
import time
import logging
import requests
import numpy as np
import pandas as pd

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMP_CSV = os.path.join(ROOT, 'results/comparator_scores.csv')

VEP_API   = 'https://rest.ensembl.org/vep/human/region'
VEP_BATCH = 200
VEP_DELAY = 2.5
MAX_RETRY = 4
BACKOFF   = 15

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

if not os.path.exists(COMP_CSV):
    sys.exit(f'ERROR: {COMP_CSV} not found. Run fetch_comparator_scores.py first.')

df = pd.read_csv(COMP_CSV)
log.info('Loaded %d variants from %s', len(df), COMP_CSV)

# Reset SpliceAI columns — we will re-populate all of them correctly
for col in ['SpliceAI_DS_AG', 'SpliceAI_DS_AL', 'SpliceAI_DS_DG', 'SpliceAI_DS_DL', 'SpliceAI_max_delta']:
    df[col] = np.nan


def vep_format(row):
    chrom = str(row['CHROM']).replace('chr', '')
    return f"{chrom} {int(row['POS'])} . {row['REF']} {row['ALT']} . . ."


def fetch_vep_batch(batch_rows):
    variants_fmt = [vep_format(r) for _, r in batch_rows.iterrows()]
    payload = {'variants': variants_fmt, 'SpliceAI': 1}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    for attempt in range(1, MAX_RETRY + 1):
        try:
            r = requests.post(VEP_API, json=payload, headers=headers, timeout=120)
            if r.status_code == 200:
                return r.json()
            elif r.status_code in (429, 503):
                wait = BACKOFF * (2 ** (attempt - 1))
                log.warning('VEP %d — sleeping %ds', r.status_code, wait)
                time.sleep(wait)
            else:
                log.error('VEP HTTP %d: %s', r.status_code, r.text[:200])
                return []
        except Exception as e:
            log.warning('VEP error attempt %d: %s', attempt, e)
            time.sleep(BACKOFF * attempt)
    return []


def parse_vep(vep_data, batch_rows):
    """Match on (pos, ref, alt) to handle same-position variants correctly."""
    key_to_idx = {}
    for idx, row in batch_rows.iterrows():
        key = (str(int(row['POS'])), str(row['REF']), str(row['ALT']))
        key_to_idx[key] = idx

    results = {}
    for entry in vep_data:
        inp = entry.get('input', '')
        parts = inp.split()
        if len(parts) < 5:
            continue
        key = (parts[1], parts[3], parts[4])   # (pos, ref, alt)
        idx = key_to_idx.get(key)
        if idx is None:
            continue

        best_sa, best_max = {}, -1.0
        for tc in entry.get('transcript_consequences', []):
            if 'spliceai' in tc:
                sa = tc['spliceai']
                ds_max = max(float(sa.get(k, 0) or 0) for k in ['DS_AG', 'DS_AL', 'DS_DG', 'DS_DL'])
                if ds_max > best_max:
                    best_max, best_sa = ds_max, sa

        results[idx] = {
            'SpliceAI_DS_AG':     float(best_sa.get('DS_AG', 0) or 0),
            'SpliceAI_DS_AL':     float(best_sa.get('DS_AL', 0) or 0),
            'SpliceAI_DS_DG':     float(best_sa.get('DS_DG', 0) or 0),
            'SpliceAI_DS_DL':     float(best_sa.get('DS_DL', 0) or 0),
            'SpliceAI_max_delta': best_max if best_max >= 0 else 0.0,
        }
    return results


n = len(df)
n_batches = (n + VEP_BATCH - 1) // VEP_BATCH
log.info('Re-fetching SpliceAI for all %d variants in %d batches', n, n_batches)

all_results = {}
for batch_num, batch_start in enumerate(range(0, n, VEP_BATCH), 1):
    batch = df.iloc[batch_start: batch_start + VEP_BATCH]
    log.info('  Batch %d/%d (variants %d–%d)', batch_num, n_batches,
             batch_start + 1, min(batch_start + VEP_BATCH, n))
    vep_data = fetch_vep_batch(batch)
    batch_results = parse_vep(vep_data, batch)
    all_results.update(batch_results)
    log.info('  -> %d scores returned', len(batch_results))
    time.sleep(VEP_DELAY)

log.info('VEP complete. Got scores for %d/%d variants', len(all_results), n)

# Write scores back to DataFrame
for idx, scores in all_results.items():
    for col, val in scores.items():
        df.at[idx, col] = val

df.to_csv(COMP_CSV, index=False)
log.info('Updated %s with corrected SpliceAI scores', COMP_CSV)

print(f'\n=== SpliceAI score summary ===')
print(f'Variants with SpliceAI score: {df["SpliceAI_max_delta"].notna().sum()}')
s = df['SpliceAI_max_delta'].dropna()
print(f'Max delta: mean={s.mean():.3f}  p50={s.median():.3f}  p95={s.quantile(0.95):.3f}  '
      f'>0.2: {(s > 0.2).sum()}  >0.5: {(s > 0.5).sum()}')
