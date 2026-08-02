"""
Correct pairwise DeLong tests for Phase 1 comparisons.

Uses the full covariance-accounting implementation in phase1_utils_delong.py
(Sun & Xu 2014 algorithm, citing https://github.com/yandexdataschool/roc_comparison).

Input:  results/phase1/benchmark_cohort.csv
Output: results/phase1/delong_tests.csv

Sanity check: the corrected Z values must be LARGER (more extreme) than the
previously reported values (2.88 / 3.28 / 5.87), because the original code
omitted the covariance term, over-estimating SE. If any corrected Z is smaller
in magnitude, this script raises an error rather than producing wrong results.
"""

import os, sys, csv, logging
import numpy as np

ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from phase1_utils_delong import delong_test

COHORT_CSV  = os.path.join(ROOT, 'results', 'phase1', 'benchmark_cohort.csv')
DELONG_CSV  = os.path.join(ROOT, 'results', 'phase1', 'delong_tests.csv')

PREVIOUS_Z = {
    ('AlphaMissense', 'PolyPhen'): 2.88,
    ('AlphaMissense', 'CADD'):     3.28,
    ('AlphaMissense', 'SIFT'):     5.87,
}

IMPLEMENTATION = (
    'Sun X, Xu W. Fast Implementation of DeLong\'s Algorithm. '
    'IEEE Signal Process Lett 2014;21(11):1389-1393. '
    'Reference code: https://github.com/yandexdataschool/roc_comparison '
    '(scripts/phase1_utils_delong.py)'
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# ── Load cohort ───────────────────────────────────────────────────────────────
with open(COHORT_CSV) as f:
    all_rows = list(csv.DictReader(f))

included = [r for r in all_rows if r['included'] == 'True']
n = len(included)
log.info('Included variants for DeLong: %d', n)

labels = np.array([int(r['label'])                for r in included])
am     = np.array([float(r['am_pathogenicity'])   for r in included])
cadd   = np.array([float(r['cadd_phred'])         for r in included])
pp     = np.array([float(r['polyphen_score'])     for r in included])
sift   = np.array([float(r['sift_score_inv'])     for r in included])

# ── Run DeLong tests ──────────────────────────────────────────────────────────
comparisons = [
    ('AlphaMissense', 'PolyPhen', am, pp),
    ('AlphaMissense', 'CADD',     am, cadd),
    ('AlphaMissense', 'SIFT',     am, sift),
]

rows_out = []
sanity_fail = False

print(f"\n{'Comparison':<35} {'AUC_A':>6} {'AUC_B':>6} {'Z':>7} {'p':>10}  prev_Z  OK?")
print('-' * 75)

for tool_a, tool_b, scores_a, scores_b in comparisons:
    auc_a, auc_b, z, p = delong_test(labels, scores_a, scores_b)

    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
    prev_z = PREVIOUS_Z.get((tool_a, tool_b), None)
    direction_ok = (abs(z) >= abs(prev_z)) if prev_z is not None else True
    ok_str = 'OK' if direction_ok else 'FAIL (unexpected direction)'
    if not direction_ok:
        sanity_fail = True

    label_str = f'{tool_a} vs {tool_b}'
    print(f'{label_str:<35} {auc_a:>6.3f} {auc_b:>6.3f} {z:>7.3f} {p:>10.6f}  '
          f'{prev_z or "n/a":>6}  {ok_str}')

    rows_out.append({
        'tool_a': tool_a, 'tool_b': tool_b,
        'auc_a': round(auc_a, 6), 'auc_b': round(auc_b, 6),
        'n': n,
        'z': round(z, 4), 'p': round(p, 6),
        'significance': sig,
        'implementation': IMPLEMENTATION,
    })

if sanity_fail:
    print('\nERROR: one or more corrected Z values are SMALLER in magnitude than '
          'the previously reported values. This contradicts the expected direction '
          '(corrected DeLong should give larger Z when covariance is positive). '
          'Check the DeLong implementation.')
    sys.exit(1)
else:
    print('\nSanity check passed: all corrected |Z| ≥ previously reported |Z|.')

with open(DELONG_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['tool_a', 'tool_b', 'auc_a', 'auc_b',
                                      'n', 'z', 'p', 'significance', 'implementation'])
    w.writeheader()
    w.writerows(rows_out)
log.info('Saved %s', DELONG_CSV)
