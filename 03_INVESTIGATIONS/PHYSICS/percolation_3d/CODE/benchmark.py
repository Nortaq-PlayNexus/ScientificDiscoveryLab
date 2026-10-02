import os, sys, time
sys.path.insert(0, 'C:/Users/natha/ScientificDiscoveryLab/03_INVESTIGATIONS/PHYSICS/percolation/ENGINE')
import perc_engine as pe
import numpy as np

for L in [8, 16, 24, 32]:
    src, dst, N = pe.cubic_lattice_3d(L)
    t0 = time.time()
    for i in range(10):
        o = pe.run_span_cell_edges(src, dst, N, L, 0.3116079, 1, i, 'bench', semantics='site', want_largest_mass=True, want_stats=True, want_cluster_sizes=True, ndim=3)
    t1 = time.time()
    per_cell = (t1 - t0) / 10
    print(f'L={L}: N={N}, 10 cells in {t1-t0:.2f}s, per cell = {per_cell:.4f}s, 500 cells = {per_cell*500:.0f}s')
