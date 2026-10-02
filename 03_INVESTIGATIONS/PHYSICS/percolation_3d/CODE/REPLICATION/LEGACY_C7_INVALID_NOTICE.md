# Legacy 3D C7 invalidity notice

The historical `C7_EXP-0011_report.json` is retained only as audit evidence.
It must not be cited as a passing control because its union-find checker copied
the primary routine's incorrect `z=0` slice-row boundary and did not test
opposite cubic planes.

The corrected same-stream implementation cross-check is:

`C7_QP008-AUDIT-R1-SMOKE_V2_corrected_report.json`

The earlier `C7_QP008-AUDIT-R1-SMOKE_corrected_report.json` is retained as
pre-hardening evidence; its recorded script hash predates the current C7
runner. The V2 report is the source-hash-bound authoritative smoke check.

That smoke report is also **not** an independent experimental replication; it
uses the primary config streams to compare two implementations. A production
scientific claim requires a separately preregistered stream policy and C7
scope.
