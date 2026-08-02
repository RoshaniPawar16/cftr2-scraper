"""
Build the Phase 1 benchmark cohort.

Inputs (all must exist before running):
  data/cftr2_results_annotated.csv        — AM scores + CFTR2 labels
  data/All_Variants_VEP.Gene.vcf          — SIFT / PolyPhen via CSQ field
  results/phase1/inputs_cadd_scores.csv   — produced by phase1_fetch_cadd.py

Outputs:
  results/phase1/inputs_cftr2_labels.csv  — 292-variant label table
  results/phase1/inputs_polyphen_sift.csv — SIFT and PolyPhen per variant
  results/phase1/benchmark_cohort.csv     — fully merged cohort
  results/phase1/SOURCE.md                — input file checksums

benchmark_cohort.csv columns:
  variant, determination_2026, label, am_pathogenicity,
  cadd_phred, polyphen_score, sift_score_inv,
  included, exclusion_reason

included=True: variant enters the final benchmark.
included=False: excluded — exclusion_reason says why.
All 292 variants are present in the file regardless of inclusion.
"""

import os, re, csv, hashlib, logging
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR       = os.path.join(ROOT, 'results', 'phase1')
ANNOT_CSV     = os.path.join(ROOT, 'data', 'cftr2_results_annotated.csv')
VCF_PATH      = os.path.join(ROOT, 'data', 'All_Variants_VEP.Gene.vcf')
CADD_CSV      = os.path.join(ROOT, 'results', 'phase1', 'inputs_cadd_scores.csv')
LABELS_CSV    = os.path.join(ROOT, 'results', 'phase1', 'inputs_cftr2_labels.csv')
PS_CSV        = os.path.join(ROOT, 'results', 'phase1', 'inputs_polyphen_sift.csv')
COHORT_CSV    = os.path.join(ROOT, 'results', 'phase1', 'benchmark_cohort.csv')
SOURCE_MD     = os.path.join(ROOT, 'results', 'phase1', 'SOURCE.md')

# CSQ field indices (0-based within the pipe-separated CSQ string)
HGVSP_IDX    = 11
SIFT_IDX     = 31
POLYPHEN_IDX = 32

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)
os.makedirs(OUT_DIR, exist_ok=True)


def sha256_hex(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


# ── Step 1: extract CFTR2 binary labels ──────────────────────────────────────
with open(ANNOT_CSV) as f:
    annotated = list(csv.DictReader(f))

binary = [r for r in annotated
          if r['determination_2026'] in ('CF-causing', 'Non CF-causing')
          and r['am_pathogenicity']]

log.info('Binary variants from cftr2_results_annotated.csv: %d', len(binary))
cf_count  = sum(1 for r in binary if r['determination_2026'] == 'CF-causing')
nc_count  = len(binary) - cf_count
log.info('  CF-causing: %d  Non-CF-causing: %d', cf_count, nc_count)

with open(LABELS_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['variant', 'protein_name', 'legacy_name',
                                      'determination_2026', 'label',
                                      'am_pathogenicity', 'am_class'])
    w.writeheader()
    for r in binary:
        label = 1 if r['determination_2026'] == 'CF-causing' else 0
        w.writerow({'variant': r['variant'],
                    'protein_name': r.get('protein_name', ''),
                    'legacy_name': r.get('legacy_name', ''),
                    'determination_2026': r['determination_2026'],
                    'label': label,
                    'am_pathogenicity': r['am_pathogenicity'],
                    'am_class': r.get('am_class', '')})
log.info('Saved %s', LABELS_CSV)

# ── Step 2: parse SIFT and PolyPhen from VCF ─────────────────────────────────
protein_re = re.compile(r'p\.([A-Z][a-z]{2}\d+[A-Z][a-z]{2})')
csq_re     = re.compile(r'CSQ=([^;]+)')

sift_re    = re.compile(r'\(([0-9.]+)\)')
pp_re      = re.compile(r'\(([0-9.]+)\)')

variant_scores = {}   # protein_variant -> {'sift': str, 'polyphen': str}

with open(VCF_PATH, encoding='utf-8', errors='replace') as fh:
    for line in fh:
        if line.startswith('#'):
            continue
        csq_m = csq_re.search(line)
        if not csq_m:
            continue
        for transcript in csq_m.group(1).split(','):
            fields = transcript.split('|')
            if len(fields) <= POLYPHEN_IDX:
                continue
            hgvsp_field   = fields[HGVSP_IDX]
            sift_field    = fields[SIFT_IDX]
            polyphen_field = fields[POLYPHEN_IDX]
            if not sift_field and not polyphen_field:
                continue
            m = protein_re.search(hgvsp_field)
            if m:
                pv = m.group(1)
                if pv not in variant_scores and (sift_field or polyphen_field):
                    variant_scores[pv] = {'sift': sift_field, 'polyphen': polyphen_field}

log.info('VCF: extracted SIFT/PolyPhen for %d protein variants', len(variant_scores))


def parse_sift_inv(s):
    """Return 1 - SIFT (higher = more damaging), or None."""
    m = sift_re.search(s or '')
    return round(1.0 - float(m.group(1)), 6) if m else None


def parse_polyphen(s):
    """Return PolyPhen score (higher = more damaging), or None."""
    m = pp_re.search(s or '')
    return round(float(m.group(1)), 6) if m else None


with open(PS_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['variant', 'sift_raw', 'sift_score_inv', 'polyphen_raw', 'polyphen_score'])
    w.writeheader()
    for variant_name, s in variant_scores.items():
        w.writerow({'variant': variant_name,
                    'sift_raw': s['sift'],
                    'sift_score_inv': parse_sift_inv(s['sift']),
                    'polyphen_raw': s['polyphen'],
                    'polyphen_score': parse_polyphen(s['polyphen'])})
log.info('Saved %s', PS_CSV)

# ── Step 3: load CADD scores ──────────────────────────────────────────────────
with open(CADD_CSV) as f:
    cadd_rows = list(csv.DictReader(f))
cadd_by_variant = {r['variant']: r['cadd_phred'] for r in cadd_rows}
log.info('CADD scores loaded: %d', sum(1 for v in cadd_by_variant.values() if v))

# ── Step 4: build merged cohort ───────────────────────────────────────────────
cohort = []
merge_log = {'total': 0, 'missing_cadd': 0, 'missing_sift': 0,
             'missing_polyphen': 0, 'included': 0}

for r in binary:
    v = r['variant']
    merge_log['total'] += 1

    cadd_val = cadd_by_variant.get(v, '')
    cadd_phred = float(cadd_val) if cadd_val not in ('', None) else None

    ps_data = variant_scores.get(v, {})
    sift_inv = parse_sift_inv(ps_data.get('sift', ''))
    pp_score = parse_polyphen(ps_data.get('polyphen', ''))

    missing = []
    if cadd_phred is None:
        missing.append('cadd')
        merge_log['missing_cadd'] += 1
    if sift_inv is None:
        missing.append('sift')
        merge_log['missing_sift'] += 1
    if pp_score is None:
        missing.append('polyphen')
        merge_log['missing_polyphen'] += 1

    included = len(missing) == 0
    if included:
        merge_log['included'] += 1

    cohort.append({
        'variant': v,
        'determination_2026': r['determination_2026'],
        'label': 1 if r['determination_2026'] == 'CF-causing' else 0,
        'am_pathogenicity': r['am_pathogenicity'],
        'cadd_phred': '' if cadd_phred is None else cadd_phred,
        'polyphen_score': '' if pp_score is None else pp_score,
        'sift_score_inv': '' if sift_inv is None else sift_inv,
        'included': included,
        'exclusion_reason': 'missing_' + '+'.join(missing) if missing else '',
    })

log.info('Cohort merge summary:')
log.info('  Total: %d', merge_log['total'])
log.info('  Missing CADD: %d', merge_log['missing_cadd'])
log.info('  Missing SIFT: %d', merge_log['missing_sift'])
log.info('  Missing PolyPhen: %d', merge_log['missing_polyphen'])
log.info('  Included (all four scores): %d', merge_log['included'])

# Count exclusions by reason
from collections import Counter
exclusion_counts = Counter(r['exclusion_reason'] for r in cohort if not r['included'])
if exclusion_counts:
    log.info('  Exclusion reasons: %s', dict(exclusion_counts))

with open(COHORT_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['variant', 'determination_2026', 'label',
                                      'am_pathogenicity', 'cadd_phred',
                                      'polyphen_score', 'sift_score_inv',
                                      'included', 'exclusion_reason'])
    w.writeheader()
    w.writerows(cohort)
log.info('Saved %s', COHORT_CSV)

# ── Step 5: write SOURCE.md ───────────────────────────────────────────────────
inputs = [
    ('data/AlphaMissense_hg38.tsv.gz', 'AlphaMissense scores (Zenodo 8208688), filtered to CFTR (P13569) via cftr_alphamissense.tsv'),
    ('data/cftr2_results_annotated.csv', 'CFTR2 Jan 2026 release merged with AM scores; source of binary labels and AM pathogenicity'),
    ('data/All_Variants_VEP.Gene.vcf', 'VEP-annotated VCF; source of SIFT and PolyPhen scores via CSQ field (indices 31, 32)'),
    ('data/cftr_alphamissense.tsv', 'CFTR-filtered AlphaMissense scores from AlphaMissense_hg38.tsv.gz'),
]
with open(SOURCE_MD, 'w') as f:
    f.write('# Phase 1 Input Sources\n\n')
    f.write('| file | sha256 (full) | description |\n')
    f.write('|---|---|---|\n')
    for rel_path, desc in inputs:
        abs_path = os.path.join(ROOT, rel_path)
        try:
            chk = sha256_hex(abs_path)
        except FileNotFoundError:
            chk = 'FILE_NOT_FOUND'
        f.write(f'| {rel_path} | {chk} | {desc} |\n')
    f.write(f'\n| results/phase1/inputs_cadd_raw.json | {sha256_hex(os.path.join(ROOT, "results/phase1/inputs_cadd_raw.json"))} | Raw CADD API responses before parsing |\n')
log.info('Saved %s', SOURCE_MD)

print(f'\n=== Cohort summary ===')
print(f'Total binary variants: {merge_log["total"]}')
print(f'Missing CADD: {merge_log["missing_cadd"]}')
print(f'Missing SIFT: {merge_log["missing_sift"]}')
print(f'Missing PolyPhen: {merge_log["missing_polyphen"]}')
print(f'INCLUDED (all four scores present): {merge_log["included"]}')
if exclusion_counts:
    print('Exclusion detail:', dict(exclusion_counts))
    exc_variants = [r['variant'] for r in cohort if not r['included']]
    print('Excluded variants:', exc_variants)
