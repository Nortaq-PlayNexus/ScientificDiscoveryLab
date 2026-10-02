# QUESTION — Q-M005: Feigenbaum universality in higher-order 1D maps

**Field:** mathematics / physics
**Question ID:** Q-M005
**Feasibility:** HIGH

## Question

Do higher-derivative 1D maps (z = f(z) with local extrema of order
z = 2, 3, 4) show Feigenbaum-like universal constants with clean
convergence of delta/alpha estimates?

## What scientists already know

For order-2 extrema (logistic map): delta ~ 4.669, alpha ~ -2.5029.
Universality extends to maps within the same extremum class.
Feigenbaum (1978) computed delta_n -> delta_infty; Hu & Mao (1982)
extended to higher orders — delta depends on z but convergence
is universal within a class.

## What remains unknown

Precise delta for each local extremum order with tight numerics;
convergence-rate subtleties at higher order. Specifically:
- Does delta_n converge monotonically for z = 3, 4?
- How many n are needed for |delta_n - delta_infty| < 1e-4?
- Is alpha_n convergence similarly well-behaved?

## Current theories

Renormalization-group explanation (Feigenbaum 1978, Hu & Mao 1982).
The RG fixed point depends on z; delta(z) and alpha(z) are
universal functions of z alone.

## Known methods

Superstable-cycle search: find parameter a_n where the critical
point is periodic with period 2^n; compute delta_n =
(a_{n-1} - a_{n-2}) / (a_n - a_{n-1}); compute alpha_n from
the spatial scaling at the period-doubling orbit.

## Computational requirements

CPU, low-to-moderate. Pure integer/real arithmetic. No external data.

## Falsification test

If delta_n fails to converge for any order z in {2, 3, 4}, or if
the limit disagrees with published values by more than the estimated
numerical error, the universality hypothesis for that order is
falsified.

## What would count as a real result

Reproduction of published Feigenbaum constants for z = 2, 3, 4
with quantified error bars; a new reproducible deviation would
need independent numerical method verification.