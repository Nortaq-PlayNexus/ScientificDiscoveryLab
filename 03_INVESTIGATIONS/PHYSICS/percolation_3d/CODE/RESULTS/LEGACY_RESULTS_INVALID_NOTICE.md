# Historical 3D result invalidity notice

`EXP-0011_results.json` is a historical pilot artifact, not a production main
result. The 2026-09-24 audit found that its width/p-c calculation used 2D slice
boundaries for cubic labels, its configured sample counts were silently reduced,
all exponent arrays were truncated to the smallest size, and the stored tau tail
was structurally empty because of nested cluster arrays.

Do not use this file for a current p-c, exponent, or C7 claim. The old runner
path now refuses execution. Corrected smoke artifacts are under
`../RESULTS_AUDIT_REPAIR/QP008_AUDIT_R1_SMOKE_V4/` and remain INCONCLUSIVE.
No corrected production 3D result exists.
