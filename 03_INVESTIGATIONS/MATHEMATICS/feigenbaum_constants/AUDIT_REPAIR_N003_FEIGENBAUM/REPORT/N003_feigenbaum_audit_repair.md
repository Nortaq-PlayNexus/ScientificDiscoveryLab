# N-003 Feigenbaum Audit-Repair Report

**Status:** COMPLETE
**Scope:** z=2 smoke/control and z=3/z=4 diagnosis only; no discovery claim.

## Frozen protocol and convention

The implementation reads only the new N-003 preregistration. The map is
`f_a(x) = 1 - a*abs(x)**z` with `x_0=0`; `z` is the extremum exponent
and `n` labels exact period `P_n=2**n`.

Arithmetic: mpmath at 100 decimal digits; primary scan and doubled-resolution scan are both required.
Environment: Python `3.14.7 (tags/v3.14.7:823f032, Aug  5 2026, 10:51:32) [MSC v.1944 64 bit (AMD64)]`; mpmath `1.3.0`; platform `Windows-10-10.0.19045-SP0`.

## Computed sequences

### z=2 — COMPLETE

| n | a_n (28 digits) | delta_n (28 digits) | P_n | period verified |
|---|---|---|---|---|
| 2 | 1.31070264133683288356357079 | — | 4 | True |
| 3 | 1.38154748443206146954069356 | 4.38567759856833908574494856 | 8 | True |
| 4 | 1.39694535970456064167247798 | 4.60094927653807535781169469 | 16 | True |
| 5 | 1.40025308121478279732501228 | 4.65513049539198013648625499 | 32 | True |
| 6 | 1.40096196294484104029611631 | 4.66611194782857138833121369 | 64 | True |
| 7 | 1.40111380493977612390087965 | 4.66854858144684094804454368 | 128 | True |
| 8 | 1.40114632582694617864728823 | 4.66906066064826823913259982 | 256 | True |
| 9 | 1.40115329084992388147467229 | 4.66917155537951138888600460 | 512 | True |
| 10 | 1.40115478254661784121861253 | 4.66919515603001717402110880 | 1024 | True |

- Parameters strictly increasing: **True**
- Deltas strictly increasing: **True**
- Deltas nondecreasing: **True**
- All completed periods independently verified: **True**
- Alpha: **not computed** (not computed; no spatial scaling variable was defined)

Literature status: `reproduced_known_limit_at_finite_n`. Finite-n superstable ratio agrees with the published quadratic Feigenbaum delta; this is a reproduction, not a discovery.
Reference `4.669201609102990671853203820466201617258185577475768632745651343054117265635530130179812`; last observed `4.669195156030017174021108801191492093392147908605756405516325961597435502075013574720115107441916156`.

### z=3 — COMPLETE

| n | a_n (28 digits) | delta_n (28 digits) | P_n | period verified |
|---|---|---|---|---|
| 2 | 1.42802812679762439526968989 | — | 4 | True |
| 3 | 1.50621514629369052986803553 | 5.47441416179267459779679623 | 8 | True |
| 4 | 1.51929945268221690703754731 | 5.97563349362013560591761479 | 16 | True |
| 5 | 1.52145475598874952902146050 | 6.07074946197524300889955901 | 32 | True |
| 6 | 1.52180910078275744038813620 | 6.08250309579686126732332188 | 64 | True |
| 7 | 1.52186733810647147793153767 | 6.08449652919919434022626086 | 128 | True |
| 8 | 1.52187690925888295928630704 | 6.08467206563101688367828036 | 256 | True |
| 9 | 1.52187848224708903695951392 | 6.08469432542505474337465678 | 512 | True |
| 10 | 1.52187874076279860377955958 | 6.08469097956731282444923926 | 1024 | True |

- Parameters strictly increasing: **True**
- Deltas strictly increasing: **False**
- Deltas nondecreasing: **False**
- All completed periods independently verified: **True**
- Alpha: **not computed** (not computed; no spatial scaling variable was defined)

Literature status: `not_directly_reported_by_Hu_Mao`. Hu-Mao's actual paper studies z=2,4,6,8 and does not provide a z=3 table entry. The historical 4.894 value is not used as a literature comparator.

### z=4 — COMPLETE

| n | a_n (28 digits) | delta_n (28 digits) | P_n | period verified |
|---|---|---|---|---|
| 2 | 1.50393440785455922191062361 | — | 4 | True |
| 3 | 1.58225304517237897214918409 | 6.43441235844765650373719452 | 8 | True |
| 4 | 1.59316486333511718749684856 | 7.17741407983346057231377849 | 16 | True |
| 5 | 1.59466304624830278287846208 | 7.28336845034252222892045654 | 32 | True |
| 6 | 1.59486864741155577699320276 | 7.28684064565368038900609462 | 64 | True |
| 7 | 1.59489686637225007309667462 | 7.28592259227152413586180882 | 128 | True |
| 8 | 1.59490073989691468352317902 | 7.28508610055131272279432494 | 256 | True |
| 9 | 1.59490127162270653630814263 | 7.28481620406869596977533415 | 512 | True |
| 10 | 1.59490134461459431462826407 | 7.28472448154323398306701969 | 1024 | True |

- Parameters strictly increasing: **True**
- Deltas strictly increasing: **False**
- Deltas nondecreasing: **False**
- All completed periods independently verified: **True**
- Alpha: **not computed** (not computed; no spatial scaling variable was defined)

Literature status: `direct_even_order_comparison_at_paper_precision`. The map convention agrees for even z; the finite-n ratio is compared only with the four-digit table value.
Reference `7.284`; last observed `7.284724481543233983067019693384028906052800144731693923610066231867526499863537820118098963671613885`.

## Interpretation and limitations

- z=2 is a known Feigenbaum reproduction, not a discovery.
- z=3 and z=4 have strictly increasing period-verified parameter sequences, but their finite delta ratios are not monotone: z=3 decreases from n=9 to n=10, and z=4 decreases after n=6. Under the frozen claim gate, no monotone convergence claim is made for those families; the computation is a root-selection diagnosis.
- The actual Hu-Mao record is B. Hu and J. M. Mao, *Period doubling: Universality and critical-point order*, Phys. Rev. A 25, 3259–3261 (1982), DOI `10.1103/PhysRevA.25.3259`. It studies even orders z=2,4,6,8 and displays exact delta values 4.669, 7.284, 9.296, 10.948; it does not report z=3.
- The historical z=3/z=4 claims are not treated as evidence. Their root-selection problems are outside the repaired implementation.
- A finite scan cannot prove that no unresolved sign changes exist between grid points. The doubled-resolution check, direct/grouped period certificates, and explicit stop rule reduce but do not eliminate this numerical limitation.
- At 100 digits the configured zero tolerance is 1e-80; trailing digits beyond that numerical certificate should not be interpreted as additional independent accuracy.
- No alpha is reported because no spatial scaling variable is defined in this protocol.
- EXP-0014 historical files/results remain preserved and untouched.
