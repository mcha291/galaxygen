"""Closed unit vocabulary for field, input and constant declarations (rule A8).

Closed means a declaration cannot invent a unit: it must name a symbol in
``UNITS``. Extending the vocabulary is a deliberate edit to this file with a
``DECISIONS.md`` entry, never a side effect of declaring a field.

Symbols are ASCII because they are dictionary keys, appear in JSON and in code,
and non-ASCII look-alikes (``☉`` vs ``⊙``) are an invisible typo class
``[inferred]``. The ``display`` form carries the pretty version for humans.

No conversion factors live here. A factor is a factual claim needing a citation,
and nothing at S0 converts anything. Add them when a stage needs one.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Unit:
    symbol: str  # canonical ASCII key used in declarations, code and JSON
    display: str  # human form; may use non-ASCII
    dimension: str  # coarse physical dimension tag, for cross-checks


class UnknownUnit(ValueError):
    """A declaration named a unit outside the closed vocabulary."""


_UNITS: tuple[Unit, ...] = (
    # ratios, fractions, redshift, spin parameters
    Unit("dimensionless", "", "none"),
    # integer counts: a count has a meaningful zero and is not a ratio
    Unit("count", "", "count"),
    # length
    Unit("kpc", "kpc", "length"),
    Unit("pc", "pc", "length"),
    Unit("AU", "AU", "length"),
    Unit("Rsun", "R☉", "length"),
    Unit("Rearth", "R⊕", "length"),
    Unit("Rjup", "R♃", "length"),
    # mass
    Unit("Msun", "M☉", "mass"),
    Unit("Mearth", "M⊕", "mass"),
    Unit("Mjup", "M♃", "mass"),
    # time
    Unit("Gyr", "Gyr", "time"),
    Unit("Myr", "Myr", "time"),
    Unit("yr", "yr", "time"),
    Unit("day", "d", "time"),
    # kinematics and dynamics
    Unit("km/s", "km/s", "velocity"),
    Unit("km2/s2", "km²/s²", "specific_energy"),
    Unit("km/s/kpc", "km/s/kpc", "angular_frequency"),
    # star formation and densities
    Unit("Msun/yr", "M☉/yr", "mass_rate"),
    Unit("Msun/pc2", "M☉/pc²", "surface_density"),
    Unit("Msun/pc3", "M☉/pc³", "volume_density"),
    Unit("Msun/yr/kpc2", "M☉/yr/kpc²", "sfr_surface_density"),
    # chemistry
    Unit("dex", "dex", "log_ratio"),
    Unit("dex/kpc", "dex/kpc", "log_ratio_gradient"),
    # stellar and planetary
    Unit("K", "K", "temperature"),
    Unit("Lsun", "L☉", "luminosity"),
    Unit("mag", "mag", "magnitude"),
    Unit("Searth", "S⊕", "insolation"),
    # gravitation: G in the model's own length/velocity/mass units, so that
    # G·M/R is a squared velocity with no conversion anywhere (S1)
    Unit("kpc.km2/s2/Msun", "kpc km²/s²/M☉", "gravitational_constant"),
    # angles
    Unit("deg", "°", "angle"),
    Unit("rad", "rad", "angle"),
)

UNITS: dict[str, Unit] = {u.symbol: u for u in _UNITS}
DIMENSIONS: frozenset[str] = frozenset(u.dimension for u in _UNITS)


def unit(symbol: str) -> Unit:
    """Resolve a symbol or raise :class:`UnknownUnit` naming the vocabulary."""
    try:
        return UNITS[symbol]
    except (KeyError, TypeError):
        raise UnknownUnit(
            f"{symbol!r} is not in the closed unit vocabulary "
            f"(galaxy/core/units.py). Known symbols: {sorted(UNITS)}"
        ) from None
