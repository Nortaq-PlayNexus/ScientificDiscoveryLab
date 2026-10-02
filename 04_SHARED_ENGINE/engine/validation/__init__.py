"""engine.validation — reproducibility validation tooling.

Currently contains the lightweight PRNG battery (rng_battery) used by EXP-0004
to certify the lab RNG and to validate the battery itself against known-good
generators.
"""

from . import rng_battery

__all__ = ["rng_battery"]