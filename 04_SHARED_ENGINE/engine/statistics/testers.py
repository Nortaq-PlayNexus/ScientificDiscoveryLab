"""statistics.testers — BH-FDR, Welch t, Cohen's d, bootstrap CIs, binomial bands.

Conventions (RESEARCH_RULES.md): alpha = 0.01 preregistered by default;
Benjamini-Hochberg FDR whenever many comparisons are made.
"""

from __future__ import annotations

import numpy as np

from ..utilities.core import rng


def bh_fdr(pvals, alpha=0.01):
    """Benjamini-Hochberg (step-up).

    Returns (significant_mask, context). significant_mask is in INPUT order.
    context = (ranked_p, thresholds, order_indices_of_ranked) for inspection.

    Reference step-up: sort p ascending; find largest rank k with
    p_(k) <= k/n * alpha (k 1-indexed); reject all ranks <= k.
    """
    p = np.asarray(pvals, dtype=float).ravel()
    n = p.size
    if n == 0:
        return np.zeros(0, dtype=bool), (np.array([]), np.array([]), np.array([]))
    order = np.argsort(p)
    ranked = p[order]
    thresholds = np.arange(1, n + 1) / n * alpha
    below = ranked <= thresholds
    if not below.any():
        k = -1
    else:
        first_in_flipped = int(np.flatnonzero(np.flip(below))[0])
        k = (n - 1) - first_in_flipped  # largest 0-based rank with p_(k) <= thr
    significant = np.zeros(n, dtype=bool)
    if k >= 0:
        significant[order[: k + 1]] = True
    return significant, (ranked, thresholds, order)


def cohens_d(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = a.size, b.size
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    if sp == 0:
        return float("inf") if (a.mean() - b.mean()) == 0 else 0.0
    return float((a.mean() - b.mean()) / sp)


def welch_t(a, b):
    """Two-sample Welch t-test -> (t, df, p)."""
    from scipy import stats

    res = stats.ttest_ind(a, b, equal_var=False)
    df = getattr(res, "df", float("nan"))
    return float(res.statistic), df, float(res.pvalue)


def effect_size_and_ci(a, b, n_boot=2000, seed=0, alpha=0.05):
    """Bootstrap percentile CI on the mean difference (a - b)."""
    gen = rng("bootstrap-diff", seed)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        diffs[i] = a[gen.integers(0, a.size, a.size)].mean() - b[
            gen.integers(0, b.size, b.size)
        ].mean()
    lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {
        "mean_diff": float(a.mean() - b.mean()),
        "ci_low": float(lo),
        "ci_high": float(hi),
        "mean_a": float(a.mean()),
        "mean_b": float(b.mean()),
    }


def summarize(metric_a, metric_b, label="effect", alpha=0.01):
    """t-test + Cohen's d + bootstrap CI in one report dict (default alpha 0.01)."""
    t, df, p = welch_t(metric_a, metric_b)
    ci = effect_size_and_ci(metric_a, metric_b)
    return {
        "label": label,
        "t": float(t),
        "df": float(df),
        "p": float(p),
        "significant_alpha": bool(p < alpha),
        "cohens_d": cohens_d(metric_a, metric_b),
        **ci,
    }


def binomial_band(n_trials, p=0.5, alpha=0.05):
    """Exact central binomial quantiles (digit-count style checks)."""
    from scipy import stats

    return {
        "lo": int(stats.binom.ppf(alpha / 2, n_trials, p)),
        "hi": int(stats.binom.ppf(1 - alpha / 2, n_trials, p)),
    }