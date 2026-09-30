"""Fetch FSPS's nebular line grid (Byler et al. 2017's method) and convert it into the model's table.

    uv run python tools/fetch_nebular.py --raw <dir>     # download (skips a file already there) and convert
    uv run python tools/fetch_nebular.py --raw <dir> --convert-only

One file, ``nebular/ZAU_ND_prsc.lines`` from the FSPS repository at a pinned commit (the owner's word,
2026-09-27, on D184's question), Byler et al. 2017's method as FSPS ships it at that commit (11 log Z, four
of them shifted from the paper's, a 20 Myr row the paper lacks): Cloudy line luminosities per ionizing photon (L☉ per photon/s, FSPS's
``sps_setup.f90``: "Units are Lsun/Q") for 166 lines on 11 gas metallicities log(Z/Z☉) × 10 ages
(0.5–20 Myr) × 7 ionization parameters log U (−4 to −1), ionized by PARSEC ("prsc") single stellar
populations with no dust inside the region ("ND"). The file is read in FSPS's own order: a header line,
the vacuum wavelengths, then for each (Z, age, U), Z outermost and U innermost, a line of the three
coordinates and a line of the 166 luminosities.

What is committed is ``model/galaxy/data/nebular_lines.npz``: the three axes, and for the six lines the
model names (``spectra.LINE_WAVELENGTHS``) their vacuum wavelengths and log10 of their luminosity per
ionizing photon as float32 on the full grid. FSPS's vacuum wavelengths sit +0.07 to +0.10 Å above NIST's air
values × Morton 1991's refractive index for all six lines [verified: NIST ASD and FSPS ``emlines_info.dat`` at
the pinned commit, compared at S43 (Audit IV A4-11)]. Attribution: the README's Attributions section (MIT).
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "model" / "galaxy" / "data" / "nebular_lines.npz"
COMMIT = "bd187a0d07dac17b55c4dc7c60d83f63694c1b4e"  # cconroy20/fsps master on 2026-08-06, fetched 2026-09-27
FILE = "nebular/ZAU_ND_prsc.lines"
URL = f"https://raw.githubusercontent.com/cconroy20/fsps/{COMMIT}/{FILE}"
SHAPE = (11, 10, 7)  # log Z, age, log U: FSPS's nebnz, nebnage, nebnip (sps_vars.f90)
N_LINES = 166  # nemline

# The model's line names and the grid's vacuum wavelengths for them (FSPS data/emlines_info.dat at the same
# commit: "4862.7629,Ba-beta 4861", "5008.3137,[O III] 5007", "6564.7229,Ba-alpha 6563",
# "6585.3687,[N II] 6584", "6718.3965,[S II] 6716", "6732.7805,[S II] 6731").
LINES = {
    "hbeta": 4862.7629, "oiii_5007": 5008.3137, "halpha": 6564.7229,
    "nii_6583": 6585.3687, "sii_6716": 6718.3965, "sii_6731": 6732.7805,
}


def fetch(raw: Path) -> Path:
    raw.mkdir(parents=True, exist_ok=True)
    dest = raw / Path(FILE).name
    if not dest.exists():
        with urllib.request.urlopen(URL, timeout=120) as r:
            dest.write_bytes(r.read())
    return dest


def convert(src: Path) -> dict[str, np.ndarray]:
    rows = src.read_text(encoding="ascii").split("\n")
    header = rows[0].split()
    if header[:1] != [f"#{N_LINES}"] or "770" not in header:
        raise ValueError(f"unexpected header {rows[0]!r}")
    wavelength = np.array(rows[1].split(), dtype=float)
    if wavelength.size != N_LINES:
        raise ValueError(f"{wavelength.size} wavelengths, not {N_LINES}")
    n = int(np.prod(SHAPE))
    coords = np.array([rows[2 + 2 * i].split() for i in range(n)], dtype=float)
    values = np.array([rows[3 + 2 * i].split() for i in range(n)], dtype=float)
    if values.shape != (n, N_LINES):
        raise ValueError(f"luminosity block is {values.shape}")
    grid = coords.reshape(*SHAPE, 3)
    log_z, age, log_u = grid[:, 0, 0, 0], grid[0, :, 0, 1], grid[0, 0, :, 2]
    # The coordinates must be a product grid in FSPS's order, or the reshape above is wrong.
    if not (np.all(grid[..., 0] == log_z[:, None, None]) and np.all(grid[..., 1] == age[None, :, None])
            and np.all(grid[..., 2] == log_u[None, None, :])):
        raise ValueError("the coordinates are not a product grid in (Z, age, U) order")
    columns = []
    for name, w in LINES.items():
        k = int(np.argmin(np.abs(wavelength - w)))
        if abs(wavelength[k] - w) > 0.01:
            raise ValueError(f"{name}: nearest grid line {wavelength[k]} is not {w}")
        columns.append(k)
    lum = values.reshape(*SHAPE, N_LINES)[..., columns]
    if not np.all(lum > 0.0):
        raise ValueError("a named line is zero somewhere on the grid")
    return {
        "log_z": log_z, "log_age_yr": np.log10(age), "log_u": log_u,
        "lines": np.array(list(LINES)), "wavelength_vacuum": np.array(list(LINES.values())),
        "log_lsun_per_photon": np.log10(lum).astype(np.float32),
        "source": np.array(f"cconroy20/fsps@{COMMIT}:{FILE}"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, required=True, help="directory for the downloaded file (kept out of the repository)")
    ap.add_argument("--convert-only", action="store_true")
    a = ap.parse_args()
    src = a.raw / Path(FILE).name if a.convert_only else fetch(a.raw)
    table = convert(src)
    np.savez_compressed(OUT, **table)
    print(f"wrote {OUT.relative_to(ROOT)}: {table['log_lsun_per_photon'].shape} from {table['source']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
