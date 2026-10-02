# Proposed Follow-up Email to Professor Swartzlander

> **DO NOT SEND UNCHANGED (audit hold 2026-09-24).** The external sandbox/raw
> chain and related laboratory claims require a fresh review. See
> `AUDIT_SUPERSESSION_NOTICE.md`.

- **Dossier:** Document 9 of 9
- **Date:** 2026-09-18
- **Recipient:** Professor Grover Swartzlander
- **Context:** written follow-up to the 2026-09-15 correspondence and the
  W. H. Carter / E. Wolf reply
- **Use:** ready to send as-is, or edit; the full technical backing lives in the
  other 8 documents of this dossier

---

**Subject: follow-up on the structured coherent-field question — audit results**

Dear Professor Swartzlander,

Thank you for your 15 September reply regarding our question about roughly
periodic dark/winding structures seen in a simulated coherent field
(λ = 694.3 nm), and for pointing us to W. H. Carter's work, possibly with
E. Wolf. Following that suggestion we rebuilt our literature pass from that
starting point, and we ran a formal, adversarial audit of the original
observation rather than trying to confirm it.

I want to give you a short, honest summary of where the investigation now
stands, because the honest result is mostly a set of methodological
corrections.

**What we found**

1. The observation came from an AI vision agent examining images rendered from
   a **simulation** (angular-spectrum propagation on a finite FFT grid). It is
   treated in our records strictly as an unverified observation report — a
   hypothesis generator, not a measurement.
2. The "~32 µm" periodicity is **real but explained**: the field was built on a
   8 × 6 lattice of phase vortices with column pitch 32.0 µm, so the structure
   is **inherited from the input, not emergent**. An emergence-vs-inheritance
   control confirmed this.
3. The phase vortices themselves are real topological defects: 48 unit-charge
   singularities, +24 / −24, net charge 0. Their density in well-resolved
   random fields reproduces the standard Kac-Rice / Nye-Berry prediction with
   n_meas/n_pred = 0.9952–1.0011 (within 0.5%) in an independent code.
4. The more interesting readings ("45 structures", an asymmetric + vs − split,
   a propagation-generated excess at z = 1280 µm) **did not survive**. We found
   three numerical artifacts that are now documented in detail: a
   phase-randomisation/propagation conflation, a detector that imposes a
   constant 8-pixel spacing floor (which manufactured the apparent "32 µm"
   invariance), and a pixelation resonance at exactly one grid configuration
   (256², z = 1280 µm) that our probes showed is not Talbot self-imaging and
   not scale-invariant topology.
5. All of this is simulation-side. We have not made any physical measurements,
   we are not claiming a discovery, and we are not proposing that light carries
   symbolic content — controls find none.

**What we would value from you**

Your guidance at this stage would help most in a few specific places (full
detail in the attached dossier's Section 12):

- The **canonical Carter (and Wolf) references**, so our literature pass can
  cite the exact papers you meant.
- A sanity check that our vortex-density reproduction (Kac-Rice / Nye-Berry)
  uses the standard constant — this is our strongest hard anchor.
- Whether a 256²-grid, λ = 0.6943 µm FFT propagator plausibly produces a
  plane-asymmetric feature distribution purely from finite-bin geometry, since
  that is the explanation our probes support for the last remaining anomaly.

If useful, I can send the nine-document dossier (executive summary, timeline,
methods and controls, results, negative results, open questions, data index)
and a simulation-only experiment plan with the exact parameters for an
interested lab to reproduce future measurements.

With thanks for your time,

Nathan — independent researcher (with large language model assistants for
engineering only; every cited result was obtained with deterministic,
reproducible code.)

---

*Note for the sender.* Attach or link `PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md`
(or just `EXECUTIVE_SUMMARY.md` + `FOLLOWUP_EMAIL.md`) when sending. Do not send
PDFs generated from images as "results"; the dossier's figures are simulation
renders, plainly labelled as such.