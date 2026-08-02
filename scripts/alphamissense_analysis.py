"""
AlphaMissense CFTR validation analysis.

Executable replacement for notebooks/alphamissense.ipynb.
That notebook is out-of-sequence and cannot be trusted as a reproducibility record.
This script runs top-to-bottom from committed inputs.

Inputs (must exist on disk):
  data/cftr2_results_annotated.csv   — CFTR2 labels + AM scores (3716 rows)
  data/cftr_alphamissense.tsv        — CFTR-filtered AM scores from Zenodo 8208688
  data/All_Variants_VEP.Gene.vcf     — for gnomAD AF and SIFT/PolyPhen
  data/varying_consequence_am.csv    — VCC variants with AM scores (72 rows, cftr2_results.csv snapshot)

Outputs:
  results/phase1/am_validation_metrics.csv   — AUC, AP, MCC, classification metrics
  results/phase1/am_vcc_analysis.csv         — varying clinical consequence breakdown
  results/phase1/am_domain_analysis.csv      — domain distribution of VCC likely pathogenic
  results/phase1/am_unclassified_counts.csv  — counts of AM classes in unclassified set

NOTE on two CFTR2 snapshots:
  data/cftr2_results_annotated.csv (this file, used for benchmark) has 82 VCC variants.
  data/cftr2_results.csv (smaller snapshot) has 72 VCC variants.
  data/varying_consequence_am.csv was derived from cftr2_results.csv (72 VCC).
  These snapshots differ; the documented figure of 72 VCC reflects cftr2_results.csv.
  This script reports both counts and flags the discrepancy.
"""

import os, re, csv, logging
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR      = os.path.join(ROOT, 'results', 'phase1')
ANNOT_CSV    = os.path.join(ROOT, 'data', 'cftr2_results_annotated.csv')
VCC_CSV      = os.path.join(ROOT, 'data', 'varying_consequence_am.csv')
METRICS_OUT  = os.path.join(ROOT, 'results', 'phase1', 'am_validation_metrics.csv')
VCC_OUT      = os.path.join(ROOT, 'results', 'phase1', 'am_vcc_analysis.csv')
DOMAIN_OUT   = os.path.join(ROOT, 'results', 'phase1', 'am_domain_analysis.csv')
UNCLASS_OUT  = os.path.join(ROOT, 'results', 'phase1', 'am_unclassified_counts.csv')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load annotated dataset ────────────────────────────────────────────────────
with open(ANNOT_CSV) as f:
    annotated = list(csv.DictReader(f))
log.info('Loaded cftr2_results_annotated.csv: %d rows', len(annotated))

# ── Validation cohort: binary classification ──────────────────────────────────
binary = [r for r in annotated
          if r['determination_2026'] in ('CF-causing', 'Non CF-causing')
          and r['am_pathogenicity']]

log.info('Binary variants: %d', len(binary))
n_cf = sum(1 for r in binary if r['determination_2026'] == 'CF-causing')
n_nc = len(binary) - n_cf
log.info('  CF-causing: %d   Non-CF-causing: %d', n_cf, n_nc)

labels = np.array([1 if r['determination_2026'] == 'CF-causing' else 0 for r in binary])
scores = np.array([float(r['am_pathogenicity']) for r in binary])

from sklearn.metrics import (roc_auc_score, average_precision_score,
                              classification_report, matthews_corrcoef,
                              accuracy_score)

auc = roc_auc_score(labels, scores)
ap  = average_precision_score(labels, scores)

AM_THRESHOLD = 0.564
preds = (scores >= AM_THRESHOLD).astype(int)
acc   = accuracy_score(labels, preds)
mcc   = matthews_corrcoef(labels, preds)

report = classification_report(labels, preds, target_names=['Non CF-causing', 'CF-causing'],
                                output_dict=True)
cf_f1 = report['CF-causing']['f1-score']
nc_f1 = report['Non CF-causing']['f1-score']

log.info('AUC=%.4f  AP=%.4f  ACC=%.4f  MCC=%.4f  CF-F1=%.4f  NC-F1=%.4f',
         auc, ap, acc, mcc, cf_f1, nc_f1)

with open(METRICS_OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['metric', 'value', 'n', 'threshold'])
    w.writeheader()
    for metric, val in [('AUC', auc), ('AP', ap), ('Accuracy', acc), ('MCC', mcc),
                        ('CF_causing_F1', cf_f1), ('Non_CF_F1', nc_f1)]:
        w.writerow({'metric': metric, 'value': round(val, 6), 'n': len(binary),
                    'threshold': AM_THRESHOLD if metric not in ('AUC', 'AP') else 'n/a'})
log.info('Saved %s', METRICS_OUT)

# ── VCC analysis — from varying_consequence_am.csv (72-variant snapshot) ─────
with open(VCC_CSV) as f:
    vcc_rows = list(csv.DictReader(f))
log.info('VCC from varying_consequence_am.csv: %d rows', len(vcc_rows))

# Also count VCC in annotated file (82-variant snapshot) for comparison
vcc_annotated = [r for r in annotated if r['determination_2026'] == 'Varying clinical consequence']
log.info('VCC in cftr2_results_annotated.csv: %d  (NOTE: different CFTR2 snapshot)', len(vcc_annotated))

from collections import Counter
vcc_classes = Counter(r['am_class'] for r in vcc_rows)
log.info('VCC AM class distribution (72-row file): %s', dict(vcc_classes))

with open(VCC_OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['source', 'total_vcc', 'likely_pathogenic',
                                      'ambiguous', 'likely_benign', 'note'])
    w.writeheader()
    w.writerow({
        'source': 'data/varying_consequence_am.csv',
        'total_vcc': len(vcc_rows),
        'likely_pathogenic': vcc_classes.get('likely_pathogenic', 0),
        'ambiguous': vcc_classes.get('ambiguous', 0),
        'likely_benign': vcc_classes.get('likely_benign', 0),
        'note': 'derived_from_cftr2_results_csv_snapshot_72_variants'
    })
    vcc_ann_classes = Counter(r['am_class'] for r in vcc_annotated if r.get('am_class'))
    w.writerow({
        'source': 'data/cftr2_results_annotated.csv',
        'total_vcc': len(vcc_annotated),
        'likely_pathogenic': vcc_ann_classes.get('likely_pathogenic', 0),
        'ambiguous': vcc_ann_classes.get('ambiguous', 0),
        'likely_benign': vcc_ann_classes.get('likely_benign', 0),
        'note': 'derived_from_cftr2_results_annotated_csv_snapshot_82_variants'
    })
log.info('Saved %s', VCC_OUT)

# ── Domain analysis — from varying_consequence_am.csv (72 variants) ───────────
DOMAINS = [('MSD1', 1, 394), ('NBD1', 395, 646), ('R-domain', 647, 835),
           ('MSD2', 836, 1172), ('NBD2', 1173, 1480)]

pos_re = re.compile(r'[A-Z][a-z]{2}(\d+)')

def get_domain(variant_name):
    m = pos_re.search(variant_name)
    if not m:
        return 'unknown'
    pos = int(m.group(1))
    for name, lo, hi in DOMAINS:
        if lo <= pos <= hi:
            return name
    return 'unknown'

lp_vcc = [r for r in vcc_rows if r['am_class'] == 'likely_pathogenic']
domain_counts = Counter(get_domain(r['variant']) for r in lp_vcc)
msd_total = domain_counts.get('MSD1', 0) + domain_counts.get('MSD2', 0)
msd_pct = msd_total / len(lp_vcc) * 100 if lp_vcc else 0.0

log.info('Domain distribution (n=%d LP): %s', len(lp_vcc), dict(domain_counts))
log.info('MSD1+MSD2: %d / %d = %.1f%%  R-domain: %d',
         msd_total, len(lp_vcc), msd_pct, domain_counts.get('R-domain', 0))

with open(DOMAIN_OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['domain', 'count', 'pct_of_lp', 'source_n_lp'])
    w.writeheader()
    for dname, _, _ in DOMAINS:
        cnt = domain_counts.get(dname, 0)
        pct = cnt / len(lp_vcc) * 100 if lp_vcc else 0.0
        w.writerow({'domain': dname, 'count': cnt,
                    'pct_of_lp': round(pct, 2), 'source_n_lp': len(lp_vcc)})
log.info('Saved %s', DOMAIN_OUT)

# ── Unclassified variant AM class counts ─────────────────────────────────────
unclassified = [r for r in annotated if not r['determination_2026'] and r['am_pathogenicity']]
unclass_classes = Counter(r['am_class'] for r in unclassified)
log.info('Unclassified with AM: %d  classes: %s', len(unclassified), dict(unclass_classes))

# Pre-dedup: raw counts per am_class
# Post-dedup: unique by am_variant (single-letter)
seen_am = set()
dedup_lp = []
for r in unclassified:
    if r['am_class'] == 'likely_pathogenic' and r.get('am_variant'):
        if r['am_variant'] not in seen_am:
            seen_am.add(r['am_variant'])
            dedup_lp.append(r)

log.info('LP unclassified: raw=%d  dedup by am_variant=%d',
         unclass_classes.get('likely_pathogenic', 0), len(dedup_lp))

with open(UNCLASS_OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['am_class', 'count_raw', 'count_dedup_lp_only', 'note'])
    w.writeheader()
    for am_class in ['likely_pathogenic', 'ambiguous', 'likely_benign']:
        cnt = unclass_classes.get(am_class, 0)
        dedup = len(dedup_lp) if am_class == 'likely_pathogenic' else ''
        w.writerow({'am_class': am_class, 'count_raw': cnt,
                    'count_dedup_lp_only': dedup,
                    'note': 'from_cftr2_results_annotated_csv_unclassified'})
log.info('Saved %s', UNCLASS_OUT)

print('\n=== AlphaMissense validation summary ===')
print(f'n (binary): {len(binary)}  CF-causing: {n_cf}  Non-CF-causing: {n_nc}')
print(f'AUC: {auc:.4f}  AP: {ap:.4f}  MCC: {mcc:.4f}')
print(f'Accuracy: {acc:.4f}  CF-F1: {cf_f1:.4f}  NC-F1: {nc_f1:.4f}')
print(f'\nVCC (72-row file): {len(vcc_rows)}  LP: {vcc_classes.get("likely_pathogenic",0)}')
print(f'VCC (annotated file): {len(vcc_annotated)}  LP: {vcc_ann_classes.get("likely_pathogenic",0)}')
print(f'Domain: MSD1+MSD2 = {msd_total}/{len(lp_vcc)} = {msd_pct:.1f}%  R-domain = {domain_counts.get("R-domain",0)}')
print(f'\nUnclassified LP: raw={unclass_classes.get("likely_pathogenic",0)}  dedup={len(dedup_lp)}')
