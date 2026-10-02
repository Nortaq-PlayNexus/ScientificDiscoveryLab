# Security Policy

## Scope

This is a small numerical library. It reads a CSV/JSON of indicator
assessments, computes scalars, and writes a JSON result. There is no web server,
no database, no authentication, no user input parsing, and no network code.

**Known vulnerabilities: none identified.**

## Dependencies

Three, all pinned by lower bound in `requirements.txt`:

- `numpy`
- `scipy`
- `pytest` (test-only)

None of these load untrusted input formats by default. Nothing here evaluates
pickle, YAML, or `eval`.

## What is deliberately NOT supported

If you need any of the following, this library is the wrong tool:

- Loading models or model weights
- Network access or fetching remote resources
- Parsing untrusted structured input (the `json` reader is standard-library only
  and takes no code execution paths, but the library does not promise safety on
  adversarial schemas)
- Running as a service
- Handling secrets or credentials

## Reporting

Open a private security advisory on the repository, or contact the maintainers
directly. Please do not open a public issue for an unfixed vulnerability.

Given the scope above, reports are most likely to concern the hash-verification
path (`experiment_verify.py`) or a correctness bug with security implications.
Correctness reports are equally welcome — several already fixed bugs are
documented in `FALSIFICATION/`.

## Integrity

Results in `RESULTS/` carry SHA-256 hashes over a canonical JSON encoding.
Verify with:

```bash
python experiment_verify.py RESULTS/experiment.json RESULTS/experiment_C003.json
```

This detects post-hoc edits to recorded results. `test_verify_helper_detects_tampering`
asserts that the verifier itself catches such edits rather than passing silently.