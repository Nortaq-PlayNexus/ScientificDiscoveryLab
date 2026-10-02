# LITERATURE — Q-P004 anchors and methods (EXP-0005)

## Thresholds (anchors)

- **Bond percolation, square lattice: p_c = 1/2 EXACT.** Proof via planar duality
  and self-duality of the square lattice (Kesten 1982 "Percolation Theory for
  Mathematicians"; earlier suggestions by Sykes-Essam; Wierman for some classes).
  This is a theorem, not a measurement.
- **Site percolation, square lattice: p_c = 0.59274605079210(2)** (high precision).
  Newman & Ziff efficient Monte Carlo (PRL 85, 4104 2000; joint with Ziff's
  boundary-crossing methodology). Common citable precision: ~0.59274605. We use
  0.5927460508 as the anchor; the decision tolerance (0.01) dwarfs the ~2e-4
  literature uncertainty, so the precise digit string is not decision-sensitive.

## Exponents (universality class)

- The 2D percolation universality class: beta = 5/36, nu = 4/3, beta/nu = 5/48
  ~= 0.10417 (Nienhuis exact via Coulomb-gas; CFT/Conformal invariance). Numerically
  confirmed to ~1e-4 with transfer-matrix / MC (see e.g. Jensen; Ziff).
- These are used (a) as the fixed exponent 1/nu = 3/4 in the primary FSS
  extrapolation model, and (b) as the comparison target for the free-exponent
  diagnostic (C8).

## Methods

- **Efficient Monte Carlo**: Newman & Ziff (2000) incremental algorithm. We use a
  simpler version: independent realizations per p (required because we also fix the
  seeds and reuse the certified RNG streams).
- **Wrapping clusters** on the torus (Ziff & Newman; Ziff 2016) have the cleanest
  crossing: define W(p) = P(cluster wraps horizontally). p50(L) = root of W(p)=1/2.
  Known FSS: p50(L) - p_c ~ a L^(-1/nu) + subleading (b L^(-1/nu - delta), log
  terms). We fit only the leading term and use C4/C8 to detect contamination.
- **Spanning on open square** (top-bottom) is the classic alternative. We use it as
  an independent-estimator AND independent-boundary-condition control (C2).

## Subleading / correction subtleties (why C4/C8 exist)

- For periodic wrapping estimators, corrections include the dangerous-irrelevant
  exponent omega = 2 (Weygand & Ziff; see also Grygiel & Prellberg). Dropping the
  smallest L (C4) checks that our single-term fit is stable.
- Crossing-probability arguments (Langlands-Pichet-Sainte-Marie-yock; Cardy 1992;
  Smirnov 2001 proof of Cardy) justify universality of crossing functions.

## Known pitfalls from the informal literature

- Naive "cluster touches both boundary columns" on the torus overcounts wraps.
- Fitting p50(L) with the wrong correction term shifts extrapolated p_c by ~1e-3.
- Seed/stream quality: adjacent seeds can look correlated. This lab's RNG was
  certified in EXP-0004 (G_LAB, CONTROLLED).
- Windows numpy uint8 sum overflow (EXP-0004) — count everything in int.