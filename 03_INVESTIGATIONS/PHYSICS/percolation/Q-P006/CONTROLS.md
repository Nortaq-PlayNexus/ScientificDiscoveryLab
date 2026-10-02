# Controls — Q-P006 (from frozen prereg)

| Control | Description |
|---|---|
| C1 | full-cell rerun (L=1024, p_c) cluster census bit-identical |
| C6 | seed ladder on M_max, chi at each L (n per seed from n_real) |
| C7 | pure-Python union-find independent: L in [512, 1024, 2048], subsample n=40, per-realization M_max and chi bit-identical |
| FG | slope stability: refit D_f on inner sizes |d|<=0.02, gamma/nu |d|<=0.04 |
| PC1 | bootstrap SE + chi2_red reported for every fit |
