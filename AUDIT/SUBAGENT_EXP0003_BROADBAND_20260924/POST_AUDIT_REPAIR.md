# Post-audit artifact-manifest repair

Date: 2026-09-24

The original `RESULTS/artifact_hashes.json` was intentionally preserved because
it is the malformed artifact identified as N-16. It ends with the literal bytes
`5c 6e` (`\\n`) after the final JSON brace, so strict JSON parsing fails.

A non-destructive validator was added at
`CODE/validate_artifact_hashes.py`. It:

1. records the source file's exact size and SHA-256;
2. salvages only the JSON prefix through the final closing brace;
3. verifies all 38 listed artifacts against their recorded byte counts and
   SHA-256 values;
4. writes a valid serialization at `RESULTS/artifact_hashes_repaired.json`; and
5. writes the complete machine-readable check to
   `RESULTS/artifact_hashes_validation.json`.

Validation result: **38/38 listed artifacts match; no file is missing or changed.**

The sidecar SHA-256 is
`c847d63dc210cd29a2612f6c26a33280ccf468bdfa3a5edd38d7207700abfb9d`.
This repair restores machine readability without altering the original evidence
or changing any scientific result.
