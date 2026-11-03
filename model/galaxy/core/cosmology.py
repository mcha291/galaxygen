"""The model's one cosmology: its two parameters, the age of the universe they give, and the closed form.

Until S87 the model held two ages of the universe (debt #148, S58): the bar stage turned the halo's assembly
redshift into the disc's age by the flat-ΛCDM closed form on H₀ and Ω_M (13.467 Gyr old), while the grid's
time axis ran to ``t_max`` = 13.8 Gyr ``[recall: age of the universe]``. They live here so both clocks read one
statement (rule A9: a duplicate that wins is a bug wearing the right name): ``models/level0.py`` declares
``H0`` and ``OMEGA_M`` from :data:`HUBBLE` and :data:`OMEGA_M`, the bar stage reads them through its constants,
and ``core/grids.py`` runs its time axis to :data:`AGE`, the same closed form at z = 0. ``core`` imports no model,
so the numbers sit in ``core`` and the declaration points at them, not the other way round.
"""

from __future__ import annotations

import math

# One kpc/(km/s) in Gyr: the IAU kiloparsec (3.0856775814913673e16 km) over a Julian gigayear (3.15576e16 s). A
# definition, which turns the Hubble constant's km/s/kpc into a time.
GYR_PER_KPC_PER_KMS = 3.0856775814913673e16 / 3.15576e16

# Level 0's two cosmological parameters (GALAXY_INPUTS.md §2, citing BHG16 §1): h = 0.7 and Ω_M = 0.3, flat.
# Their declarations, with their tags and what reads them, are ``models/level0.py``'s H0 and OMEGA_M.
HUBBLE = 0.07  # km/s/kpc: 70 km/s/Mpc
OMEGA_M = 0.3


def cosmic_time(redshift: float, hubble: float, omega_m: float) -> float:
    """The age of the universe at ``redshift``, in Gyr, for flat matter and a cosmological constant:
    t(z) = (2 / (3 H₀ √Ω_Λ)) asinh(√(Ω_Λ/Ω_M) (1 + z)^{−3/2}), Ω_Λ = 1 − Ω_M - the closed form of the
    Friedmann equation with no radiation and no curvature [inferred: the textbook integral; held against
    its own quadrature in tests/test_bar.py]. ``hubble`` in km/s/kpc, as the model holds H₀.

    Flat because the model's one other use of Ω_M, the virial overdensity the halo's concentration is
    quoted at, is the flat-universe form (``halo.virial_overdensity``): one cosmology, not two.
    """
    omega_l = 1.0 - omega_m
    scale = 2.0 / (3.0 * hubble * math.sqrt(omega_l)) * GYR_PER_KPC_PER_KMS
    return scale * math.asinh(math.sqrt(omega_l / omega_m) * (1.0 + redshift) ** -1.5)


# The age of the universe today by the model's own cosmology, 13.467 Gyr: the grid's time axis runs from t = 0 to
# here (S87, debt #148), so "now" on the grid is the moment the bar stage's lookback times are counted back from.
AGE = cosmic_time(0.0, HUBBLE, OMEGA_M)
