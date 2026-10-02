# HIGH FEASIBILITY candidates

Feasibility = can run a well-controlled experiment on this machine soon with
current tools/data. NOT a statement of scientific importance.

| ID | Field | Question | Cost |
|---|---|---|---|
| Q-M001 | mathematics | Generalized Collatz stopping-time statistics | CPU-min..hrs |
| Q-M002 | mathematics | Prime gap distribution vs Poisson model | CPU-min |
| Q-M003 | mathematics | Constant digit normalcy scan (with FDR) | CPU-hrs |
| Q-M005 | mathematics | Feigenbaum constants order-2/3/4 maps | CPU-min |
| Q-M006 | mathematics | First-passage universality in correlated walks | CPU-hrs |
| Q-O001 | optics | Speckle contrast vs 1/sqrt(M) law | CPU-min |
| Q-O002 | optics | Vortex density in random fields (Nye-Berry/Freund) | CPU-min |
| Q-O003 | optics | Propagation-invariance audit vs surrogate nulls | GPU-hrs |
| Q-P003 | physics/optics | "Quantum-looking" classical correlations (falsification) | CPU-min |
| Q-P004 | physics | Percolation thresholds reproduction | CPU-min |
| Q-C002 | climate | ENSO simple-model baseline skill | CPU-min |
| Q-I001 | infotheory | Compression pattern tests calibration | CPU-hrs |
| Q-I002 | compsci | Summation-order effect on pipeline metrics | CPU-hrs |
| Q-I004 | compsci | PRNG statistical battery (lab RNG cert) | CPU-min |

Recommended first wave (bundled infrastructure + highest reuse):
Q-O001, Q-O002 (both reuse the optics sandbox), Q-I004 (certifies the lab RNG),
Q-M001 (complete with-core math run).

Next wave: Q-M002, Q-M005, Q-M006, Q-P004, Q-I001, Q-P003, Q-C002.