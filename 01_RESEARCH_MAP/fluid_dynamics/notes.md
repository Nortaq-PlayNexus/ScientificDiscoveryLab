# FLUID DYNAMICS — research map

## Known
- Kraichnan-Batchelor dual cascade: k^-5/3 enstrophy/energy inverse, k^-3 forward
  (with log corrections). Von Kármán shedding: St-Re empirics. Burgers shocks:
  analytic scary-Frisch results.

## Computable on this machine
- 1D Burgers: yes, cheap, well controlled. 2D turbulence: yes but CPU-bound with
  torch CPU build; 512^2 manageable, 1024^2 slow. Cylinder wake: solver cost.

## Realistic mode
- Numerical-science benchmark projects: reproduce published spectra/scalings with
  honest error bars + scheme-dependence tables. No fluid "discovery" is plausible or
  claimed.