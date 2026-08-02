"""
Re-query Ensembl VEP for all 766 variants with SpliceAI_max_delta == 0.0
in results/comparator_analysis.csv. Classify each as:
  GENUINE_ZERO       - VEP returned a response for this variant AND a SpliceAI record
                       was present in at least one transcript consequence, and max delta = 0.0
  NO_SPLICEAI_RECORD - VEP returned a response for this variant but no transcript
                       consequence contained a spliceai key
  VEP_ERROR          - VEP returned a non-200 HTTP status
  VARIANT_NOT_FOUND  - VEP returned 200 but the variant was absent from the response

Output: results/spliceai_zero_reclassification.csv
"""

import os
import csv
import time
import logging
import requests

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_CSV  = os.path.join(ROOT, 'results', 'comparator_analysis.csv')
OUT_CSV = os.path.join(ROOT, 'results', 'spliceai_zero_reclassification.csv')

VEP_API   = 'https://rest.ensembl.org/vep/human/region'
VEP_BATCH = 200
VEP_DELAY = 2.5
MAX_RETRY = 4
BACKOFF   = 15

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)


def vep_format(chrom, pos, ref, alt):
    c = str(chrom).replace('chr', '')
    return f"{c} {int(pos)} . {ref} {alt} . . ."


def fetch_vep_batch(batch_rows):
    variants_fmt = [vep_format(r['CHROM'], r['POS'], r['REF'], r['ALT']) for r in batch_rows]
    payload = {'variants': variants_fmt, 'SpliceAI': 1}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    for attempt in range(1, MAX_RETRY + 1):
        try:
            resp = requests.post(VEP_API, json=payload, headers=headers, timeout=120)
            if resp.status_code == 200:
                return resp.status_code, resp.json()
            elif resp.status_code in (429, 503):
                wait = BACKOFF * (2 ** (attempt - 1))
                log.warning('VEP %d on attempt %d — sleeping %ds', resp.status_code, attempt, wait)
                time.sleep(wait)
            else:
                log.error('VEP HTTP %d: %s', resp.status_code, resp.text[:200])
                return resp.status_code, []
        except Exception as e:
            log.warning('VEP request error attempt %d: %s', attempt, e)
            time.sleep(BACKOFF * attempt)
    return 0, []


def classify_batch(batch_rows, vep_data):
    # Build lookup: (pos, ref, alt) -> variant_id
    key_map = {}
    for r in batch_rows:
        key = (str(int(r['POS'])), r['REF'], r['ALT'])
        key_map[key] = r['variant_id']

    found_keys = set()
    results = {}

    for entry in vep_data:
        inp = entry.get('input', '')
        parts = inp.split()
        if len(parts) < 5:
            continue
        key = (parts[1], parts[3], parts[4])
        vid = key_map.get(key)
        if vid is None:
            continue
        found_keys.add(key)

        # Check for SpliceAI record in any transcript consequence
        best_max = -1.0
        best_sa = {}
        for tc in entry.get('transcript_consequences', []):
            if 'spliceai' in tc:
                sa = tc['spliceai']
                ds_max = max(float(sa.get(k, 0) or 0) for k in ['DS_AG', 'DS_AL', 'DS_DG', 'DS_DL'])
                if ds_max > best_max:
                    best_max = ds_max
                    best_sa = sa

        if best_max >= 0:
            # SpliceAI record was present
            results[vid] = {
                'vep_http_status': 200,
                'spliceai_record_present': 'YES',
                'ds_ag':  float(best_sa.get('DS_AG', 0) or 0),
                'ds_al':  float(best_sa.get('DS_AL', 0) or 0),
                'ds_dg':  float(best_sa.get('DS_DG', 0) or 0),
                'ds_dl':  float(best_sa.get('DS_DL', 0) or 0),
                'delta_max': best_max,
                'classification': 'GENUINE_ZERO',
            }
        else:
            # VEP responded but no spliceai key in any transcript consequence
            results[vid] = {
                'vep_http_status': 200,
                'spliceai_record_present': 'NO',
                'ds_ag': '', 'ds_al': '', 'ds_dg': '', 'ds_dl': '', 'delta_max': '',
                'classification': 'NO_SPLICEAI_RECORD',
            }

    # Variants in the batch that VEP didn't return at all
    for r in batch_rows:
        key = (str(int(r['POS'])), r['REF'], r['ALT'])
        if key not in found_keys and r['variant_id'] not in results:
            results[r['variant_id']] = {
                'vep_http_status': 200,
                'spliceai_record_present': 'NO',
                'ds_ag': '', 'ds_al': '', 'ds_dg': '', 'ds_dl': '', 'delta_max': '',
                'classification': 'VARIANT_NOT_FOUND',
            }
    return results


# Load 766 zero-delta variants
with open(IN_CSV) as f:
    all_rows = list(csv.DictReader(f))

zero_rows = [r for r in all_rows if r['SpliceAI_max_delta'] == '0.0']
log.info('Loaded %d zero-delta variants to reclassify', len(zero_rows))

out_fieldnames = [
    'variant_id', 'CHROM', 'POS', 'REF', 'ALT',
    'vep_http_status', 'spliceai_record_present',
    'ds_ag', 'ds_al', 'ds_dg', 'ds_dl', 'delta_max', 'classification',
]

all_results = {}
n = len(zero_rows)
n_batches = (n + VEP_BATCH - 1) // VEP_BATCH

for batch_num, batch_start in enumerate(range(0, n, VEP_BATCH), 1):
    batch = zero_rows[batch_start: batch_start + VEP_BATCH]
    log.info('Batch %d/%d (%d variants)', batch_num, n_batches, len(batch))
    http_status, vep_data = fetch_vep_batch(batch)

    if http_status == 0:
        # All retries failed
        for r in batch:
            all_results[r['variant_id']] = {
                'vep_http_status': 0,
                'spliceai_record_present': 'ERROR',
                'ds_ag': '', 'ds_al': '', 'ds_dg': '', 'ds_dl': '', 'delta_max': '',
                'classification': 'VEP_ERROR',
            }
    elif http_status != 200:
        for r in batch:
            all_results[r['variant_id']] = {
                'vep_http_status': http_status,
                'spliceai_record_present': 'ERROR',
                'ds_ag': '', 'ds_al': '', 'ds_dg': '', 'ds_dl': '', 'delta_max': '',
                'classification': 'VEP_ERROR',
            }
    else:
        batch_results = classify_batch(batch, vep_data)
        all_results.update(batch_results)
        gz = sum(1 for v in batch_results.values() if v['classification'] == 'GENUINE_ZERO')
        ns = sum(1 for v in batch_results.values() if v['classification'] == 'NO_SPLICEAI_RECORD')
        nf = sum(1 for v in batch_results.values() if v['classification'] == 'VARIANT_NOT_FOUND')
        log.info('  -> GENUINE_ZERO=%d  NO_SPLICEAI_RECORD=%d  VARIANT_NOT_FOUND=%d', gz, ns, nf)

    if batch_num < n_batches:
        time.sleep(VEP_DELAY)

# Write output
with open(OUT_CSV, 'w', newline='') as out:
    writer = csv.DictWriter(out, fieldnames=out_fieldnames)
    writer.writeheader()
    for r in zero_rows:
        vid = r['variant_id']
        result = all_results.get(vid, {
            'vep_http_status': '', 'spliceai_record_present': 'MISSING',
            'ds_ag': '', 'ds_al': '', 'ds_dg': '', 'ds_dl': '', 'delta_max': '',
            'classification': 'VEP_ERROR',
        })
        writer.writerow({
            'variant_id': vid, 'CHROM': r['CHROM'], 'POS': r['POS'],
            'REF': r['REF'], 'ALT': r['ALT'], **result,
        })

log.info('Saved %d rows to %s', len(zero_rows), OUT_CSV)

# Summary
from collections import Counter
counts = Counter(all_results[r['variant_id']]['classification'] for r in zero_rows if r['variant_id'] in all_results)
print('\n=== Classification summary ===')
for k, v in sorted(counts.items()):
    print(f'  {k}: {v}')
print(f'  Total: {sum(counts.values())}')
