"""Halo: the NFW dark halo and the mass budget of the galaxy (checkpoint 1).

One implementation, shared by both models (GALAXY_PLAN.md §2): nothing here
differs between the simple and the advanced pass, so the model chooses the same
code and the field set is identical.

What it computes, and how much freedom each step has (GALAXY_INPUTS.md §4b):

- **R₂₀₀ is arithmetic (verdict A).** ``R₂₀₀ = (3 M₂₀₀ / 800 π ρ_crit)^(1/3)`` is
  the *definition* of the radius enclosing 200 ρ_crit, not a fitted relation, so
  it has no freedom at all once M₂₀₀ and the cosmology are fixed.
- **c₂₀₀ is correlated with scatter (verdict C)**, absorbed into the assembly
  redshift by ruling 5: ``c_vir = CONCENTRATION_NORM (1 + z_f)``, quoted at the
  virial overdensity Δ_vir(Ω_M) and converted through the NFW profile to the c₂₀₀
  the halo is built with (S13, debt #12). The scatter it does not absorb is a
  calibration debt, not a variable.
- **The baryon budget** splits M₂₀₀ into what became the disc and what stayed
  dark. ``m_d = f_b × baryon_retention`` (ruling 9). The dark halo carries
  ``(1 − m_d) M₂₀₀``, so the disc's mass is not counted twice in the rotation
  curve — at m_d ≈ 0.05 double counting would be worth about 6 km/s at R₀,
  which is twice acceptance row 3's error bar ``[inferred]``.

- **The halo's response to the disc (S14, debt #6).** The baryons that became the
  disc were once spread through the halo like the dark matter; as they settled
  into an exponential of scale length ``R_d = λ_d R₂₀₀/√2`` every dark-matter
  shell moved inward after them. The stage solves that contraction on its own
  radial mesh — the invariant is ``r M(r̄)`` with the orbit-averaged radius
  ``r̄ = A R₂₀₀ (r/R₂₀₀)^w`` ``[recall: Gnedin et al. 2004]``, ``A = w = 1``
  being the circular-orbit form ``[recall: Blumenthal et al. 1986]`` — and every
  profile it publishes is the contracted one. The scale length is therefore
  computed here and the disc stage reads it (rule A9: one opinion, held where
  the halo needs it first).

- **The two ends of the angular-momentum distribution (S16, S17).** The retained
  baryons carry the halo's own distribution of specific angular momentum
  ``[recall: Bullock et al. 2001]``, and one exponential disc cannot hold it: the
  distribution allots more mass than the exponential at both ends and less in
  between. Beyond the outer crossing the surplus is the extended gas disc (debt
  #18, S16); inside the inner one it is mass with too little angular momentum to
  be in any exponential, and that is the **central spheroid** (debt #11, S17).
  Both are computed here, from one construction read twice, because both are
  splits of the budget this stage owns and both need the potential on this
  stage's own mesh — and because the halo contracts around all three components,
  which it cannot do around a spheroid a later stage would derive. What the
  spheroid is *not* is a stage: a stage that only republished these four scalars
  would be the duplicate rule A9 forbids.

The halo owns the budget rather than the disc because M₂₀₀ and its split are
properties of the halo; the disc stage turns the baryon half into a disc.

"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage


def mu(x: np.ndarray | float) -> np.ndarray | float:
    """The NFW mass factor ``ln(1+x) − x/(1+x)``; ``M(<r) = M_tot μ(r/r_s)/μ(c)``."""
    return np.log1p(x) - x / (1.0 + x)


def rho_crit(H0: float, G: float) -> float:
    """Critical density ``3H₀²/8πG`` in M☉/kpc³, with H₀ in km/s/kpc and G in kpc (km/s)²/M☉."""
    return 3.0 * H0 * H0 / (8.0 * math.pi * G)


def virial_radius(M200: float, H0: float, G: float) -> float:
    """R₂₀₀ from its definition: the radius enclosing a mean density of 200 ρ_crit."""
    return (3.0 * M200 / (800.0 * math.pi * rho_crit(H0, G))) ** (1.0 / 3.0)


def virial_overdensity(omega_m: float) -> float:
    """Δ_vir in units of ρ_crit at z = 0: ``18π² + 82x − 39x²``, x = Ω_M − 1 [recall: Bryan & Norman 1998]."""
    x = omega_m - 1.0
    return 18.0 * math.pi**2 + 82.0 * x - 39.0 * x * x


def concentration_at(delta: float, c_ref: float, delta_ref: float) -> float:
    """Concentration of one NFW halo at overdensity ``delta``, given ``c_ref`` at ``delta_ref``.

    The mean density inside x scale radii goes as μ(x)/x³, so ``Δ c³ / μ(c)`` is the
    halo's own invariant (its scale density in units of ρ_crit) and the conversion is
    a root, not a fit. Bisected; μ(x)/x³ is monotone.
    """
    target = delta_ref * c_ref**3 / mu(c_ref)
    lo, hi = 0.5, 60.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if delta * mid**3 / mu(mid) < target else (lo, mid)
    return 0.5 * (lo + hi)


def nfw_circular_velocity(R: np.ndarray | float, M: float, r_s: float, c: float, G: float) -> np.ndarray | float:
    """Circular velocity of an NFW halo of total mass ``M`` inside R₂₀₀ = c·r_s."""
    return np.sqrt(G * M * mu(np.asarray(R, dtype=float) / r_s) / mu(c) / np.asarray(R, dtype=float))


def scale_length(spin: float, R200: float) -> float:
    """MMW98: ``R_d = λ_d R₂₀₀ / √2``, with j_d/m_d folded into λ_d (ruling 8)."""
    return spin * R200 / math.sqrt(2.0)


def disc_enclosed_mass(r: np.ndarray | float, M_d: float, R_d: float) -> np.ndarray | float:
    """Mass of an exponential disc inside cylindrical radius ``r``: ``M_d [1 − e^(−x)(1 + x)]``, x = r/R_d.

    The spherical enclosed baryon mass the contraction responds to, as MMW98 take it
    [recall: Mo, Mao & White 1998 §2.3]; the razor-thin disc's own flattening is not
    carried into the halo's response.
    """
    x = np.asarray(r, dtype=float) / R_d
    return M_d * (-np.expm1(-x) - x * np.exp(-x))


# The contraction is solved on its own radial mesh, not on the grid: the potential
# is an integral inward from beyond R₂₀₀ and the grid stops at 30 kpc. Log-spaced
# from well inside the first cell to MESH_OUTER × R₂₀₀. The scalars it feeds do not
# move with N_R, and a test doubles the mesh to show they do not move with this either.
MESH_POINTS = 600
MESH_INNER = 1.0e-3  # kpc
MESH_OUTER = 1.5  # in units of R₂₀₀


def angular_momentum_excess(
    R: np.ndarray, j: np.ndarray, M_d: float, R_d: float, mu: float
) -> tuple[np.ndarray, np.ndarray]:
    """``(the exponential, the angular-momentum distribution mapped onto the plane)``, both in M☉/kpc².

    Bullock et al. 2001's universal profile, ``M(< j) = M μ j/(j₀ + j)`` for ``j ≤ j₀/(μ − 1)``,
    mapped onto the plane through the specific angular momentum of a circular orbit at each
    radius, ``j(R)`` on the model's own rotation curve, with ``j₀`` fixed so that the profile's
    mean j is the exponential disc's — the disc λ_d already sets. Their difference is what the
    exponential assumption gets wrong, and it has two signs: the profile lies *above* the
    exponential at both ends and below it in between, so there are two crossings and two
    excesses. Beyond the outer crossing the excess is gas the exponential never held (S16,
    debt #18: :func:`angular_momentum_tail`); inside the inner one it is mass with too little
    angular momentum for any exponential disc, which is the bulge (S17, debt #11:
    :func:`angular_momentum_core`). One construction, read twice, so the two components cannot
    drift apart (rule A9). Profiles are normalised on ``R``, which the stage makes its own mesh
    so that no scalar inherits the grid's resolution (rule B2's cousin: a scalar that moves with
    N_R is a hidden quadrature).
    """
    R, j = np.asarray(R, dtype=float), np.asarray(j, dtype=float)
    ring = 2.0 * math.pi * R
    disc = M_d / (2.0 * math.pi * R_d * R_d) * np.exp(-R / R_d)  # M☉/kpc²
    j_mean = float(np.trapezoid(j * disc * ring, R) / np.trapezoid(disc * ring, R))
    x = 1.0 / (mu - 1.0)
    j0 = j_mean / (mu * (math.log1p(x) - x / (1.0 + x)))  # the profile's own mean is μ j₀ [ln(1 + x) − x/(1 + x)]
    dMdj = mu * j0 / (j0 + j) ** 2 * (j < j0 * x)
    profile = np.maximum(dMdj * np.gradient(j, R) / ring, 0.0)
    return disc, profile * M_d / float(np.trapezoid(profile * ring, R))


def angular_momentum_tail(
    R: np.ndarray, j: np.ndarray, M_d: float, R_d: float, mu: float
) -> tuple[np.ndarray, float, float]:
    """The high-j tail: the excess beyond the outer crossing (S16, debt #18).

    Returns ``(tail in M☉/pc², its share of M_d, the crossing radius)``; the tail is zero
    inside the crossing. The low-j excess inside is :func:`angular_momentum_core`.
    """
    R = np.asarray(R, dtype=float)
    ring = 2.0 * math.pi * R
    disc, profile = angular_momentum_excess(R, j, M_d, R_d, mu)
    excess = profile - disc
    above = np.flatnonzero(excess > 0.0)
    if above.size == 0:
        return np.zeros_like(R), 0.0, float(R[-1])
    runs = above[np.concatenate([[True], np.diff(above) > 1])]  # the first index of each run above the exponential
    R_c = float(R[runs[-1]])
    tail = np.where(R >= R_c, np.maximum(excess, 0.0), 0.0)
    share = float(np.trapezoid(tail * ring, R) / M_d)
    return tail * 1.0e-6, share, R_c


def angular_momentum_core(
    R: np.ndarray, j: np.ndarray, M_d: float, R_d: float, mu: float
) -> tuple[float, float, float, float]:
    """The low-j excess: the mass the exponential disc cannot hold, inside the inner crossing (S17, debt #11).

    The mirror of :func:`angular_momentum_tail`. Inside the inner crossing the distribution
    allots more mass than the exponential holds, and the surplus has too little angular
    momentum to be in *any* exponential disc of this scale length: it is the material that
    settles into the central spheroid. Returns ``(mass in M☉, the radius inside which half of
    it lies, the crossing radius, its mass-weighted specific angular momentum)``.

    Two things it is not. It is not a formation channel — whether the mass ends up in a
    classical bulge built by dissipation or in the box/peanut a bar makes of the inner disc is
    a distinction this model does not draw, and ``bulge_classical_fraction`` measures the
    rotation it carries rather than assuming one. And the radii are the *mapping's*: each
    element is placed where a circular orbit would carry its j, which is exactly the assumption
    that fails for material this far below the disc's angular momentum, so the radius is used
    only to set the spheroid's half-mass radius and never as a position.
    """
    R = np.asarray(R, dtype=float)
    ring = 2.0 * math.pi * R
    disc, profile = angular_momentum_excess(R, j, M_d, R_d, mu)
    excess = profile - disc
    above = np.flatnonzero(excess > 0.0)
    if above.size == 0:
        return 0.0, float(R[0]), float(R[0]), 0.0
    ends = above[np.concatenate([np.diff(above) > 1, [True]])]  # the last index of each run above the exponential
    R_c = float(R[ends[0]])
    core = np.where(R <= R_c, np.maximum(excess, 0.0), 0.0)
    mass = float(np.trapezoid(core * ring, R))
    if mass <= 0.0:
        return 0.0, float(R[0]), R_c, 0.0
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (core[1:] * R[1:] + core[:-1] * R[:-1]) * np.diff(R))])
    r_half = float(np.interp(0.5 * cum[-1], cum, R))
    j_mean = float(np.trapezoid(np.asarray(j, dtype=float) * core * ring, R) / mass)
    return mass, r_half, R_c, j_mean


# --- the central spheroid ----------------------------------------------------


def hernquist_enclosed(r: np.ndarray | float, M: float, a: float) -> np.ndarray | float:
    """Hernquist 1990: ``M(<r) = M r²/(r + a)²``."""
    r = np.asarray(r, dtype=float)
    return M * r * r / (r + a) ** 2


def hernquist_density(r: np.ndarray | float, M: float, a: float) -> np.ndarray | float:
    """``ρ(r) = M a / (2π r (r + a)³)``, the density whose enclosed mass is :func:`hernquist_enclosed`."""
    r = np.asarray(r, dtype=float)
    return M * a / (2.0 * math.pi * r * (r + a) ** 3)


# r²/(r + a)² = ½ at r = a(1 + √2): the Hernquist sphere's own half-mass radius, algebra
# rather than a citation, and a test reproduces it. The spheroid's scale is set by equating
# this to the radius inside which half the low-j excess lies. Matching the *projected*
# half-mass radius instead would read a = r_half/1.8153 [recall: Hernquist 1990]; that is a
# named alternative and not the choice (rule B12), because the excess's radius is a mass
# inside a radius and so is this one, with no projection assumed on either side.
HERNQUIST_HALF_MASS = 1.0 + math.sqrt(2.0)


def spheroid_dispersion(
    r: np.ndarray, M: float, a: float, GM_total: np.ndarray
) -> tuple[float, float]:
    """Mass-weighted 1-D velocity dispersion of a Hernquist spheroid, isotropic, in the total potential.

    The spherical isotropic Jeans equation, integrated inward from the mesh's outer edge:

        ρ σ_r²(r) = ∫_r^∞ ρ(r') G M_total(r') / r'² dr'

    with ``GM_total`` the whole enclosed mass times G — dark halo, disc and spheroid — because
    the spheroid is not isolated: on its own gravity alone the dispersion is a third lower, and
    reporting that would be reporting a different galaxy's bulge. Isotropy is the assumption,
    and it is the one that makes this a derivation rather than a fit: no rotation is subtracted
    and none is added, so a bulge that in fact rotates has some of its support counted here as
    dispersion. Returns ``(σ inside the half-mass radius, σ over the whole spheroid)``; the
    first is what acceptance row 14 reads, because the source's 113 km/s is mass-weighted
    within the bulge's half-mass radius `[verified: BHG16 §4.3, "the rms is σ_rms,b ≈ 113 km/s,
    to ≈3 km/s"]`.
    """
    r = np.asarray(r, dtype=float)
    rho = hernquist_density(r, M, a)
    f = rho * np.asarray(GM_total, dtype=float) / r**2
    seg = 0.5 * (f[1:] + f[:-1]) * np.diff(r)
    integral = np.concatenate([np.cumsum(seg[::-1])[::-1], [0.0]])  # ∫_r^∞, on the mesh
    sigma_r2 = integral / rho
    dM = rho * 4.0 * math.pi * r**2
    inside = r <= a * HERNQUIST_HALF_MASS
    half = float(np.trapezoid((sigma_r2 * dM)[inside], r[inside]) / np.trapezoid(dM[inside], r[inside]))
    whole = float(np.trapezoid(sigma_r2 * dM, r) / np.trapezoid(dM, r))
    return math.sqrt(half), math.sqrt(whole)


def contracted_halo(
    r_f: np.ndarray, M200: float, r_s: float, c: float, m_d: float, R_d: float, R200: float, A: float, w: float,
    enclosed: Callable[[np.ndarray], np.ndarray] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """The dark halo's response to the disc: final dark mass and shell displacement at each ``r_f``.

    Every shell of the initial NFW halo — total mass M₂₀₀, the disc's baryons spread
    through it like the dark matter — moves inward as the baryons settle into the disc,
    conserving ``r M(r̄)`` with ``r̄ = A R₂₀₀ (r/R₂₀₀)^w`` [recall: Gnedin et al. 2004;
    A = w = 1 is Blumenthal et al. 1986]:

        r_i M_i(r̄_i) = r_f [ (1 − m_d) M_i(r̄_i) + M_disc(r̄_f) ]

    — the dark mass inside r̄_f after the move is approximated by what was inside r̄_i
    before, which is what makes the equation explicit — and the shell itself carries its
    mass: the dark mass inside r_f afterwards is what was inside r_i before, (1 − m_d)
    M_i(r_i). That last step is at the physical radius, not the orbit-averaged one:
    attaching the mass to r̄_f instead makes A cancel out of the whole calculation, a
    defect S14 found by probing a third (A, w) and reading the default's number back.
    The root is bisected in log r_i between 0.01 r_f and 20 r_f, where the two sides are
    known to have crossed, vectorised over the mesh (rule A1: bounded and cheap). Returns
    ``(M_dark(r_f), r_i/r_f)``. With no disc the root is r_i = r_f exactly and the halo
    comes back unchanged. ``enclosed(r)`` is the baryons' enclosed mass the halo responds
    to; by default the exponential's, and since S16 the exponential plus the tail.
    """
    r_f = np.asarray(r_f, dtype=float)
    M_d = m_d * M200

    def initial(r: np.ndarray) -> np.ndarray:
        return M200 * mu(r / r_s) / mu(c)

    def bar(r: np.ndarray) -> np.ndarray:
        return A * R200 * (r / R200) ** w

    rb_f = bar(r_f)
    disc = disc_enclosed_mass(rb_f, M_d, R_d) if enclosed is None else enclosed(rb_f)
    lo, hi = 1.0e-2 * r_f, 2.0e1 * r_f
    for _ in range(80):
        mid = np.sqrt(lo * hi)
        M_i = initial(bar(mid))
        from_further_out = mid * M_i < r_f * ((1.0 - m_d) * M_i + disc)
        lo, hi = np.where(from_further_out, mid, lo), np.where(from_further_out, hi, mid)
    r_i = np.sqrt(lo * hi)
    return (1.0 - m_d) * initial(r_i), r_i / r_f


def potential_of(r: np.ndarray, M: np.ndarray, dark: float, r_s: float, c: float, G: float) -> np.ndarray:
    """Φ(r) of a spherical profile ``M(r)`` tabulated on an increasing mesh, zero at infinity.

    Integrated inward from the mesh's outer edge, where the profile is taken to be the
    uncontracted NFW halo's — the disc is all inside by then and the invariant returns
    r_i = r_f at R₂₀₀ — so the outer boundary is the analytic NFW potential and the
    integral carries only what the mesh resolves: ``dΦ = G M / r² dr = (G M / r) d ln r``,
    trapezoid in ln r.
    """
    r = np.asarray(r, dtype=float)
    f = G * np.asarray(M, dtype=float) / r
    seg = 0.5 * (f[1:] + f[:-1]) * np.diff(np.log(r))
    inward = np.concatenate([np.cumsum(seg[::-1])[::-1], [0.0]])
    phi_top = -G * dark * math.log1p(r[-1] / r_s) / (mu(c) * r[-1])
    return phi_top - inward


def _loglog(x: np.ndarray | float, xp: np.ndarray, fp: np.ndarray) -> np.ndarray | float:
    """Interpolate a positive tabulated profile linearly in log–log."""
    return np.exp(np.interp(np.log(x), np.log(xp), np.log(fp)))


def density_of(r: np.ndarray, M: np.ndarray) -> np.ndarray:
    """ρ(r) of a spherical profile ``M(r)`` tabulated on a log mesh: ``M (d ln M / d ln r) / 4π r³``.

    The logarithmic derivative is second-order on the mesh; with no disc it returns the
    NFW density to a part in 10⁵ (S15, the instrument before the physics).
    """
    r, M = np.asarray(r, dtype=float), np.asarray(M, dtype=float)
    return M * np.gradient(np.log(M), np.log(r)) / (4.0 * math.pi * r**3)


def nfw_density(r: np.ndarray | float, M: float, r_s: float, c: float) -> np.ndarray | float:
    """Density of an NFW halo of mass ``M`` inside ``c r_s``: ``ρ_s / (x (1 + x)²)``, x = r/r_s."""
    x = np.asarray(r, dtype=float) / r_s
    return M / (4.0 * math.pi * r_s**3 * mu(c)) / (x * (1.0 + x) ** 2)


def concentration_enclosing(M_inside: float, r: float, M: float, R200: float) -> float:
    """The c₂₀₀ of the NFW halo of mass ``M`` inside ``R200`` that encloses ``M_inside`` at ``r``.

    What a measurement anchored on the inner halo reads off a profile that is not NFW any
    more: the contracted halo's effective concentration (S15). μ(c r/R₂₀₀)/μ(c) rises with c
    for r < R₂₀₀, so the root is bisected. With no disc it returns the halo's own c.
    """
    x = r / R200
    lo, hi = 0.5, 60.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if M * mu(mid * x) / mu(mid) < M_inside else (lo, mid)
    return 0.5 * (lo + hi)


HALO_VIRIAL_MASS = FieldDecl(
    name="halo_virial_mass",
    label="Halo mass M₂₀₀",
    unit="Msun",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Total mass inside R₂₀₀, dark and baryonic. Equal to the halo_mass input: the model does "
        "not derive it, and acceptance row 19 is therefore a check that the default lies inside the "
        "literature span 1.0–1.3 × 10¹² M☉, not a check on any physics."
    ),
)

HALO_VIRIAL_RADIUS = FieldDecl(
    name="halo_virial_radius",
    label="Virial radius R₂₀₀",
    unit="kpc",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Radius enclosing a mean density of 200 ρ_crit. A definition, not a relation (verdict A), "
        "so the only freedom is the cosmology. The surprise is how large it is: 213 kpc at the "
        "default mass, an order of magnitude beyond every stellar structure the model publishes. "
        "It is not the R_vir ≈ 255 kpc quoted in GALAXY_INPUTS.md §6, which is a different "
        "overdensity at a different mass — see DECISIONS.md D30."
    ),
)

HALO_CONCENTRATION = FieldDecl(
    name="halo_concentration",
    label="Concentration c₂₀₀",
    unit="dimensionless",
    kind=Kind.SCALAR,
    about=(
        "R₂₀₀/r_s, derived from the assembly redshift by ruling 5: haloes that assembled early are "
        "concentrated because they froze in the mean density of an earlier, denser universe. "
        "Since S13 it is halo_concentration_virial converted through the NFW profile from Δ_vir to "
        "200 ρ_crit (debt #12). Verdict C: the epoch absorbs most of the galaxy-to-galaxy scatter "
        "and not all of it. This is the halo before it responded to the disc — 8.24 at the default "
        "epoch, the ΛCDM median for the default mass since S15 — and a measurement of the Milky "
        "Way's halo reads halo_concentration_contracted, not this (D117)."
    ),
)
HALO_CONCENTRATION_VIRIAL = FieldDecl(
    name="halo_concentration_virial",
    label="Concentration c_vir",
    unit="dimensionless",
    kind=Kind.SCALAR,
    about=(
        "The normalisation K times (1 + z_f) as Wechsler et al. quote it, at the virial overdensity "
        "Δ_vir(Ω_M) ≈ 101 ρ_crit. Published so the conversion to c₂₀₀ can be read off; until S13 "
        "this number was used as c₂₀₀ unconverted (debt #12)."
    ),
)

HALO_SCALE_RADIUS = FieldDecl(
    name="halo_scale_radius",
    label="NFW scale radius r_s",
    unit="kpc",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about="R₂₀₀/c₂₀₀. The radius where the NFW logarithmic slope passes through −2.",
)

HALO_DARK_MASS = FieldDecl(
    name="halo_dark_mass",
    label="Dark halo mass",
    unit="Msun",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "(1 − m_d) M₂₀₀: what the NFW profile carries once the disc's baryons are taken out, so "
        "that the rotation curve does not count them twice."
    ),
)

BARYON_MASS_TOTAL = FieldDecl(
    name="baryon_mass_total",
    label="Retained baryon mass",
    unit="Msun",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "f_b × baryon_retention × M₂₀₀: every baryon the galaxy kept, stars and gas together. "
        "Until S2 splits off a gas phase the disc stage treats all of it as stars, so "
        "stellar_mass_total is high by the gas mass — about 8 × 10⁹ M☉, or 14% (debt #11)."
    ),
)

DISC_MASS_FRACTION = FieldDecl(
    name="disc_mass_fraction",
    label="Disc mass fraction m_d",
    unit="dimensionless",
    kind=Kind.SCALAR,
    about=(
        "Retained baryons as a fraction of M₂₀₀. Ruling 9 puts the Milky Way near 0.055; the "
        "default inputs give 0.053. Only about a third of the cosmic share survives feedback."
    ),
)

HALO_CIRCULAR_VELOCITY_SUN = FieldDecl(
    name="halo_circular_velocity_sun",
    label="Halo circular velocity at R₀",
    unit="km/s",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "The contracted dark halo's contribution to v_c at the solar radius, read off the "
        "contraction mesh rather than the grid so that it does not inherit the radial resolution. "
        "Published as a scalar so the sfh stage can add the baryons' own contribution without a "
        "second copy of the halo (rule A9). halo_circular_velocity_sun_initial is the same number "
        "before the halo responded to the disc; the difference is what debt #6 was worth at R₀."
    ),
)

HALO_CIRCULAR_VELOCITY_SUN_INITIAL = FieldDecl(
    name="halo_circular_velocity_sun_initial",
    label="Halo circular velocity at R₀ before contraction",
    unit="km/s",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "The NFW halo of (1 − m_d) M₂₀₀ at R₀, analytically, before its shells moved inward after "
        "the disc's baryons (S14, debt #6). Published so the contraction can be read off as a "
        "difference, the way halo_concentration_virial lets the c_vir → c₂₀₀ conversion be read."
    ),
)

HALO_DENSITY_SUN = FieldDecl(
    name="halo_density_sun",
    label="Dark matter density at R₀",
    unit="Msun/pc3",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "The contracted halo's density at the solar radius, read off the contraction mesh (S15). "
        "It is the one property of the dark halo measured without the rotation curve — from the "
        "vertical kinematics of the stars — so it judges the contraction independently of row 3: "
        "0.3–0.5 GeV/cm³, 0.008–0.013 M☉/pc³ [recall: de Salas & Widmark 2021, the global "
        "analyses]. The surprise is how little the response moves it: the dark mass inside R₀ "
        "rises 70% and the density there 16%, because the response steepens the profile inside "
        "R₀ more than it raises it at R₀ — so every epoch from 1 to 3 reads inside the span (0.28 "
        "to 0.43 GeV/cm³) and the number does not discriminate between them (D117)."
    ),
)

HALO_CONCENTRATION_CONTRACTED = FieldDecl(
    name="halo_concentration_contracted",
    label="Effective concentration of the contracted halo",
    unit="dimensionless",
    kind=Kind.SCALAR,
    about=(
        "The c₂₀₀ of the NFW halo of the same dark mass that encloses the same mass inside R₀ as "
        "the contracted one (S15). The contracted profile is not NFW, and a measurement of the "
        "Milky Way's halo fits one to it anyway; the 10–18 that GALAXY_INPUTS.md §4b quotes are "
        "such fits, so they are measurements of this number and not of halo_concentration, which "
        "is the halo before it responded to the disc. Until S15 the epoch's default was validated "
        "by comparing the two (debt #12)."
    ),
)

HALO_CONTRACTION = FieldDecl(
    name="halo_contraction",
    label="Shell displacement r_i/r_f",
    unit="dimensionless",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("magma", scale="linear", lo=1.0, hi=2.0),
    meaningful_zero=False,
    about=(
        "Where the dark matter now at R came from, as a ratio: the initial radius of the shell "
        "over its final one. Unity means no response; it tends to a constant near the centre, "
        "where the disc and the halo both enclose mass as R², and falls to unity at R₂₀₀ where "
        "the whole disc is inside. Zero is not meaningful: a shell cannot have come from nowhere."
    ),
)

HALO_ENCLOSED_MASS = FieldDecl(
    name="halo_enclosed_mass",
    label="Dark mass inside R",
    unit="Msun",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("viridis", scale="log"),
    meaningful_zero=True,
    about=(
        "Cumulative dark mass after the halo has contracted around the disc (S14): the NFW "
        "profile's shells, each moved inward by halo_contraction. Rises logarithmically: half the "
        "halo's mass lies outside 60 kpc."
    ),
)

HALO_CIRCULAR_VELOCITY = FieldDecl(
    name="halo_circular_velocity",
    label="Halo circular velocity",
    unit="km/s",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("viridis", scale="linear", lo=0.0, hi=300.0),
    meaningful_zero=True,
    about=(
        "√(GM(<R)/R) for the contracted dark halo alone. Nearly flat across the disc, which is "
        "the whole reason a halo is needed: the baryons alone fall off Keplerian beyond a few "
        "scale lengths."
    ),
)

HALO_POTENTIAL = FieldDecl(
    name="halo_potential",
    label="Halo potential Φ(R, z)",
    unit="km2/s2",
    kind=Kind.FIELD,
    axes=("R", "z"),
    ramp=Ramp("magma", scale="linear"),
    meaningful_zero=False,
    about=(
        "Potential of the contracted dark halo at r = √(R² + z²), on the half-space z ≥ 0 by "
        "plane symmetry: the mesh's mass profile integrated inward from the analytic NFW value "
        "beyond R₂₀₀. Spherical, so it varies with z only through r; the disc's own flattened "
        "potential arrives with the vertical structure at S2. Zero is not meaningful: the zero "
        "point is at infinity."
    ),
)
HALO_POTENTIAL_MIDPLANE = FieldDecl(
    name="halo_potential_midplane",
    label="Halo potential Φ(R, 0)",
    unit="km2/s2",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("magma", scale="linear"),
    meaningful_zero=False,
    about=(
        "The same potential in the plane, z = 0 exactly: what the advanced chemistry's escape "
        "velocity climbs out of. Until S12 that stage read halo_potential's first z-row, half a "
        "cell above the plane at a height set by N_z (debt #35). Deeper since S14 by the "
        "contraction, which is why WIND_SPEED was re-examined then (rule B10)."
    ),
)

INFALL_TAIL_SURFACE_DENSITY = FieldDecl(
    name="infall_tail_surface_density",
    label="High-j accretion tail Σ(R)",
    unit="Msun/pc2",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("cividis", scale="log"),
    meaningful_zero=True,
    about=(
        "Everything that will ever accrete beyond what the exponential disc holds: the high-j "
        "tail of the halo's angular-momentum distribution (its shape a Level 0 constant), mapped onto the "
        "plane on the model's own rotation curve (S16, debt #18). Zero inside the crossing radius, "
        "3–4 M☉/pc² from 15 to 20 kpc, and it ends where the distribution's j_max lands, near 25 "
        "kpc. The surprise is what it is not: a timescale. At these radii the inside-out law "
        "already accretes over 10–20 Gyr, and three arrival laws read the same on every row but "
        "row 2, within 0.05 there (D119). Debt #18 wanted a component the threshold protects; this "
        "is one, and it still forms 0.2 M☉/yr of stars where it overlaps the disc's own gas."
    ),
)

INFALL_TAIL_SHARE = FieldDecl(
    name="infall_tail_share",
    label="Share of the budget in the tail",
    unit="dimensionless",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "The tail's mass over the retained budget: about 0.09 at the default, and nearly the same "
        "for any μ between 1.15 and 1.4 — the profile's shape moves the tail's radius, not its "
        "mass. Derived, not chosen: the register asked for a component 'sized to the observed HI "
        "disc', and this one is sized by the halo's angular momentum instead (debt #47 holds "
        "the difference)."
    ),
)

INFALL_TAIL_INNER_RADIUS = FieldDecl(
    name="infall_tail_inner_radius",
    label="Tail's inner radius",
    unit="kpc",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "The outer crossing of the distribution's profile and the exponential: inside it the "
        "exponential holds more than the distribution allots, outside it less. About 12 kpc at "
        "the default, 4.6 scale lengths — beyond the stellar disc's edge, which is why row 4 does "
        "not move (the check debt #18 named for a component high enough in angular momentum)."
    ),
)

BULGE_STELLAR_MASS = FieldDecl(
    name="bulge_stellar_mass",
    label="Bulge stellar mass",
    unit="Msun",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Acceptance row 12: the central spheroid, derived as the low-j end of the same "
        "angular-momentum distribution the high-j tail comes from (S17, debt #11) — the mass the "
        "exponential disc cannot hold because its angular momentum is too small, 13% of the "
        "retained budget, all of it inside 2.5 kpc. It is stellar and carries no gas: at these "
        "radii and densities the depletion time is a percent of the disc's, so the model takes "
        "the spheroid to have finished forming stars long ago and the star formation history "
        "never sees this mass. The surprise is the size of it — 7.7 × 10⁹ M☉ against the "
        "observed 1.4–1.7 × 10¹⁰, low by 45%, because the model has no bar to buckle the inner "
        "disc into a box/peanut and BHG16 §4.2 says that is most of what the Milky Way's bulge is."
    ),
)

BULGE_SCALE_RADIUS = FieldDecl(
    name="bulge_scale_radius",
    label="Bulge scale radius a",
    unit="kpc",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "The Hernquist scale of the spheroid, set by equating its own half-mass radius, "
        "a(1 + √2), to the radius inside which half the low-j excess lies. Derived, not chosen: "
        "no constant enters and the identity is algebra a test reproduces. 0.36 kpc at the "
        "default, which puts the spheroid's half-mass radius at 0.88 kpc."
    ),
)

BULGE_VELOCITY_DISPERSION = FieldDecl(
    name="bulge_velocity_dispersion",
    label="Bulge velocity dispersion",
    unit="km/s",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Acceptance row 14, mass-weighted inside the spheroid's half-mass radius to match the "
        "way the source quotes it. The isotropic spherical Jeans equation in the model's own "
        "total potential — dark halo, disc and spheroid — so it is a derivation with one "
        "assumption, isotropy, and that assumption is why the number can be right for a bulge "
        "that in fact rotates: rotational support counted as dispersion. On the spheroid's own "
        "gravity alone it would read a third lower."
    ),
)

BULGE_CLASSICAL_FRACTION = FieldDecl(
    name="bulge_classical_fraction",
    label="Classical share of the bulge",
    unit="dimensionless",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "How much of the spheroid is pressure-supported rather than rotating: one minus the "
        "low-j excess's mean specific angular momentum over that of a circular orbit at its "
        "half-mass radius, which is the V/σ axis pseudobulges are classified on [recall: "
        "Kormendy & Kennedy 2004 via Kormendy & Ho 2013]. Reading a support ratio as a mass "
        "fraction is the model's assumption and the linear one is the least it can make. "
        "0.13 at the default — a prediction, and it lands inside the 0–25% classical share "
        "BHG16 §4.2.4 gives the Milky Way. Ruling 10 interpolates the M–σ residual's width "
        "with it (GALAXY_INPUTS.md §13)."
    ),
)

DISC_SCALE_LENGTH_SPIN = FieldDecl(
    name="disc_scale_length_spin",
    label="Disc scale length from λ_d",
    unit="kpc",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Exponential scale length from MMW98 given λ_d and R₂₀₀. The surprise is how little of "
        "the halo it is: R_d/R₂₀₀ ≈ 1.2%, so the visible galaxy is a speck at the centre of the "
        "thing that holds it. This is MMW98's *prediction* of the scale length from angular "
        "momentum. Acceptance row 4 is read from thin_disc_scale_length, which S2 fits to the "
        "stellar profile the star formation history actually builds — the two disagree by a "
        "third, and that disagreement is debt #13 rather than something to average away. "
        "Computed by the halo stage since S14, which needs it first: it is the disc the halo "
        "contracts around."
    ),
)


def compute(ctx: Context) -> Mapping[str, Any]:
    G = float(ctx.constants["G"])
    H0 = float(ctx.constants["H0"])
    M200 = float(ctx.inputs["halo_mass"])
    z_f = float(ctx.inputs["halo_assembly_z"])
    R_sun = float(ctx.constants["R_SUN"])

    R200 = virial_radius(M200, H0, G)
    c_vir = float(ctx.constants["CONCENTRATION_NORM"]) * (1.0 + z_f)
    c = concentration_at(200.0, c_vir, virial_overdensity(float(ctx.constants["OMEGA_M"])))
    r_s = R200 / c

    m_d = float(ctx.constants["F_BARYON"]) * float(ctx.inputs["baryon_retention"])
    baryons = m_d * M200
    dark = M200 - baryons
    R_d = scale_length(float(ctx.inputs["disc_spin"]), R200)

    # The halo's response to the disc, on its own mesh (debt #6, S14).
    mesh = np.geomspace(MESH_INNER, MESH_OUTER * R200, MESH_POINTS)
    A, w = float(ctx.constants["CONTRACTION_A"]), float(ctx.constants["CONTRACTION_W"])
    M_dark, ratio = contracted_halo(mesh, M200, r_s, c, m_d, R_d, R200, A, w)
    R = ctx.grid.R

    # The high-j tail (S16, debt #18), on the mesh so that no scalar inherits the grid: j(r) on
    # the curve the first pass gives — the contracted halo plus the razor-thin exponential —
    # then the halo contracts again around the total. Two passes, bounded (rule A1). The disc
    # stage's Freeman curve is imported here rather than at the top because that module
    # re-exports this one's scale length.
    from galaxy.stages.disc import PC_PER_KPC, freeman_circular_velocity

    v_disc = freeman_circular_velocity(mesh, baryons / (2.0 * math.pi * R_d * R_d), R_d, G)
    j = mesh * np.hypot(np.sqrt(G * M_dark / mesh), v_disc)
    mu_j = float(ctx.constants["ANGULAR_MOMENTUM_MU"])
    tail_mesh, share, R_c = angular_momentum_tail(mesh, j, baryons, R_d, mu_j)
    tail_cum = np.concatenate([[0.0], np.cumsum(0.5 * (tail_mesh[1:] * mesh[1:] + tail_mesh[:-1] * mesh[:-1]) * np.diff(mesh))])
    tail_cum = tail_cum * 2.0 * math.pi * PC_PER_KPC**2  # M☉ inside r

    # The other end of the same distribution: the mass with too little angular momentum for
    # the exponential, which settles into the central spheroid (S17, debt #11). It leaves the
    # exponential's budget exactly as the tail does, and the halo contracts around all three.
    M_b, r_half_b, _R_core, j_b = angular_momentum_core(mesh, j, baryons, R_d, mu_j)
    a_b = r_half_b / HERNQUIST_HALF_MASS
    share_b = M_b / baryons

    def enclosed(r: np.ndarray) -> np.ndarray:
        return (
            disc_enclosed_mass(r, (1.0 - share - share_b) * baryons, R_d)
            + np.interp(r, mesh, tail_cum)
            + hernquist_enclosed(r, M_b, a_b)
        )

    M_dark, ratio = contracted_halo(mesh, M200, r_s, c, m_d, R_d, R200, A, w, enclosed=enclosed)
    sigma_b, _sigma_whole = spheroid_dispersion(mesh, M_b, a_b, G * (M_dark + enclosed(mesh)))
    # V/σ at the spheroid's own half-mass radius: what rotates is the pseudobulge's (§13).
    v_half = math.sqrt(G * float(_loglog(r_half_b, mesh, M_dark + enclosed(mesh))) / r_half_b)
    classical = 1.0 - j_b / (r_half_b * v_half)
    tail = np.interp(R, mesh, tail_mesh)  # what the grid sees of it; the part beyond R_max is off the grid
    phi_mesh = potential_of(mesh, M_dark, dark, r_s, c, G)
    enclosed = _loglog(R, mesh, M_dark)
    v_c = np.sqrt(G * enclosed / R)

    r = np.hypot(R[:, None], ctx.grid.z[None, :])
    potential = np.interp(np.log(r).ravel(), np.log(mesh), phi_mesh).reshape(r.shape)
    midplane = np.interp(np.log(R), np.log(mesh), phi_mesh)

    return {
        "halo_virial_mass": M200,
        "halo_virial_radius": R200,
        "halo_concentration": c,
        "halo_concentration_virial": c_vir,
        "halo_scale_radius": r_s,
        "halo_dark_mass": dark,
        "baryon_mass_total": baryons,
        "disc_mass_fraction": m_d,
        "disc_scale_length_spin": R_d,
        "infall_tail_surface_density": tail,
        "infall_tail_share": share,
        "infall_tail_inner_radius": R_c,
        "bulge_stellar_mass": M_b,
        "bulge_scale_radius": a_b,
        "bulge_velocity_dispersion": sigma_b,
        "bulge_classical_fraction": classical,
        "halo_circular_velocity_sun": math.sqrt(G * float(_loglog(R_sun, mesh, M_dark)) / R_sun),
        "halo_circular_velocity_sun_initial": float(nfw_circular_velocity(R_sun, dark, r_s, c, G)),
        "halo_density_sun": float(_loglog(R_sun, mesh, density_of(mesh, M_dark))) * 1.0e-9,
        "halo_concentration_contracted": concentration_enclosing(float(_loglog(R_sun, mesh, M_dark)), R_sun, dark, R200),
        "halo_contraction": np.interp(np.log(R), np.log(mesh), ratio),
        "halo_enclosed_mass": enclosed,
        "halo_circular_velocity": v_c,
        "halo_potential": potential,
        "halo_potential_midplane": midplane,
    }


HALO = IMPLEMENTATIONS.register(
    Stage(
        id="halo",
        slot="halo",
        checkpoint=1,
        about=(
            "NFW dark halo from M₂₀₀ and the assembly redshift, the split of M₂₀₀ into retained "
            "baryons and dark matter, the two ends of their angular-momentum distribution the "
            "exponential disc cannot hold — the extended gas disc (S16) and the central spheroid "
            "(S17) — and the halo's contraction around all three (S14). Shared by both models."
        ),
        compute=compute,
        reads_inputs=("halo_mass", "halo_assembly_z", "baryon_retention", "disc_spin"),
        reads_constants=(
            "G", "H0", "F_BARYON", "CONCENTRATION_NORM", "OMEGA_M", "R_SUN",
            "CONTRACTION_A", "CONTRACTION_W", "ANGULAR_MOMENTUM_MU",
        ),
        publishes=(
            HALO_VIRIAL_MASS,
            HALO_VIRIAL_RADIUS,
            HALO_CONCENTRATION,
            HALO_CONCENTRATION_VIRIAL,
            HALO_SCALE_RADIUS,
            HALO_DARK_MASS,
            BARYON_MASS_TOTAL,
            DISC_MASS_FRACTION,
            DISC_SCALE_LENGTH_SPIN,
            INFALL_TAIL_SURFACE_DENSITY,
            INFALL_TAIL_SHARE,
            INFALL_TAIL_INNER_RADIUS,
            BULGE_STELLAR_MASS,
            BULGE_SCALE_RADIUS,
            BULGE_VELOCITY_DISPERSION,
            BULGE_CLASSICAL_FRACTION,
            HALO_CIRCULAR_VELOCITY_SUN,
            HALO_CIRCULAR_VELOCITY_SUN_INITIAL,
            HALO_DENSITY_SUN,
            HALO_CONCENTRATION_CONTRACTED,
            HALO_CONTRACTION,
            HALO_ENCLOSED_MASS,
            HALO_CIRCULAR_VELOCITY,
            HALO_POTENTIAL,
            HALO_POTENTIAL_MIDPLANE,
        ),
    )
)
