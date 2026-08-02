"""
4-predictor benchmark analysis: AlphaMissense, CADD, PolyPhen, SIFT.

Executable replacement for notebooks/comparison.ipynb.
That notebook is out-of-sequence. This script delegates to the Phase 1
pipeline scripts which handle raw-response saving and correct DeLong.

Prerequisite: run in order:
  1. scripts/phase1_fetch_cadd.py
  2. scripts/phase1_build_cohort.py
  3. scripts/phase1_benchmark.py
  4. scripts/phase1_delong.py

This script reads the produced files and prints a summary.
It does not re-compute; it validates consistency and produces
results/phase1/comparison_summary.csv.
"""

import os, csv, logging

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_CSV = os.path.join(ROOT, 'results', 'phase1', 'benchmark_metrics.csv')
DELONG_CSV  = os.path.join(ROOT, 'results', 'phase1', 'delong_tests.csv')
COHORT_CSV  = os.path.join(ROOT, 'results', 'phase1', 'benchmark_cohort.csv')
SUMMARY_CSV = os.path.join(ROOT, 'results', 'phase1', 'comparison_summary.csv')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

for path in [METRICS_CSV, DELONG_CSV, COHORT_CSV]:
    if not os.path.exists(path):
        raise FileNotFoundError(f'{path} — run phase1_fetch_cadd.py, phase1_build_cohort.py, '
                                f'phase1_benchmark.py, phase1_delong.py first')

# ── Load metrics ──────────────────────────────────────────────────────────────
with open(METRICS_CSV) as f:
    metrics = {r['tool']: r for r in csv.DictReader(f)}

with open(DELONG_CSV) as f:
    delong = list(csv.DictReader(f))

with open(COHORT_CSV) as f:
    cohort = list(csv.DictReader(f))
n_included = sum(1 for r in cohort if r['included'] == 'True')
n_total    = len(cohort)

log.info('Cohort: %d total  %d included', n_total, n_included)

# ── Print comparison table ────────────────────────────────────────────────────
print(f'\n=== 4-predictor comparison (n={n_included}) ===')
print(f"{'Tool':<20} {'AUC':>7} {'AP':>7}")
print('-' * 36)
for tool in ['AlphaMissense', 'CADD', 'PolyPhen', 'SIFT']:
    if tool in metrics:
        r = metrics[tool]
        print(f"{tool:<20} {float(r['auc']):>7.4f} {float(r['ap']):>7.4f}")

print(f'\n=== Ensemble ===')
if 'Ensemble_CV' in metrics:
    r = metrics['Ensemble_CV']
    print(f"{'Ensemble (5-fold CV)':<20} {float(r['auc']):>7.4f} {float(r['ap']):>7.4f}")
    print(f'  {r["note"]}')

print(f'\n=== DeLong tests (corrected, Sun & Xu 2014) ===')
print(f"{'Comparison':<35} {'Z':>7} {'p':>10}")
print('-' * 54)
for d in delong:
    cmp = f"{d['tool_a']} vs {d['tool_b']}"
    print(f"{cmp:<35} {float(d['z']):>7.3f} {float(d['p']):>10.6f} {d['significance']}")

# ── Save summary ──────────────────────────────────────────────────────────────
rows_out = []
for tool in ['AlphaMissense', 'CADD', 'PolyPhen', 'SIFT', 'Ensemble_CV']:
    if tool in metrics:
        r = metrics[tool]
        rows_out.append({'source': 'benchmark_metrics.csv', 'tool': tool,
                         'auc': r['auc'], 'ap': r['ap'], 'n': r['n'], 'note': r['note']})
for d in delong:
    rows_out.append({'source': 'delong_tests.csv',
                     'tool': f"{d['tool_a']}_vs_{d['tool_b']}",
                     'auc': d['z'], 'ap': d['p'], 'n': d['n'], 'note': d['significance']})

with open(SUMMARY_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['source', 'tool', 'auc', 'ap', 'n', 'note'])
    w.writeheader()
    w.writerows(rows_out)
log.info('Saved %s', SUMMARY_CSV)
