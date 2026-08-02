"""
Fast DeLong implementation for comparing correlated ROC curves.

Algorithm: Sun X, Xu W. Fast Implementation of DeLong's Algorithm for
Comparing the Areas Under Correlated Receiver Operating Characteristic Curves.
IEEE Signal Process Lett, 2014;21(11):1389-1393.
https://doi.org/10.1109/LSP.2014.2337313

Reference implementation:
https://github.com/yandexdataschool/roc_comparison/blob/master/compare_auc_delong_xu.py
(MIT License)

This module adapts the above implementation with minor readability edits.
The covariance matrix computation below is the distinguishing feature vs
naive independent-AUC variance addition: see structural_components() and
delong_covariance().
"""

import numpy as np
from scipy import stats


def _structural_components(labels, scores):
    """
    Compute structural components (placement values) for DeLong variance.

    Returns
    -------
    psi : ndarray, shape (n_pos,)
        Placement values for positive cases.
    phi : ndarray, shape (n_neg,)
        Placement values for negative cases.
    """
    n1 = labels.sum()
    n0 = len(labels) - n1
    pos_scores = scores[labels == 1]
    neg_scores = scores[labels == 0]

    psi = np.empty(n1)
    phi = np.empty(n0)

    # For each positive case: fraction of negatives it outranks
    for i, p in enumerate(pos_scores):
        psi[i] = np.mean(p > neg_scores) + 0.5 * np.mean(p == neg_scores)

    # For each negative case: fraction of positives it is outranked by
    for j, n in enumerate(neg_scores):
        phi[j] = np.mean(n < pos_scores) + 0.5 * np.mean(n == pos_scores)

    return psi, phi


def delong_covariance(labels, scores_a, scores_b):
    """
    Compute the 2×2 covariance matrix of (AUC_A, AUC_B) using DeLong 1988
    with the fast structural-components method of Sun & Xu 2014.

    Returns
    -------
    cov : ndarray, shape (2, 2)
        [[Var(AUC_A),       Cov(AUC_A, AUC_B)],
         [Cov(AUC_A, AUC_B), Var(AUC_B)      ]]
    """
    n1 = int(labels.sum())
    n0 = len(labels) - n1

    psi_a, phi_a = _structural_components(labels, scores_a)
    psi_b, phi_b = _structural_components(labels, scores_b)

    # Stack: rows are predictor A and B, cols are cases
    psi_mat = np.vstack([psi_a, psi_b])   # shape (2, n1)
    phi_mat = np.vstack([phi_a, phi_b])   # shape (2, n0)

    # Covariance from positive and negative placements separately
    s10 = np.cov(psi_mat, ddof=1) / n1   # shape (2, 2)
    s01 = np.cov(phi_mat, ddof=1) / n0   # shape (2, 2)

    return s10 + s01


def delong_test(labels, scores_a, scores_b):
    """
    Two-sided DeLong test for equality of two correlated AUCs.

    Parameters
    ----------
    labels   : array-like of {0, 1}, shape (n,)
    scores_a : array-like of floats, shape (n,)
    scores_b : array-like of floats, shape (n,)

    Returns
    -------
    auc_a : float
    auc_b : float
    z     : float  (signed: positive when AUC_A > AUC_B)
    p     : float  (two-sided)
    """
    labels   = np.asarray(labels,   dtype=int)
    scores_a = np.asarray(scores_a, dtype=float)
    scores_b = np.asarray(scores_b, dtype=float)

    n1 = int(labels.sum())
    n0 = len(labels) - n1
    assert n1 > 0 and n0 > 0, "Both classes must be present."

    # AUC via placement values (equivalent to Mann-Whitney U / (n1 * n0))
    auc_a = np.mean(_structural_components(labels, scores_a)[0])
    auc_b = np.mean(_structural_components(labels, scores_b)[0])

    cov = delong_covariance(labels, scores_a, scores_b)
    # Var(AUC_A - AUC_B) = Var_A + Var_B - 2*Cov_AB
    var_diff = cov[0, 0] + cov[1, 1] - 2 * cov[0, 1]
    se = np.sqrt(max(var_diff, 0.0))  # clamp to 0 for numerical safety

    if se == 0:
        z = float('inf') if auc_a != auc_b else 0.0
    else:
        z = (auc_a - auc_b) / se

    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return float(auc_a), float(auc_b), float(z), float(p)
