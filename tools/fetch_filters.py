"""Fetch named-instrument filter curves from the SVO Filter Profile Service into the viewer's instrument sets.

    uv run python tools/fetch_filters.py --raw <dir>     # download (skips files already there) and write
    uv run python tools/fetch_filters.py --raw <dir> --convert-only

The owner's word of 2026-09-27 (debt #108, D188): the named instrument's curves are a download. Two sets, both
HST WFC3/UVIS (chip 2, as SVO names it): the broadband F814W, F555W, F438W drawn red, green, blue, and the
narrowband "Hubble palette" F673N ([S II]), F656N (Hα), F502N ([O III]). Each curve is SVO's VOTable
(``fps.php?ID=...``): wavelength in Å and the total system throughput STScI publishes (the profile reference
SVO gives), not the filter's transmission alone - the viewer's white point divides each channel by the same
curve's response to a blackbody, so the scale cancels and only the shape draws.

What is written is ``frontend/src/galaxy/instruments.json``: per set, the three curves as the model's
``sampled`` shape, each resampled linearly onto 241 points over the span where it exceeds 10⁻³ of its peak
(the request carries its curves in the query string, and SVO's tables run to 3000 rows); the largest
difference between a resampled curve and SVO's own points, over its peak, is recorded beside it. STScI's
UVIS throughputs are on vacuum wavelengths (WFC3 Instrument Handbook section 6.5, converted by Morton 1991's
formula; read at S43, D195, #120), so each curve is written with ``wavelengths: "vacuum"`` and the model
converts its air lines before reading them; the both-ways transmissions recorded here show what the
convention is worth (Hα in F656N 0.962 at the air placement, 0.945 at the vacuum one; [S II] 6716 in F673N
0.983 against 0.958).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
from galaxy.stages.spectra import LINE_WAVELENGTHS  # noqa: E402

OUT = ROOT / "frontend" / "src" / "galaxy" / "instruments.json"
SERVICE = "https://svo2.cab.inta-csic.es/theory/fps/fps.php?ID="
POINTS = 241
FLOOR = 1.0e-3  # of the peak: the span a curve is kept over
FETCHED = "2026-09-27"
ACKNOWLEDGEMENT = (
    "This research has made use of the SVO Filter Profile Service \"Carlos Rodrigo\", funded by "
    "MCIN/AEI/10.13039/501100011033/ through grant PID2023-146210NB-I00 (Rodrigo et al. 2012, 2020, 2024; "
    "the acknowledgement and references SVO asks for, read on its front page on " + FETCHED + ")."
)
# STScI's curves are on vacuum wavelengths and the model's lines in air (D195, #120): each curve says so.
VACUUM = (", on vacuum wavelengths (WFC3 Instrument Handbook section 6.5; the model converts its air lines by Morton "
          "1991 before reading them, D195)")

SETS = {
    "wfc3": {
        "label": "WFC3",
        "about": ("As Hubble, broadband (RENDER_PHYSICS section 2a): HST WFC3/UVIS F814W, F555W and F438W as red, green "
                  "and blue - the measured system throughputs [verified: SVO Filter Profile Service, HST/WFC3_UVIS2.*, "
                  "fetched " + FETCHED + " by tools/fetch_filters.py]" + VACUUM + ", with the Airy diffraction pattern of a circular "
                  "aperture as the stars' sprite, its size per channel in proportion to the filter's pivot wavelength."),
        "filters": [("F814W", "HST/WFC3_UVIS2.F814W"), ("F555W", "HST/WFC3_UVIS2.F555W"), ("F438W", "HST/WFC3_UVIS2.F438W")],
    },
    "wfc3n": {
        "label": "WFC3 SHO",
        "about": ("As Hubble, the narrowband palette: HST WFC3/UVIS F673N ([S II] 6716/6731), F656N (Halpha) and F502N "
                  "([O III] 5007) as red, green and blue - measured throughputs [verified: SVO Filter Profile Service, "
                  "HST/WFC3_UVIS2.*, fetched " + FETCHED + "]" + VACUUM + ", the same Airy sprite. F656N is 18 A wide: the [N II] lines "
                  "either side of Halpha fall outside it, where the SHO set's 30 A box also leaves them."),
        "filters": [("F673N", "HST/WFC3_UVIS2.F673N"), ("F656N", "HST/WFC3_UVIS2.F656N"), ("F502N", "HST/WFC3_UVIS2.F502N")],
    },
}
PSF = {
    "kind": "airy",
    "about": ("The diffraction pattern of a circular aperture, (2 J1(v)/v)^2: the shape of an unresolved point through a "
              "telescope, drawn per channel at a radius proportional to the channel's pivot wavelength (lambda/D). Its "
              "scale on screen is a display choice [inferred], because the view has no distance to the galaxy; HST's "
              "central obscuration and the four spikes its secondary's supports make are not drawn."),
}


def fetch(raw: Path, svo_id: str) -> Path:
    raw.mkdir(parents=True, exist_ok=True)
    dest = raw / (svo_id.replace("/", "_") + ".xml")
    if not dest.exists():
        with urllib.request.urlopen(SERVICE + svo_id, timeout=120) as r:
            dest.write_bytes(r.read())
    return dest


def read(path: Path) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    text = path.read_text(encoding="utf-8")
    rows = re.findall(r"<TR>\s*<TD>([^<]+)</TD>\s*<TD>([^<]+)</TD>\s*</TR>", text)
    table = np.array(rows, dtype=float)
    params = {name: float(value) for name, value in re.findall(r'<PARAM name="(WavelengthPivot|WavelengthEff|FWHM)" value="([^"]+)"', text)}
    if 'value="Angstrom"' not in text or table.shape[0] < 10:
        raise ValueError(f"{path.name}: not an SVO table in Angstrom")
    order = np.argsort(table[:, 0], kind="stable")
    lam, t = table[order, 0], table[order, 1]
    keep = np.concatenate([[True], np.diff(lam) > 0])
    return lam[keep], t[keep], params


def resample(lam: np.ndarray, t: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    above = np.flatnonzero(t > FLOOR * t.max())
    lo, hi = lam[max(above[0] - 1, 0)], lam[min(above[-1] + 1, lam.size - 1)]
    grid = np.linspace(lo, hi, POINTS)
    out = np.interp(grid, lam, t)
    inside = (lam >= lo) & (lam <= hi)
    error = float(np.max(np.abs(np.interp(lam[inside], grid, out) - t[inside])) / t.max())
    return grid, out, error


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, required=True, help="directory for SVO's VOTables (kept out of the repository)")
    ap.add_argument("--convert-only", action="store_true")
    a = ap.parse_args()
    sets = {}
    for key, spec in SETS.items():
        curves, sources = [], []
        for name, svo_id in spec["filters"]:
            path = a.raw / (svo_id.replace("/", "_") + ".xml") if a.convert_only else fetch(a.raw, svo_id)
            lam, t, params = read(path)
            grid, values, error = resample(lam, t)
            peak = float(values.max())
            curves.append({"name": name, "shape": "sampled", "wavelengths": "vacuum",
                           "wavelength": [round(float(x), 2) for x in grid],
                           "transmission": [round(float(v) / peak, 5) for v in values]})
            # Each line's share at its air wavelength and at its vacuum one (air x 1.000277 near 6000 A, the
            # refractivity of dry air at 15 C [inferred]): what the air-or-vacuum question moves.
            lines = {n: [round(float(np.interp(w * f, grid, values) / peak), 4) for f in (1.0, 1.000277)]
                     for n, w in LINE_WAVELENGTHS.items() if grid[0] < w < grid[-1]}
            sources.append({"filter": name, "svo": svo_id, "pivot": round(params.get("WavelengthPivot", float("nan")), 2),
                            "fwhm": round(params.get("FWHM", float("nan")), 2), "peak_throughput": round(peak, 5),
                            "resample_error": round(error, 5), "lines_air_vacuum": lines})
        sets[key] = {"label": spec["label"], "about": spec["about"], "psf": PSF, "curves": curves, "sources": sources}
    doc = {
        "about": ("Named-instrument filter sets, generated by tools/fetch_filters.py from the SVO Filter Profile Service "
                  "(the owner's word of 2026-09-27, debt #108); do not edit by hand. Each curve is normalised to its peak "
                  "(the white point divides the scale out). " + ACKNOWLEDGEMENT),
        "sets": sets,
    }
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for key, entry in sets.items():
        for s in entry["sources"]:
            print(key, s["filter"], "pivot", s["pivot"], "fwhm", s["fwhm"], "err", s["resample_error"], s["lines_air_vacuum"])
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
