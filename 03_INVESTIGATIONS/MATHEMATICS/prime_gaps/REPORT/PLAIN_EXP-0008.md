# PLAIN_EXP-0008 — prime gaps vs Poisson/Gallagher (Q-M002)

Decision: **H1_SUPPORTED**. Question: do prime gaps follow the Poisson/Gallagher model?

We counted the gaps between consecutive primes up to 100 million in four ranges, divided each gap by the log of its lower prime, and compared the result to an exponential distribution (the standard prediction for primes).

**Result:** G1/G2/G3 rejected and the deviation survives residue-class conditioning in 4 disjoint ranges; C7 agrees -> reproducible deviation.

**Every gate:** G1=FAIL, G2=PASS, G3=FAIL, G4=PASS, C1=PASS, C2=PASS, C3=PASS, C4=PASS, C5=PASS, C6=FAIL, C7=PASS

**Replication:** an independent implementation (different prime generator, different binning, different statistics entry point) agreed block by block.

**What this does NOT prove:** nothing new in number theory; this reproduces a known result (Gallagher 1976) with honest uncertainty. No novelty is claimed.
