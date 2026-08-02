"""
Compute Phase 1 benchmark metrics from the cohort built by phase1_build_cohort.py.

Input:  results/phase1/benchmark_cohort.csv
Output: results/phase1/benchmark_metrics.csv

All four tools (AlphaMissense, CADD, PolyPhen, SIFT) are evaluated on
exactly the same n (included==True variants only).

Ensemble: logistic regression on [AlphaMissense, CADD, PolyPhen] with
stratified 5-fold CV to obtain out-of-fold probability estimates, then
AUC and AP on those estimates. Coefficients are from a model fitted on
the full included set for comparison to the documented values, but the
ensemble AUC and AP are CV-based (held-out), not in-sample.
"""

import os, csv, logging
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COHORT_CSV = os.path.join(ROOT, 'results', 'phase1', 'benchmark_cohort.csv')
METRICS_CSV = os.path.join(ROOT, 'results', 'phase1', 'benchmark_metrics.csv')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# ── Load cohort ───────────────────────────────────────────────────────────────
with open(COHORT_CSV) as f:
    all_rows = list(csv.DictReader(f))

included = [r for r in all_rows if r['included'] == 'True']
log.info('Included variants: %d', len(included))

labels = np.array([int(r['label'])  for r in included])
am     = np.array([float(r['am_pathogenicity']) for r in included])
cadd   = np.array([float(r['cadd_phred'])      for r in included])
pp     = np.array([float(r['polyphen_score'])   for r in included])
sift   = np.array([float(r['sift_score_inv'])   for r in included])

n      = len(labels)
n_pos  = int(labels.sum())
n_neg  = n - n_pos
log.info('n=%d  n_pos=%d  n_neg=%d', n, n_pos, n_neg)

# ── Individual tool metrics ───────────────────────────────────────────────────
rows_out = []

for name, scores in [('AlphaMissense', am), ('CADD', cadd),
                     ('PolyPhen', pp), ('SIFT', sift)]:
    auc = roc_auc_score(labels, scores)
    ap  = average_precision_score(labels, scores)
    log.info('%s: AUC=%.4f  AP=%.4f  n=%d', name, auc, ap, n)
    rows_out.append({'tool': name, 'auc': round(auc, 6), 'ap': round(ap, 6),
                     'n': n, 'n_pos': n_pos, 'n_neg': n_neg,
                     'note': 'individual_tool'})

# ── MCC at threshold 0.564 for AlphaMissense (used in REPORT.md) ─────────────
from sklearn.metrics import matthews_corrcoef
AM_THRESHOLD = 0.564
am_pred = (am >= AM_THRESHOLD).astype(int)
mcc = matthews_corrcoef(labels, am_pred)
log.info('AlphaMissense MCC at threshold %.3f: %.4f', AM_THRESHOLD, mcc)
rows_out.append({'tool': 'AlphaMissense_MCC', 'auc': round(mcc, 6), 'ap': '',
                 'n': n, 'n_pos': n_pos, 'n_neg': n_neg,
                 'note': f'MCC_at_threshold_{AM_THRESHOLD}'})

# ── Ensemble: logistic regression with CV ─────────────────────────────────────
X = np.column_stack([am, cadd, pp])
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
lr = LogisticRegression(max_iter=1000)

# Out-of-fold (held-out) probability estimates
oof_probs = cross_val_predict(lr, X_scaled, labels, cv=cv, method='predict_proba')[:, 1]

ens_auc = roc_auc_score(labels, oof_probs)
ens_ap  = average_precision_score(labels, oof_probs)
log.info('Ensemble CV: AUC=%.4f  AP=%.4f', ens_auc, ens_ap)

# Full-data coefficients (for comparison with documented +1.907/+0.279/-0.117)
lr_full = LogisticRegression(max_iter=1000)
lr_full.fit(X_scaled, labels)
coef_am, coef_cadd, coef_pp = lr_full.coef_[0]
log.info('Ensemble coefficients (full fit): AM=%.4f  CADD=%.4f  PP=%.4f',
         coef_am, coef_cadd, coef_pp)

rows_out.append({'tool': 'Ensemble_CV', 'auc': round(ens_auc, 6), 'ap': round(ens_ap, 6),
                 'n': n, 'n_pos': n_pos, 'n_neg': n_neg,
                 'note': f'5fold_stratified_CV_seed42_coef_am={coef_am:.4f}_cadd={coef_cadd:.4f}_pp={coef_pp:.4f}'})

# ── Save ──────────────────────────────────────────────────────────────────────
with open(METRICS_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['tool', 'auc', 'ap', 'n', 'n_pos', 'n_neg', 'note'])
    w.writeheader()
    w.writerows(rows_out)
log.info('Saved %s', METRICS_CSV)

print('\n=== Benchmark metrics summary ===')
for r in rows_out:
    print(f"  {r['tool']:<25} AUC={r['auc']}  AP={r['ap']}  n={r['n']}")
