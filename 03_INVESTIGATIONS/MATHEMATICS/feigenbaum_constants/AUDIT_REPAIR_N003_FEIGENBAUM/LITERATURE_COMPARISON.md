# N-003 literature comparison note

## Feigenbaum (z=2)

The reference used by this repair is the published Feigenbaum delta limit
`4.669201609102990671853203820466201617258185577475768632745651343054...`
from M. Feigenbaum, *Quantitative universality for a class of nonlinear
transformations*, J. Stat. Phys. **19**, 25--52 (1978), DOI
`10.1007/BF01020332`. The z=2 finite-n computation is a reproduction check.

## Hu & Mao: corrected record and convention

The relevant actual record is:

> B. Hu and J. M. Mao, “Period doubling: Universality and critical-point
> order,” *Physical Review A* **25**, 3259--3261 (1982), DOI
> `10.1103/PhysRevA.25.3259`.

The paper studies `f(x)=1-a*x**z` for **even** orders `z=2,4,6,8`. Its Table I
 displays exact/bifurcation-ratio values `4.669`, `7.284`, `9.296`, and
`10.948` for those four orders. For even z, `x**z == abs(x)**z` on the real
attracting interval, so the repair's z=4 result is directly comparable at the
paper's displayed precision.

The paper does **not** report z=3. The historical project values `4.894` and
`5.168` for z=3/z=4 are not treated as Hu & Mao comparisons: the former has no
matching table entry and the latter conflicts with the actual z=4 table value.
For z=3, the repair reports only the internally period-verified numerical
sequence and an explicit “not directly reported” literature status.

This note is separate from the historical `03_INVESTIGATIONS/MATHEMATICS/
feigenbaum_constants/LITERATURE.md`; the historical file was not edited.
