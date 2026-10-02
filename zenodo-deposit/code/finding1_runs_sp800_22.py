"""Independent reference implementation of NIST SP 800-22 Rev. 1a section 2.3 (Runs).

Written directly from the published procedure, not imported from the shared
laboratory battery, so that the two can be compared as independent
implementations of the same specification.

The standard's steps:

1. Compute the proportion of ones ``pi``.  The test is **applicable only if**
   ``|pi - 1/2| >= 2/sqrt(n - 1)``.  Otherwise the test must not be run.
2. ``V_obs = 1 + sum_k r(k)``, where ``r(k) = 1`` when ``eps_k != eps_{k+1}``.
3. ``P-value = erfc( |V_obs - 2 n pi (1 - pi)| / (2 sqrt(2 n) pi (1 - pi)) )``.

Note the deliberate absence of a further ``sqrt(2)`` in the denominator: the
argument of ``erfc`` here is already in ``erfc`` units, not a z-score.  The
normal-tail identity ``2 (1 - Phi(|z|)) == erfc(|z| / sqrt(2))`` applies only when
the argument is a standardised z-score, as it is in the monobit and DFT tests.

Only a bounded, deterministic-in-structure calibration is supported here; this
module generates no random numbers itself.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy import special

__all__ = [
    "RUNS_APPLICABILITY",
    "runs_count",
    "runs_pi",
    "runs_standardized_deviation",
    "runs_test_sp800_22",
    "runs_test_sp800_22_with_applicability",
]

RUNS_APPLICABILITY = "abs(pi - 0.5) >= 2 / sqrt(n - 1)"


def runs_count(bits: np.ndarray) -> int:
    """``V_obs``: one plus the number of adjacent bit transitions."""
    bits = np.asarray(bits)
    if bits.ndim != 1 or bits.size < 2:
        raise ValueError("bits must be a one-dimensional array of length >= 2")
    return int(np.count_nonzero(bits[1:] != bits[:-1])) + 1


def runs_pi(bits: np.ndarray) -> float:
    bits = np.asarray(bits)
    if bits.size == 0:
        raise ValueError("bits must be nonempty")
    return float(bits.mean())


def runs_standardized_deviation(bits: np.ndarray) -> float:
    """``|V_obs - 2 n pi (1 - pi)| / sqrt(2 n pi (1 - pi))``, the erfc argument."""
    n = int(bits.size)
    pi = runs_pi(bits)
    variance_term = 2.0 * n * pi * (1.0 - pi)
    if variance_term <= 0.0:
        return math.inf
    return abs(runs_count(bits) - variance_term) / math.sqrt(variance_term)


def runs_test_sp800_22(bits: np.ndarray) -> float:
    """Section 2.3 step 3, returned as a p-value.  No applicability gate here."""
    n = int(bits.size)
    pi = runs_pi(bits)
    if pi in (0.0, 1.0):
        return float("nan")
    numerator = abs(runs_count(bits) - 2.0 * n * pi * (1.0 - pi))
    denominator = 2.0 * math.sqrt(2.0 * n) * pi * (1.0 - pi)
    return float(special.erfc(numerator / denominator))


def runs_test_sp800_22_with_applicability(bits: np.ndarray) -> dict[str, Any]:
    """Section 2.3 with step 1 enforced, as the standard requires.

    ``applicable`` is ``False`` for almost every fair stream at laboratory
    lengths: the condition needs a ~4-sigma deviation in the bit balance, so a
    p-value computed for such a stream is not a valid uniform p-value.
    """
    n = int(bits.size)
    pi = runs_pi(bits)
    tau = 2.0 / math.sqrt(n - 1.0) if n > 1 else math.inf
    applicable = bool(abs(pi - 0.5) >= tau)
    record: dict[str, Any] = {
        "n": n,
        "pi": pi,
        "abs_pi_minus_half": abs(pi - 0.5),
        "tau": tau,
        "applicability_condition": RUNS_APPLICABILITY,
        "applicable": applicable,
        "V_obs": runs_count(bits),
        "standardized_deviation": runs_standardized_deviation(bits),
    }
    if not applicable:
        record["p_value"] = None
        record["status"] = "NOT_APPLICABLE_PER_SP800_22"
    else:
        record["p_value"] = runs_test_sp800_22(bits)
        record["status"] = "APPLICABLE"
    return record
