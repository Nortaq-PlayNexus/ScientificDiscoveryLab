# EXP-0005 — Stream layout specification (protocol clarification)

**Status:** frozen BEFORE any run output was produced (2026-09-17, pre-run).
**Reason:** the prereg (CONFIG/prereg_EXP-0005.json, frozen 2026-09-17T08:24:08+00:00)
locks labels, seeds, p-grids, n_real and the decision rule, but the *reader layout*
of each cell's random block must be pinned so that the independent implementation
(CONTROLS.md C7, REPLICATION/independent_check.py) consumes bit-identical draws.

Every cell stream uses G_LAB `rng(label, seed)`, label `perc-<system>:L<L>:p<canonical>`
with `canonical = "%.17g"`. Each cell draws EXACTLY ONE `gen.random(block)` call.

## Layout per system

### bond_span (open BC, vertical spanning, expanded-site encoding)
- `block = n_real * 2 * L * (L - 1)` floats.
- **Per-layer interleaved**: for layer `t` (`0..n_real-1`), the slice
  `u[t*2e : (t+1)*2e]` with `e = L*(L-1)`.
  - horizontal edges: first `e` floats, `open_h = (u[t*2e : t*2e+e]).reshape(L, L-1) < p`; `open_h[r][c]` opens edge `(r,c)-(r,c+1)`.
  - vertical edges: next `e` floats, `open_v = (u[t*2e+e : (t+1)*2e]).reshape(L-1, L) < p`; `open_v[r][c]` opens edge `(r,c)-(r+1,c)`.
- Replication reads the same interleaved slices and builds an equivalent config.

### bond_wrap (torus, horizontal wrap, universal-cover strip)
- `block = n_real * 2 * L * L` floats.
- **Per-layer interleaved**: for layer `t`, slice `u[t*2L2 : (t+1)*2L2]` with `L2 = L*L`.
  - horizontal states: first `L2` floats, `hb = (...)reshape(L, L) < p`; state `hb[r][c]` drives BOTH edge `(r,c)->(r,c+1)` and its wrap periodicate in the strip.
  - vertical states: next `L2` floats, `vb = (...)reshape(L, L) < p`; `vb[r][c]` drives the toroidal vertical edge `(r,c)-(r+1 mod L, c)`.
- Replication uses the same slices and the same torus break.

### site_span (open BC, vertical spanning)
- `block = n_real * L * L` floats.
- Layer `t`: `open_sites = u[t*L2 : (t+1)*L2].reshape(L, L) < p` (row-major).
- Replication uses the same slices.

## Invariants
- The block for each cell is drawn once regardless of internal batching (chunking
  affects only the numpy buffer layout, never the stream).
- C1/C6 cells (bond_span L=64 seed 42 / extra seeds) and C7 sampled cells use the
  exact layouts above.
- The bootstrap stream `rng("perc-boot", seed)` is NOT part of any cell layout; it
  is used only for SE estimation (500 draws, seed 42).