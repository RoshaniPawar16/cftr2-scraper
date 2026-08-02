"""
Fetch CADD v1.7 PHRED scores for the 292 binary CFTR variants.

Saves raw API responses to results/phase1/inputs_cadd_raw.json (one JSON
object per variant, keyed by variant name) before parsing. Parsed scores
are written to results/phase1/inputs_cadd_scores.csv.

Run ONCE; re-running will overwrite both files.

Source: CADD v1.7 GRCh38 REST API — https://cadd.gs.washington.edu/api
"""

import os, re, json, time, logging
import csv
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR      = os.path.join(ROOT, 'results', 'phase1')
ANNOT_CSV    = os.path.join(ROOT, 'data', 'cftr2_results_annotated.csv')
VCF_PATH     = os.path.join(ROOT, 'data', 'All_Variants_VEP.Gene.vcf')
RAW_JSON     = os.path.join(ROOT, 'results', 'phase1', 'inputs_cadd_raw.json')
SCORES_CSV   = os.path.join(ROOT, 'results', 'phase1', 'inputs_cadd_scores.csv')

CADD_URL    = 'https://cadd.gs.washington.edu/api/v1.0/GRCh38-v1.7/{chrom}:{pos}_{ref}_{alt}'
REQUEST_DELAY = 0.35   # seconds between requests to respect rate limit

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

os.makedirs(OUT_DIR, exist_ok=True)

# ── Load 292 binary variants ──────────────────────────────────────────────────
with open(ANNOT_CSV) as f:
    annotated = list(csv.DictReader(f))

binary = [r for r in annotated
          if r['determination_2026'] in ('CF-causing', 'Non CF-causing')
          and r['am_pathogenicity']]
log.info('Binary variants: %d', len(binary))

# ── Extract genomic coordinates from VCF ─────────────────────────────────────
protein_re = re.compile(r'p\.([A-Z][a-z]{2}\d+[A-Z][a-z]{2})')
coords = {}

with open(VCF_PATH, encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'):
            continue
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 5:
            continue
        chrom, pos, _, ref, alt = parts[0], parts[1], parts[2], parts[3], parts[4]
        m = protein_re.search(line)
        if m and m.group(1) not in coords:
            coords[m.group(1)] = {'chrom': chrom, 'pos': pos, 'ref': ref, 'alt': alt}

log.info('VCF coordinates extracted: %d unique protein variants', len(coords))

# ── Fetch CADD scores ─────────────────────────────────────────────────────────
def fetch_cadd(chrom, pos, ref, alt):
    url = CADD_URL.format(chrom=chrom, pos=pos, ref=ref, alt=alt)
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return resp.status_code, data
        return resp.status_code, []
    except Exception as e:
        return 0, {'error': str(e)}

raw_responses = {}
scores_out = []
no_coord = []
no_cadd = []

for i, row in enumerate(binary, 1):
    variant_name = row['variant']   # three-letter format: Ser13Phe
    # The VCF uses three-letter format matching cftr2_results_annotated.csv variant column
    coord = coords.get(variant_name)

    if coord is None:
        no_coord.append(variant_name)
        raw_responses[variant_name] = {'error': 'no_vcf_coordinate'}
        scores_out.append({'variant': variant_name,
                           'determination_2026': row['determination_2026'],
                           'am_pathogenicity': row['am_pathogenicity'],
                           'cadd_phred': '',
                           'exclusion_reason': 'no_vcf_coordinate'})
        continue

    status, data = fetch_cadd(coord['chrom'], coord['pos'], coord['ref'], coord['alt'])
    raw_responses[variant_name] = {'status': status, 'data': data,
                                    'coord': coord}

    phred = None
    if status == 200 and isinstance(data, list) and len(data) > 0:
        entry = data[0]
        if isinstance(entry, dict) and 'PHRED' in entry:
            phred = float(entry['PHRED'])

    if phred is None:
        no_cadd.append(variant_name)
        reason = f'cadd_api_no_score_http{status}'
    else:
        reason = ''

    scores_out.append({'variant': variant_name,
                       'determination_2026': row['determination_2026'],
                       'am_pathogenicity': row['am_pathogenicity'],
                       'cadd_phred': phred if phred is not None else '',
                       'exclusion_reason': reason})

    if i % 20 == 0:
        log.info('  %d / %d done', i, len(binary))

    time.sleep(REQUEST_DELAY)

log.info('CADD fetch complete. Scored: %d / %d  No coord: %d  No score: %d',
         sum(1 for r in scores_out if r['cadd_phred'] != ''),
         len(binary), len(no_coord), len(no_cadd))

# ── Save raw responses ─────────────────────────────────────────────────────────
with open(RAW_JSON, 'w') as f:
    json.dump(raw_responses, f, indent=2)
log.info('Raw responses saved to %s', RAW_JSON)

# ── Save parsed scores ─────────────────────────────────────────────────────────
with open(SCORES_CSV, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['variant', 'determination_2026',
                                           'am_pathogenicity', 'cadd_phred',
                                           'exclusion_reason'])
    writer.writeheader()
    writer.writerows(scores_out)
log.info('Parsed CADD scores saved to %s', SCORES_CSV)

if no_coord:
    log.warning('No VCF coordinate for: %s', no_coord)
if no_cadd:
    log.warning('No CADD score for: %s', no_cadd)
