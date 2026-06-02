"""
Fetch CADD v1.7 PHRED scores and SpliceAI delta scores for all 1,278 ambiguous CFTR variants.

Sources:
  - CADD:     https://cadd.gs.washington.edu/api/v1.0/GRCh38-v1.7/
  - SpliceAI: Ensembl VEP REST API with SpliceAI plugin

Output:
  results/comparator_scores.csv  — CADD_PHRED, SpliceAI_DS_AG/AL/DG/DL, SpliceAI_max_delta per variant

Checkpoint: results/.comparator_scores_checkpoint.csv
Resumes from checkpoint if interrupted.

Run from project root:
    .venv/bin/python scripts/fetch_comparator_scores.py
"""

import os
import sys
import time
import json
import logging
import requests
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_CSV    = os.path.join(ROOT, 'results/alphagenome/alphagenome_full_cftr_results.csv')
OUTPUT_CSV   = os.path.join(ROOT, 'results/comparator_scores.csv')
CHECKPOINT   = os.path.join(ROOT, 'results/.comparator_scores_checkpoint.csv')

CADD_API     = 'https://cadd.gs.washington.edu/api/v1.0/GRCh38-v1.7/{chrom}:{pos}_{ref}_{alt}'
VEP_API      = 'https://rest.ensembl.org/vep/human/region'
VEP_BATCH    = 200   # Ensembl limit per POST
CADD_DELAY   = 0.6   # seconds between CADD requests (avoid rate limit)
VEP_DELAY    = 2.0   # seconds between VEP batch requests
MAX_RETRIES  = 4
BASE_BACKOFF = 15

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# ── Load variants ─────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_CSV)
log.info('Loaded %d variants from %s', len(df), INPUT_CSV)

# ── Resume from checkpoint ────────────────────────────────────────────────────
completed_ids = set()
if os.path.exists(CHECKPOINT):
    ckpt = pd.read_csv(CHECKPOINT)
    completed_ids = set(ckpt['variant_id'].tolist())
    log.info('Resuming — %d variants already fetched', len(completed_ids))

remaining = df[~df['variant_id'].isin(completed_ids)].reset_index(drop=True)
log.info('Remaining: %d', len(remaining))


# ── CADD single-variant fetch ─────────────────────────────────────────────────
def fetch_cadd(chrom, pos, ref, alt):
    chrom_clean = chrom.replace('chr', '') if chrom.startswith('chr') else chrom
    url = CADD_API.format(chrom=chrom_clean, pos=pos, ref=ref, alt=alt)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                data = r.json()
                if data:
                    return float(data[0]['PHRED'])
                return np.nan  # variant not in CADD precomputed
            elif r.status_code == 429:
                wait = BASE_BACKOFF * (2 ** (attempt - 1))
                log.warning('CADD rate limit — sleeping %ds', wait)
                time.sleep(wait)
            else:
                log.warning('CADD HTTP %d for %s:%s_%s_%s', r.status_code, chrom, pos, ref, alt)
                return np.nan
        except Exception as e:
            log.warning('CADD error attempt %d: %s', attempt, e)
            time.sleep(BASE_BACKOFF)
    return np.nan


# ── SpliceAI via Ensembl VEP batch ───────────────────────────────────────────
def vep_format(row):
    """Convert a variant row to Ensembl VEP region format: '7 pos . REF ALT . . .'"""
    chrom = str(row['CHROM']).replace('chr', '')
    return f"{chrom} {int(row['POS'])} . {row['REF']} {row['ALT']} . . ."

def fetch_spliceai_batch(batch_rows):
    """
    Submit a batch of variants to Ensembl VEP and extract SpliceAI scores.
    Returns dict: variant_id -> {DS_AG, DS_AL, DS_DG, DS_DL, max_delta}
    """
    variants_fmt = [vep_format(r) for _, r in batch_rows.iterrows()]
    payload = {'variants': variants_fmt, 'SpliceAI': 1}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(VEP_API, json=payload, headers=headers, timeout=120)
            if r.status_code == 200:
                return _parse_vep_response(r.json(), batch_rows)
            elif r.status_code == 429 or r.status_code == 503:
                wait = BASE_BACKOFF * (2 ** (attempt - 1))
                log.warning('VEP rate limit/unavailable — sleeping %ds', wait)
                time.sleep(wait)
            else:
                log.error('VEP HTTP %d (attempt %d): %s', r.status_code, attempt, r.text[:200])
                return {}
        except Exception as e:
            log.warning('VEP error attempt %d: %s', attempt, e)
            time.sleep(BASE_BACKOFF * attempt)
    return {}


def _parse_vep_response(vep_data, batch_rows):
    """
    Parse VEP response and match SpliceAI scores back to variant_ids.
    VEP 'input' field is the exact VCF line submitted: 'CHROM POS . REF ALT . . .'
    Match on (pos, ref, alt) to handle multiple variants at the same position.
    """
    # Build (pos, ref, alt) -> variant_id map
    key_to_vid = {}
    for _, row in batch_rows.iterrows():
        key = (str(int(row['POS'])), str(row['REF']), str(row['ALT']))
        key_to_vid[key] = row['variant_id']

    results = {}
    for entry in vep_data:
        inp = entry.get('input', '')
        parts = inp.split()
        if len(parts) < 5:
            continue
        # VCF columns: CHROM POS ID REF ALT ...
        pos_str, ref_str, alt_str = parts[1], parts[3], parts[4]
        vid = key_to_vid.get((pos_str, ref_str, alt_str))
        if vid is None:
            continue

        # Collect max SpliceAI score across all transcript_consequences
        best_sa = {}
        best_max = -1.0
        for tc in entry.get('transcript_consequences', []):
            if 'spliceai' in tc:
                sa = tc['spliceai']
                ds_max = max(float(sa.get(k, 0) or 0) for k in ['DS_AG', 'DS_AL', 'DS_DG', 'DS_DL'])
                if ds_max > best_max:
                    best_max = ds_max
                    best_sa = sa

        ds_ag = float(best_sa.get('DS_AG', 0) or 0)
        ds_al = float(best_sa.get('DS_AL', 0) or 0)
        ds_dg = float(best_sa.get('DS_DG', 0) or 0)
        ds_dl = float(best_sa.get('DS_DL', 0) or 0)
        max_ds = max(ds_ag, ds_al, ds_dg, ds_dl)

        results[vid] = {
            'SpliceAI_DS_AG':     ds_ag,
            'SpliceAI_DS_AL':     ds_al,
            'SpliceAI_DS_DG':     ds_dg,
            'SpliceAI_DS_DL':     ds_dl,
            'SpliceAI_max_delta': max_ds,
        }
    return results


# ── Main loop ─────────────────────────────────────────────────────────────────
all_rows = []
n = len(remaining)

# --- Step A: Fetch CADD scores one by one ---
log.info('=== STEP A: Fetching CADD scores for %d variants ===', n)
cadd_scores = {}

for i, (_, row) in enumerate(remaining.iterrows(), 1):
    vid = row['variant_id']
    phred = fetch_cadd(row['CHROM'], int(row['POS']), row['REF'], row['ALT'])
    cadd_scores[vid] = phred
    if i % 50 == 0:
        log.info('  CADD: %d/%d done', i, n)
    time.sleep(CADD_DELAY)

log.info('CADD fetch complete. Found scores for %d/%d variants',
         sum(1 for v in cadd_scores.values() if not np.isnan(v)), n)

# --- Step B: Fetch SpliceAI scores in batches via Ensembl VEP ---
log.info('=== STEP B: Fetching SpliceAI scores in batches of %d ===', VEP_BATCH)
spliceai_scores = {}

for batch_start in range(0, n, VEP_BATCH):
    batch = remaining.iloc[batch_start: batch_start + VEP_BATCH]
    batch_num = batch_start // VEP_BATCH + 1
    total_batches = (n + VEP_BATCH - 1) // VEP_BATCH
    log.info('  VEP batch %d/%d (variants %d-%d)', batch_num, total_batches,
             batch_start + 1, min(batch_start + VEP_BATCH, n))

    batch_results = fetch_spliceai_batch(batch)
    spliceai_scores.update(batch_results)
    log.info('  -> %d scores returned in this batch', len(batch_results))
    time.sleep(VEP_DELAY)

log.info('SpliceAI fetch complete. Found scores for %d/%d variants', len(spliceai_scores), n)

# --- Step C: Combine into result rows ---
log.info('=== STEP C: Assembling results ===')
for _, row in remaining.iterrows():
    vid = row['variant_id']
    sa = spliceai_scores.get(vid, {})
    new_row = {
        'variant_id':          vid,
        'CHROM':               row['CHROM'],
        'POS':                 row['POS'],
        'REF':                 row['REF'],
        'ALT':                 row['ALT'],
        'CADD_PHRED':          cadd_scores.get(vid, np.nan),
        'SpliceAI_DS_AG':      sa.get('SpliceAI_DS_AG', np.nan),
        'SpliceAI_DS_AL':      sa.get('SpliceAI_DS_AL', np.nan),
        'SpliceAI_DS_DG':      sa.get('SpliceAI_DS_DG', np.nan),
        'SpliceAI_DS_DL':      sa.get('SpliceAI_DS_DL', np.nan),
        'SpliceAI_max_delta':  sa.get('SpliceAI_max_delta', np.nan),
    }
    all_rows.append(new_row)

new_df = pd.DataFrame(all_rows)

# Merge with checkpoint if resuming
if os.path.exists(CHECKPOINT) and len(completed_ids) > 0:
    ckpt_df = pd.read_csv(CHECKPOINT)
    final_scores = pd.concat([ckpt_df, new_df], ignore_index=True)
else:
    final_scores = new_df

final_scores = final_scores.drop_duplicates(subset='variant_id').reset_index(drop=True)
final_scores.to_csv(CHECKPOINT, index=False)
final_scores.to_csv(OUTPUT_CSV, index=False)
log.info('Saved %d rows to %s', len(final_scores), OUTPUT_CSV)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f'\n=== CADD Summary ===')
print(f'Variants with CADD score: {final_scores["CADD_PHRED"].notna().sum()}')
print(f'PHRED mean: {final_scores["CADD_PHRED"].mean():.1f}  '
      f'PHRED >=20: {(final_scores["CADD_PHRED"] >= 20).sum()}  '
      f'PHRED >=30: {(final_scores["CADD_PHRED"] >= 30).sum()}')

print(f'\n=== SpliceAI Summary ===')
print(f'Variants with SpliceAI score: {final_scores["SpliceAI_max_delta"].notna().sum()}')
print(f'Max delta mean: {final_scores["SpliceAI_max_delta"].mean():.3f}  '
      f'>0.2: {(final_scores["SpliceAI_max_delta"] > 0.2).sum()}  '
      f'>0.5: {(final_scores["SpliceAI_max_delta"] > 0.5).sum()}')

print(f'\nDone. Output: {OUTPUT_CSV}')
