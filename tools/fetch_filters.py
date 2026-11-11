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

S83 (T11; the owner accepted the download on 2026-11-02): a third set, ``jwst_nircam`` - JWST NIRCam's broadband
F444W, F200W and F090W drawn red, green, blue, SVO's ``JWST/NIRCam.*`` profiles (the total system throughput: the
telescope, NIRCam's optics, the dichroics and the detectors' QE, as their ``Comments`` say). No template names JWST's
telescope, so the set carries its own optics (``optics``): the segmented primary as a pupil the viewer's PSF job images
(frontend/src/galaxy/hstPsf.ts pupilOpen, aperture "hexagonal-18"), every number either read (cited) or derived here
from read ones, the derivations written beside them.
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
JWST_FETCHED = "2026-11-02"  # S83, T11: NIRCam's three profiles
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
    "jwst_nircam": {
        "label": "NIRCam",
        "about": ("As JWST, broadband (T11, S83): JWST NIRCam F444W, F200W and F090W as red, green and blue - the total "
                  "system throughputs, the telescope, NIRCam's optics, the dichroics and the detectors' QE [verified: SVO "
                  "Filter Profile Service, JWST/NIRCam.*, fetched " + JWST_FETCHED + " by tools/fetch_filters.py], on vacuum "
                  "wavelengths [inferred: neither SVO's profiles nor JDox's NIRCam filters page says which; a broadband "
                  "filter moves by 0.03 % between the two, 12 A at F444W's 4.4 um], with JWST's segmented primary as the "
                  "stars' image where the template has a distance (the set's optics) and the Airy sprite where it has none."),
        "filters": [("F444W", "JWST/NIRCam.F444W"), ("F200W", "JWST/NIRCam.F200W"), ("F090W", "JWST/NIRCam.F090W")],
    },
}
PSF = {
    "kind": "airy",
    # S67 (D227 R7): was "... Its scale on screen is a display choice [inferred], because the view has no distance to
    # the galaxy; HST's central obscuration and the four spikes its secondary's supports make are not drawn." - a
    # template with this instrument and a distance draws the physical PSF since (frontend/src/galaxy/hstPsf.ts). The
    # JSON's copy was set to this string by hand, without a fetch; the next run of this tool writes the same. The fix
    # pass (F4) added the zoom's clamp to it, the JSON's copy again by hand (hstPsf.ts psfHalf states the numbers);
    # S82 (#178) the wings' pass in place of the clamp's returned light, both copies by hand again.
    "about": ("The diffraction pattern of a circular aperture, (2 J1(v)/v)^2: the shape of an unresolved point through a "
              "telescope, drawn per channel at a radius proportional to the channel's pivot wavelength (lambda/D). Where "
              "a template carries this instrument with a distance (NGC 4414: WFC3/UVIS at 17.7 Mpc), a point is drawn at "
              "its physical size instead: HST's obscured Airy pattern (2.4 m, linear obscuration 0.33) at each channel's "
              "pivot, its angle turned into pc by the distance and convolved with the 0.04 arcsec pixel as a box, each "
              "screen pixel taking its share of the point's light; a switch draws the full pupil's image instead, its four "
              "spikes and the mirror's pads, the same light. Close in, the box is clamped and the light past it drawn "
              "by a second, coarser pass: at 0.488 pc a screen pixel (NGC 4414's zoom stand) the table's half-width is "
              "314 px and the box 60; the light past the box (0.042 of the red Airy, 0.060 of the red spikes) is drawn "
              "where it falls in blocks of 8 pixels, each block's light spread evenly over it, so none is returned to "
              "the box (S82). Without a distance its scale on screen is a display choice [inferred] (S67, D227)."),
}

# --- JWST's optics (S83, T11): what is read, and what is derived from it ---------------------------------------------
_JDOX_OTE = "JDox, JWST Telescope (jwst-docs.stsci.edu, read 2026-11-02)"
_JDOX_PSF = "JDox, NIRCam Point Spread Functions (jwst-docs.stsci.edu, read 2026-11-02)"
_OTE_PAPER = ("McElwain et al. 2023, PASP, DOI 10.1088/1538-3873/acada0, arXiv:2301.01779, the OTE's design and "
              "performance, read 2026-11-02")
# The paper's first author is McElwain, Feinberg the second (cited as Feinberg et al. until S95; re-read at Audit VI,
# F-1B-1). Each segment across its flats and the gap between neighbours [verified: McElwain et al. 2023: "Each of the 18
# primary mirror segments are 1.32 m (flat-to-flat) separated by 7 mm gaps"]. The brief's "6.5 m flat to flat" is JDox's
# "~6.5 m" diameter; the paper states a circumscribed 6.64 m and a flat-to-flat 6.575 m, which the two numbers here give
# to 0.5 % (circumscribed, 6.6717 m) and 0.8 % (flat-to-flat, 6.628 m) (re-read at Audit VI, F-1B-2).
SEGMENT_M, GAP_M = 1.32, 0.007
SEGMENTS = 18  # [verified: JDox JWST Telescope, "18 hexagonal segments"]
SECONDARY_M = 0.74  # the secondary's diameter [verified: JDox JWST Telescope, "a convex circular mirror 0.74 m in diameter"]
POLISHED_M2, UNOBSCURED_M2 = 26.3, 25.4  # [verified: JDox JWST Telescope: polished 26.3 m2, the struts leave 25.4 unobscured]
# The struts' directions, degrees anticlockwise from the frame's +x with +V3 up [inferred]: the upper strut along +V3 makes
# the horizontal pair of JWST's eight spikes; the lower two, 30 degrees either side of -V3, are perpendicular to the
# segments' diagonal edges' spikes and so add to them rather than making more - eight spikes in all, as JWST's images
# show. Not read from a drawing of the tripod; the spikes' relative brightness is not matched to the images (S83 measured
# the horizontal pair at twice the vertical's light with the derived width, where JWST's images show it fainter).
STRUT_ANGLES_DEG = [90.0, 240.0, 300.0]
# The detectors' pixels, red green blue [verified: JDox NIRCam PSFs: 0.031" short-wavelength (F090W, F200W), 0.063"
# long-wavelength (F444W)].
NIRCAM_PIXELS = [0.063, 0.031, 0.031]
# The 18 segments' centres in pitches, a segment and a gap (hstPsf.ts SEGMENT_CENTRES, the same): flat-topped hexagons
# tiling the plane about a missing centre - six at 1 and six at 2 along the edges' normals, six at sqrt 3 along the
# corners. Flat-topped, the outermost columns three segments each, as the two wings that fold are [inferred: JDox, "two
# wings, each supporting three mirror segments"].
SEGMENT_CENTRES = ([(np.cos(np.radians(30 + 60 * k)), np.sin(np.radians(30 + 60 * k))) for k in range(6)]
                   + [(2 * np.cos(np.radians(30 + 60 * k)), 2 * np.sin(np.radians(30 + 60 * k))) for k in range(6)]
                   + [(np.sqrt(3) * np.cos(np.radians(60 * k)), np.sqrt(3) * np.sin(np.radians(60 * k))) for k in range(6)])
STRUT_GRID = 4001  # samples a side over the pupil's square for the struts' width: 5e-4 pupil radii, 1/70 of a strut


def on_segments(x: np.ndarray, y: np.ndarray, s: float, gap: float) -> np.ndarray:
    """hstPsf.ts onSegment over arrays: on one of the 18 flat-topped hexagons of flat-to-flat width s, gap apart."""
    out = np.zeros(x.shape, dtype=bool)
    for cx, cy in SEGMENT_CENTRES:
        dx, dy = np.abs(x - cx * (s + gap)), np.abs(y - cy * (s + gap))
        out |= (dy <= s / 2) & (0.5 * dy + (np.sqrt(3) / 2) * dx <= s / 2)
    return out


def on_struts(x: np.ndarray, y: np.ndarray, width: float) -> np.ndarray:
    """hstPsf.ts pupilOpen's vanes over arrays: a strut of full width `width` from the centre along each direction."""
    out = np.zeros(x.shape, dtype=bool)
    for deg in STRUT_ANGLES_DEG:
        a = np.radians(deg)
        along, across = x * np.cos(a) + y * np.sin(a), -x * np.sin(a) + y * np.cos(a)
        out |= (along > 0) & (np.abs(across) < width / 2)
    return out


def jwst_optics() -> dict:
    """JWST's primary as the viewer's pupil (hexagonal-18), every number read or derived here (its `derived` entry)."""
    f, p = SEGMENT_M, SEGMENT_M + GAP_M  # a segment across its flats, and the pitch between neighbours' centres
    # The farthest corner: an outer segment's along a normal, at (sqrt3 p, p), its corner (f/(2 sqrt3), f/2) further out.
    circum = float(np.hypot(np.sqrt(3) * p + f / (2 * np.sqrt(3)), p + f / 2))
    across = 4 * p + f  # across the flats, through the column of four above and below the centre
    segment, gap = f / circum, GAP_M / circum  # in pupil radii (the circumscribed radius the unit)
    area = SEGMENTS * np.sqrt(3) / 2 * f * f  # against the polished 26.3: the segments' edges past the polish not read
    grid = np.linspace(-1, 1, STRUT_GRID)
    x, y = np.meshgrid(grid, grid)
    seg = on_segments(x, y, segment, gap)
    want = 1 - UNOBSCURED_M2 / POLISHED_M2  # the share of the segments the struts cover
    lo, hi = 0.0, 0.2
    for _ in range(40):  # the covered share rises with the width: bisection
        mid = 0.5 * (lo + hi)
        share = np.count_nonzero(seg & on_struts(x, y, mid)) / np.count_nonzero(seg)
        lo, hi = (mid, hi) if share < want else (lo, mid)
    width = 0.5 * (lo + hi)
    return {
        "about": ("JWST's primary as the pupil the PSF job images (frontend/src/galaxy/hstPsf.ts pupilOpen): 18 flat-topped "
                  "hexagonal segments in two rings about a missing centre [verified: " + _JDOX_OTE + ", 18 hexagonal "
                  "segments], each 1.32 m across its flats and 7 mm from its neighbours [verified: " + _OTE_PAPER + "], so "
                  f"{across:.3f} m across the flats and a circumscribed diameter of {2 * circum:.4f} m, twice the pupil's "
                  "unit radius [derived; the paper states 6.575 m and 6.64 m, met to 0.8 % and 0.5 %, JDox ~6.5 m]; the "
                  "segments' area "
                  f"{area:.2f} m2 against JDox's polished 26.3. The gaps, {gap:.5f} pupil radii, are drawn (sampled at a "
                  "sixteenth of a pupil pixel). The "
                  f"secondary's 0.74 m shadow [verified: JDox] is obscuration {SECONDARY_M / (2 * circum):.4f} of the unit "
                  "radius and lies inside the missing centre. Three struts from the centre, at 90, 240 and 300 degrees "
                  "anticlockwise from the frame's +x with +V3 up [inferred from the eight spikes of JWST's images: the upper "
                  "strut makes the horizontal pair, the lower two lie on the segments' diagonal spikes; not read from a "
                  "drawing of the tripod], each " +
                  f"{width:.5f} pupil radii ({width * circum * 100:.1f} cm) wide [derived: the width at which they cover "
                  f"1 - 25.4/26.3 = {want:.5f} of the segments, JDox's unobscured over polished area, on a {STRUT_GRID}^2 "
                  "grid, all of the difference taken as the struts' as JDox says]. The detectors' pixels 0.063\" in red (F444W, long wavelength) and 0.031\" in green and blue "
                  "(F200W, F090W, short wavelength) [verified: " + _JDOX_PSF + "], each channel's table convolved with its own."),
        "aperture": "hexagonal-18",
        "aperture_m": round(float(2 * circum), 4),
        "segment": round(segment, 6),
        "gap": round(gap, 7),
        "obscuration": round(float(SECONDARY_M / (2 * circum)), 5),
        "spider_width": round(width, 6),
        "spider_angles_deg": STRUT_ANGLES_DEG,
        "pixel_scale_arcsec": NIRCAM_PIXELS,
    }


JWST_PSF = {
    "kind": "airy",
    "about": ("Without a distance the Airy pattern of a circular aperture, per channel at a radius proportional to its "
              "pivot (lambda/D) - a display choice [inferred], as WFC3's sprite. Where the template has a distance (NGC "
              "4414: 17.7 Mpc), a point is the image of JWST's primary (the set's optics) at its physical size, each "
              "channel's at its pivot, its angle turned into pc by the distance and convolved with the channel's own "
              "detector pixel: with the spikes' switch off the 18 segments alone, whose outline makes six spikes; on, the "
              "three struts too - a horizontal pair from the upper strut, the lower two's on the segments' diagonal "
              "four. The table and the wings' pass are WFC3's (S82)."),
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
        if key == "jwst_nircam":  # S83, T11: the set carries its own optics, since no template names its telescope
            sets[key] = {"label": spec["label"], "about": spec["about"], "psf": JWST_PSF, "optics": jwst_optics(),
                         "curves": curves, "sources": sources}
        else:
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
