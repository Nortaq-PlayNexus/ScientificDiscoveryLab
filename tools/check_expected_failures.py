#!/usr/bin/env python3
"""Assert the test suite's failures are exactly the excluded-data ones.

    python tools/check_expected_failures.py <pytest-output-file>

The published tree omits 377 MB of raw simulation output (.npz, .sqlite3),
regenerable from the seeds in each preregistration. The read-only audit suite
reads some of it and therefore fails closed. Those failures are **correct
behaviour** — the audit refuses to run without the exact bytes it was audited
against — so CI must not treat them as breakage, and must not ignore the exit
status wholesale either.

The check is an exact set comparison against
``tools/expected_excluded_data_failures.txt``:

  a failure not on the list   -> real breakage, exit 1
  a listed test now passing   -> data was restored, the list is stale, exit 1
  a listed test absent entirely -> renamed or removed, exit 1

Why exact comparison rather than grepping for an error string: the previous CI
step grepped ``FAILED``/``ERROR`` summary lines for "historical evidence is
missing". Those summary lines contain only the node id, not the exception text,
so the grep matched nothing and the gate passed vacuously while all 20 failures
sat there unexamined. A gate that cannot fail is worse than no gate, because it
is read as a green light.

Exits 0 when the observed failure set equals the recorded one.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = ROOT / "tools" / "expected_excluded_data_failures.txt"
# "FAILED path::test" or "FAILED path::test - reason"; same for ERROR.
LINE = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)")


def read_text_any(path: Path) -> str:
    """Read a file written by either bash or PowerShell redirection.

    Bash writes UTF-8. Windows PowerShell 5.1 writes UTF-16LE with a BOM, which
    is not hypothetical: it is what produced the first run of this script, and
    reading it as UTF-8 yields zero parseable lines. That showed up as "observed
    failures: 0", which would have looked like a suite that passed cleanly.
    """
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    if raw[:3] == b"\xef\xbb\xbf":
        return raw.decode("utf-8-sig", errors="replace")
    return raw.decode("utf-8", errors="replace")


def observed(output: Path) -> list[str]:
    found: set[str] = set()
    for raw in read_text_any(output).splitlines():
        m = LINE.match(raw.strip())
        if m:
            found.add(m.group(1))
    return sorted(found)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} <pytest-output-file>", file=sys.stderr)
        return 2
    output = Path(argv[1])
    if not output.is_file():
        print(f"ERROR: {output} not found", file=sys.stderr)
        return 2

    expected = sorted(
        line.strip()
        for line in read_text_any(EXPECTED).splitlines()
        if line.strip() and not line.startswith("#")
    )
    got = observed(output)

    exp_set, got_set = set(expected), set(got)
    unlisted = sorted(got_set - exp_set)
    stale = sorted(exp_set - got_set)

    print(f"expected excluded-data failures: {len(exp_set)}")
    print(f"observed failures:               {len(got_set)}")

    if unlisted:
        print(f"\nUNEXPECTED ({len(unlisted)}) — not caused by excluded data:")
        for node in unlisted:
            print(f"  {node}")

    if stale:
        print(f"\nSTALE ({len(stale)}) — listed but did not fail:")
        for node in stale:
            print(f"  {node}")

    if not unlisted and not stale:
        print("\nOK: the failure set is exactly the recorded excluded-data set.")
        return 0

    print("\nFAIL: the failure set changed. Investigate before editing the list —")
    print("      a listed test that now passes may mean raw data was restored, or")
    print("      that the audit control stopped firing.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
