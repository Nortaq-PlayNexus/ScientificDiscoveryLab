# Archived: superseded CODE/ copies

These are the *original* `CODE/` source files from this investigation, preserved
per RESEARCH_RULES.md §"nothing is ever deleted without explicit approval".

**They are superseded and must not be used.** They predate the pre-release review
and still contain two defects:

- **F08** — `calibration_passed = not require_calibration or True`, i.e. the
  field reporting whether the battery had been calibrated was unconditionally
  True.
- **F09** — the duplicate-indicator check compared a dict's value count to its
  key count, so it could never fire.

The canonical source is the investigation root (`battery.py`, `perturbation.py`,
`_rng.py`), which is what the test suite and `pytest.ini` collect. These archived
copies were left diverging at exactly the moment the defects were fixed, which is
precisely the "two copies, one authoritative" hazard the F05-F11 series is about.

Superseded by: `03_INVESTIGATIONS/COMPUTATIONAL_SCIENCE/ai_consciousness_indicators/`
See: `FALSIFICATION/F08_F11_integrity_defects.md`