"""Disabled historical Q-P008 runner.

The source that previously occupied this path was archived as
``LEGACY_DISABLED/run_exp0011_historical_invalid.py`` with SHA-256
``9aed9b99edd0e65fcd0cfd921a48f4514ceed27a9dee558dcf3e9dece05ffb75``.

It must not be executed: the 2026-09-24 audit found incorrect 2D boundaries
for cubic labels, silently reduced sample counts, ragged-sample truncation,
a hardcoded out-of-config ``tau_L``, and nested cluster-tail arrays.

Use ``run_audit_repair.py`` with an explicit immutable audit-repair config.
Historical result files remain evidence and are not overwritten.
"""

from __future__ import annotations

import sys

MESSAGE = __doc__


def main() -> int:
    print(MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
