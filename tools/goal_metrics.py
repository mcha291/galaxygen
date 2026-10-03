"""Six statistics of a picture of a disc galaxy: a goal image or a capture of the viewer (BUILD_III Phase 0, rule B1).

    uv run python tools/goal_metrics.py IMAGE                       # geometry estimated, a summary printed
    uv run python tools/goal_metrics.py IMAGE --json out.json       # everything, with each metric's definition
    uv run python tools/goal_metrics.py --table-header              # the Markdown header of the headline table
    uv run python tools/goal_metrics.py IMAGE --table               # one Markdown row of it, for this image
    uv run python tools/goal_metrics.py IMAGE --centre X Y --axis-ratio Q --position-angle DEG --radius PX
    uv run python tools/goal_metrics.py IMAGE --encoded             # keep the display-encoded values
    uv run python tools/goal_metrics.py IMAGE --sky 0 0 0           # subtract this, not the border's median

**What this is, and is not.** The numbers are statistics of a picture: of the pixel values a display would show.
They are not photometry, and no number here is an acceptance row (C6, D113; BUILD_III section 0: "display targets,
not rows"). They exist so that a goal picture and a capture of the viewer can be put in one table and the same
question asked of both. Needs numpy, and Pillow only to read the file; nothing under ``model/galaxy/`` imports
either this module or Pillow (``tests/test_goal_metrics.py`` scans for it).

**A pixel value.** The input is an 8-bit display-encoded picture. By default each channel is divided by 255 and
the sRGB transfer curve is undone (IEC 61966-2-1, the piecewise curve `[recall]`), so a value is *linear display
light* on 0..1, not a flux. ``--encoded`` keeps value/255 as stored. The output says which was used. "Luminance"
is 0.2126 R + 0.7152 G + 0.0722 B of those values (the Rec. 709 weights `[recall]`; on encoded values it is the
same weighted sum, a luma). The picture's transfer curve, white balance and stretch are the picture-maker's and
are not undone; a picture that was not encoded as sRGB is decoded as if it were.

**Coordinates.** x runs right and y runs down, in pixels, pixel centres at integers, the top-left pixel at (0, 0).
The position angle is the direction of the outline's long axis, in degrees from +x towards +y (clockwise on the
screen), in [0, 180). It is not the astronomical convention: a picture carries no north. Azimuth phi is measured
in the deprojected plane from the long axis, in the same sense.

**Geometry: the picture's outline, not a galaxy's inclination.** Four numbers place the ellipse every metric uses:
the centre, the axis ratio q (short over long), the position angle, and the outer semi-major radius ``a`` in
pixels. Each may be given; each one omitted is estimated, and the estimate is always reported beside what was
used. The estimate, on the picture area-averaged until its longer side is at most 512 px:
  - the sky is the per-channel median of a border frame 2 % of the shorter side wide, and its noise 1.4826 times
    the border luminance's median absolute deviation;
  - the luminance less the sky is smoothed by a Gaussian of sigma 1 % of the longer side;
  - the outline is the set of brightest smoothed pixels that together hold 90 % of the smoothed light (the
    threshold over the sky is therefore a stated share of the light, and its level is reported);
  - the centre is the light-weighted centroid of those pixels; q, the angle and ``a`` are the unweighted second
    moments of the set: the long eigenvector, sqrt(l2/l1), and a = 2 sqrt(l1), which is exact for a filled ellipse.
For an exponential disc of scale length h that fills no more than the frame this gives a = 3.89 h. A cropped or
lopsided picture, a bar brighter than its disc, or a border that is not sky all move it; q is the flattening of
an isophote and says nothing sure about tilt. A face-on picture returns a q a little under 1 at an arbitrary
angle: give ``--axis-ratio 1`` when the picture is known to be face-on.

**The standard scale.** So that pictures of different pixel sizes compare, every metric is taken at one scale.
The sky is subtracted, and the picture is area-averaged (exact box averaging of the values in use, by the real
factor a/256) until ``a`` is 256 px. A picture whose ``a`` is already under 256 px is never enlarged: it is used
as it is, the output says ``below_standard``, and the three image-plane metrics (4-6) are then not comparable
with a standard one. The polar metrics (1-3) read that picture on a fixed deprojected grid by bilinear sampling:
320 radii at r/a = (i + 0.5)/320 and 1024 azimuths, the short axis stretched by 1/q after rotating by the
position angle. The grid is gathered into 40 rings of width a/40, each fine radius weighted by r (by area), so
every band named below ends on a ring's edge. A ring that leaves the frame anywhere has no Fourier amplitudes
and no contrast (None, never zero: B9); a ring under half inside the frame has no colour.

**The six metrics.** The constants are module-level names; the JSON repeats every definition with its numbers.
  1. *Radial colour profile.* Per ring, the mean R, G, B and the colours B-R = -2.5 log10(B/R) and
     G-R = -2.5 log10(G/R) of those means, in magnitudes (negative is bluer than equal channels). Headline: the
     colour of the area-weighted means over 0.15 <= r/a < 0.35 (inner) and over 0.65 <= r/a < 0.85 (outer), and
     outer minus inner.
  2. *Azimuthal Fourier amplitudes.* Per ring, on the luminance, A_m = |sum_j I(phi_j) exp(-i m phi_j)| /
     sum_j I(phi_j) for m = 1..8, and the phase: the azimuth of that component's crest, in [0, 360/m) degrees.
     A pattern 1 + A cos(m (phi - phi0)) returns A_m = A/2 and the phase phi0. Headline: each A_m averaged over
     the complete rings centred in 0.2 <= r/a < 0.8, and the m of the largest (also the largest among m >= 2:
     m = 1 is as often a centring error as a lopsided disc).
  3. *Arm-interarm contrast in the blue channel.* Per ring, the blue channel's azimuthal profile is cut to its
     Fourier terms m <= 8 (so knots and stars do not set it) and the contrast is its 90th percentile over its
     10th. A pattern 1 + A cos(m phi), m <= 8, returns (1 + A cos 18 deg) / (1 - A cos 18 deg). Headline: the
     median over the complete rings centred in 0.2 <= r/a < 0.8.
  4. *Dark-lane covering fraction.* The local level at a pixel is the median of the luminance on a 9 x 9 lattice
     of pixels 3a/256 apart centred on it (3 px apart at the standard scale, reaching 12 px = 0.047 a each way;
     the frame reflected at its edge). Of the pixels with 0.15 <= r/a < 1 in elliptical radius, the fraction
     whose luminance is below (1 - t) times that median, t = 0.25. A median, not a mean: a bar or a bright knot
     does not make its neighbours read as dark, and a black gap between arms is not a lane. A lane that fills
     more than half the lattice is the median and is not seen; a pattern periodic at the lattice's spacing
     would alias, and no picture has one.
  5. *Power-spectrum slope of the unsharp-masked picture.* The background is the luminance smoothed by a Gaussian
     of sigma 0.05 a (normalised at the frame's edge), U = (luminance - background) / background on the same
     annulus, less its weighted mean and times a raised-cosine window (rising over 0.15-0.25 r/a, falling over
     0.90-1.00); the 2-D power of that in a square of side 2a + 2 px, averaged in 10 logarithmic bins of
     wavenumber between 10 and 50 cycles per ``a`` (wavelengths 0.1 a down to 0.02 a); the least-squares slope
     of log10 P against log10 k over those bins. White noise is 0; redder is more negative. The weighted rms
     of U is reported beside it (the slope alone does not say how strong).
  6. *Point sources above a threshold.* The small-scale residual is the luminance smoothed at 1 px less the same
     at 2 px (at the standard scale: a/256 and a/128), divided by metric 5's background plus 0.10 of that
     background's median over the annulus. A source is a strict local maximum of the residual (8 neighbours)
     which exceeds a floor of 0.05, stands 5 robust sigmas above its surroundings (above the median, by 5 x
     1.4826 MAD, of the residual on a 15 x 15 lattice of pixels 3 px apart centred on it, reaching 21 px), and
     is compact: every pixel two away (the 16 on the rim of the 5 x 5 square) is under half the peak. Counted
     inside the ellipse (r/a < 1) and outside it separately. The sigma is local because a picture's grain is
     not one number: in a textured arm it is the texture, so the count is of sources that stand out of the
     picture's own grain there; the count by the floor alone is reported beside it. Two sources within about
     3 px fail the compactness test unless one is much the fainter: a crowded field is under-counted.

**What the metrics do not survive.** The deprojection treats the picture as a thin disc: a bulge or a thick disc
seen inclined returns a false m = 2, and so does a wrong axis ratio. The outline follows the picture's light:
foreground stars holding 3 % of it move ``a`` out by 8 %. Area averaging to the standard scale is a box filter,
not an ideal one: on power-law fields it leaves the slope where it was at a factor of 2 and steepens it by
0.03-0.04 at factors of 1.56 and 2.5, and a source smaller than a standard pixel is diluted by the area it is
averaged over. An 8-bit picture's rounding moves an A_m by up to 0.003 in a faint outer disc. The numbers
compare between pictures only under one ``a`` convention: if ``--radius`` is given for one picture and
estimated for another, say so beside the table. Each number in this paragraph is `[verified:
tests/test_goal_metrics.py]`, where it is measured on a synthetic picture.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import numpy as np

VERSION = 1

LUMA = (0.2126, 0.7152, 0.0722)        # Rec. 709 weights of R, G, B

# The outline estimate.
GEOM_WORK = 512                        # px: the longer side of the picture the outline is estimated on
GEOM_BORDER = 0.02                     # the border frame's width, as a share of the shorter side
GEOM_SMOOTH = 0.01                     # the smoothing sigma, as a share of the longer side
GEOM_LIGHT = 0.90                      # the outline holds this share of the smoothed light

# The standard scale and the polar grid.
STANDARD_A = 256                       # px: the outer semi-major radius every metric is taken at
POLAR_N_R = 320                        # fine radii, r/a = (i + 0.5) / 320
POLAR_N_PHI = 1024                     # azimuths
N_RINGS = 40                           # rings of width a/40: 8 fine radii each
M_MAX = 8

COLOUR_INNER = (0.15, 0.35)            # r/a, the inner colour's band
COLOUR_OUTER = (0.65, 0.85)            # r/a, the outer colour's band
PATTERN_RANGE = (0.2, 0.8)             # r/a, the rings the Fourier and contrast headlines average over
CONTRAST_PERCENTILES = (10.0, 90.0)

DISC_INNER = 0.15                      # r/a: the annulus of metrics 4 and 5 starts here
DARK_LATTICE = 9                       # the local median is over a 9 x 9 lattice of pixels ...
DARK_SPACING = 3.0 / 256               # ... x a apart (3 px at the standard scale): it reaches 12a/256 each way
DARK_T = 0.25                          # a pixel is dark below (1 - t) x that median
BACKGROUND_SIGMA = 0.05                # x a: the Gaussian background of metrics 5 and 6
TAPER = 0.10                           # r/a: the width of each raised-cosine edge of the window
SLOPE_KAPPA = (10.0, 50.0)             # cycles per a: the fit's range (wavelengths 0.1 a to 0.02 a)
SLOPE_BINS = 10

POINT_SIGMAS = (1.0, 2.0)              # px at the working scale: the two Gaussians of the residual
POINT_K = 5.0                          # robust sigmas
POINT_LATTICE = 15                     # the local sigma is over a 15 x 15 lattice of pixels ...
POINT_SPACING = 3                      # ... px apart at the working scale: it reaches 21 px each way
POINT_FLOOR = 0.05                     # the least relative residual that counts
POINT_SOFT = 0.10                      # x the background's median: added under the residual
POINT_COMPACT = 0.5                    # the rim two pixels out is under this share of the peak


@dataclass(frozen=True, slots=True)
class Geometry:
    """The ellipse every metric uses, in the picture's own pixels (see the module docstring for the conventions)."""

    cx: float
    cy: float
    q: float               # short axis over long axis, 0 < q <= 1
    pa_deg: float          # the long axis, degrees from +x towards +y, [0, 180)
    a: float               # the outer semi-major radius, px

    def scaled(self, factor: float) -> "Geometry":
        """The same ellipse on the picture area-averaged by ``factor`` (pixel edges, not centres, scale)."""
        return Geometry((self.cx + 0.5) / factor - 0.5, (self.cy + 0.5) / factor - 0.5, self.q, self.pa_deg, self.a / factor)


# --------------------------------------------------------------------------------------------------------------
# Pixel values
# --------------------------------------------------------------------------------------------------------------

def srgb_decode(v):
    """Display-encoded sRGB on 0..1 to linear light on 0..1 (IEC 61966-2-1)."""
    v = np.asarray(v, dtype=np.float64)
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def srgb_encode(v):
    """Linear light on 0..1 to display-encoded sRGB on 0..1; the inverse of ``srgb_decode``."""
    v = np.clip(np.asarray(v, dtype=np.float64), 0.0, 1.0)
    return np.where(v <= 0.0031308, v * 12.92, 1.055 * v ** (1 / 2.4) - 0.055)


def load_image(path, encoded: bool = False) -> np.ndarray:
    """Read an 8-bit picture as H x W x 3 float32: linear light by default, value/255 with ``encoded``.

    Transparency is composited on black. This is the only place Pillow is used.
    """
    from PIL import Image

    with Image.open(path) as im:
        if im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info:
            rgba = im.convert("RGBA")
            im = Image.alpha_composite(Image.new("RGBA", rgba.size, (0, 0, 0, 255)), rgba)
        u8 = np.asarray(im.convert("RGB"))
    lut = np.arange(256, dtype=np.float64) / 255.0
    if not encoded:
        lut = srgb_decode(lut)
    return lut.astype(np.float32)[u8]


def luminance(image: np.ndarray) -> np.ndarray:
    return image[..., 0] * LUMA[0] + image[..., 1] * LUMA[1] + image[..., 2] * LUMA[2]


# --------------------------------------------------------------------------------------------------------------
# Resampling, smoothing, sampling
# --------------------------------------------------------------------------------------------------------------

def _box_axis(arr: np.ndarray, factor: float, axis: int) -> np.ndarray:
    """Exact box averaging along one axis by a real factor >= 1: each output pixel is its overlaps' weighted sum."""
    arr = np.moveaxis(arr, axis, 0)
    n_in = arr.shape[0]
    n_out = int(math.floor(n_in / factor + 1e-9))
    out = np.empty((n_out,) + arr.shape[1:], dtype=np.float64)
    for k in range(n_out):
        lo, hi = k * factor, min((k + 1) * factor, float(n_in))
        first, last = int(math.floor(lo + 1e-12)), int(math.ceil(hi - 1e-12))
        weights = np.ones(last - first)
        weights[0] -= lo - first                   # the part of the first pixel before the box
        weights[-1] -= last - hi                   # the part of the last pixel after it
        out[k] = np.tensordot(weights, arr[first:last], axes=1) / factor
    return np.moveaxis(out, 0, axis)


def resample_area(image: np.ndarray, factor: float) -> np.ndarray:
    """Area-average ``image`` (H x W or H x W x C) down by a real ``factor``; never up (factor <= 1 returns it).

    Output pixel k is the mean of the input over [k f, (k + 1) f) measured from the top-left edge, a part-covered
    input pixel counting by its covered length; so a position x in the input is (x + 0.5) / f - 0.5 in the
    output. Rows and columns that do not fill a last output pixel are dropped.
    """
    if factor <= 1.0 + 1e-12:
        return np.asarray(image, dtype=np.float64)
    return _box_axis(_box_axis(image, factor, 0), factor, 1)


def gaussian_smooth(arr: np.ndarray, sigma: float) -> np.ndarray:
    """A Gaussian of ``sigma`` px on a 2-D array, normalised at the frame's edge (the frame's outside has no weight)."""
    arr = np.asarray(arr, dtype=np.float64)
    if sigma <= 0:
        return arr.copy()
    h, w = arr.shape
    pad = int(math.ceil(4 * sigma)) + 1
    scale = -2.0 * math.pi**2 * sigma**2
    padded = np.zeros((h + pad, w + pad))
    padded[:h, :w] = arr
    transfer = np.exp(scale * (np.fft.fftfreq(h + pad)[:, None] ** 2 + np.fft.rfftfreq(w + pad)[None, :] ** 2))
    smooth = np.fft.irfft2(np.fft.rfft2(padded) * transfer, s=padded.shape)[:h, :w]

    def weight(n):                                 # the same Gaussian on a row of ones: the kernel is separable
        ones = np.zeros(n + pad)
        ones[:n] = 1.0
        return np.fft.irfft(np.fft.rfft(ones) * np.exp(scale * np.fft.rfftfreq(n + pad) ** 2), n=n + pad)[:n]

    return smooth / (weight(h)[:, None] * weight(w)[None, :])


def lattice_values(arr: np.ndarray, rows: np.ndarray, cols: np.ndarray, lattice: int, spacing: int) -> np.ndarray:
    """A 2-D array's values on a ``lattice`` x ``lattice`` grid of pixels ``spacing`` apart, centred on each (row, col).

    One row of lattice^2 values per position; the frame is reflected at its edge. A median over these is the
    running median of a window 2 (lattice // 2) spacing + 1 px wide, taken on every ``spacing``-th pixel of it:
    the whole window at every pixel would cost spacing^2 more and say the same of anything not periodic.
    """
    arr = np.asarray(arr, dtype=np.float32)
    spacing = max(1, int(spacing))
    reach = min((lattice // 2) * spacing, (min(arr.shape) - 1) // spacing * spacing)
    padded = np.pad(arr, reach, mode="reflect")
    windows = np.lib.stride_tricks.sliding_window_view(padded, (2 * reach + 1, 2 * reach + 1))[:, :, ::spacing, ::spacing]
    return windows[rows, cols].reshape(len(rows), windows.shape[2] * windows.shape[3])


def bilinear(image: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """``image`` (H x W x C) at real positions; NaN outside the pixel centres' rectangle."""
    h, w = image.shape[:2]
    inside = (x >= 0) & (x <= w - 1) & (y >= 0) & (y <= h - 1)
    x0 = np.clip(np.floor(x), 0, w - 2).astype(int)
    y0 = np.clip(np.floor(y), 0, h - 2).astype(int)
    fx = np.clip(x - x0, 0.0, 1.0)[..., None]
    fy = np.clip(y - y0, 0.0, 1.0)[..., None]
    out = (
        image[y0, x0] * (1 - fx) * (1 - fy)
        + image[y0, x0 + 1] * fx * (1 - fy)
        + image[y0 + 1, x0] * (1 - fx) * fy
        + image[y0 + 1, x0 + 1] * fx * fy
    )
    return np.where(inside[..., None], out, np.nan)


def elliptical_radius(shape: tuple[int, int], geometry: Geometry) -> tuple[np.ndarray, np.ndarray]:
    """Each pixel's deprojected r/a and azimuth (radians from the long axis) for ``geometry``."""
    yy, xx = np.mgrid[0 : shape[0], 0 : shape[1]].astype(np.float64)
    dx, dy = xx - geometry.cx, yy - geometry.cy
    c, s = math.cos(math.radians(geometry.pa_deg)), math.sin(math.radians(geometry.pa_deg))
    along = dx * c + dy * s
    across = (-dx * s + dy * c) / geometry.q
    return np.hypot(along, across) / geometry.a, np.arctan2(across, along)


# --------------------------------------------------------------------------------------------------------------
# The outline
# --------------------------------------------------------------------------------------------------------------

def estimate_outline(image: np.ndarray) -> dict:
    """The picture's outline as an ellipse, and the border's sky (the module docstring states the definition).

    Returns ``{"geometry": Geometry, "sky": [r, g, b], "sky_noise": float, "threshold": float, ...}`` in the
    picture's own pixels and values.
    """
    h0, w0 = image.shape[:2]
    factor = max(1.0, max(h0, w0) / GEOM_WORK)
    small = resample_area(image, factor)
    h, w = small.shape[:2]
    b = max(2, int(round(GEOM_BORDER * min(h, w))))
    border = np.ones((h, w), dtype=bool)
    border[b : h - b, b : w - b] = False
    sky = np.median(small[border], axis=0)
    lum = luminance(small)
    sky_lum = float(np.median(lum[border]))
    noise = 1.4826 * float(np.median(np.abs(lum[border] - sky_lum)))

    smooth = gaussian_smooth(lum - sky_lum, GEOM_SMOOTH * max(h, w))
    flat = smooth.ravel()
    total = float(flat.sum())
    if not total > 0:
        raise ValueError("the picture holds no light above its border's median: give the geometry and the sky")
    order = np.argsort(flat)[::-1]
    n = int(np.searchsorted(np.cumsum(flat[order]), GEOM_LIGHT * total)) + 1
    n = max(8, min(n, int((flat > 0).sum())))
    members = order[:n]
    ys, xs = np.unravel_index(members, smooth.shape)
    weights = flat[members]
    cx = float((xs * weights).sum() / weights.sum())
    cy = float((ys * weights).sum() / weights.sum())
    dx, dy = xs - xs.mean(), ys - ys.mean()
    ixx, iyy, ixy = float((dx * dx).mean()), float((dy * dy).mean()), float((dx * dy).mean())
    half, root = 0.5 * (ixx + iyy), math.hypot(0.5 * (ixx - iyy), ixy)
    l1, l2 = half + root, max(half - root, 1e-12)
    pa = math.degrees(0.5 * math.atan2(2 * ixy, ixx - iyy)) % 180.0
    geometry = Geometry(
        cx=(cx + 0.5) * factor - 0.5, cy=(cy + 0.5) * factor - 0.5,
        q=math.sqrt(l2 / l1), pa_deg=pa, a=2.0 * math.sqrt(l1) * factor,
    )
    return {
        "geometry": geometry,
        "sky": [float(v) for v in sky],
        "sky_noise": noise,
        "threshold": float(flat[members[-1]]),
        "outline_centre": [(float(xs.mean()) + 0.5) * factor - 0.5, (float(ys.mean()) + 0.5) * factor - 0.5],
        "work_factor": factor,
        "work_shape": [h, w],
    }


# --------------------------------------------------------------------------------------------------------------
# The polar metrics: 1, 2, 3
# --------------------------------------------------------------------------------------------------------------

def polar_rings(work: np.ndarray, geometry: Geometry) -> dict:
    """``work`` on the deprojected grid, gathered into rings.

    Returns the rings' centres (r/a), their azimuthal profiles (N_RINGS x POLAR_N_PHI x C, NaN where a ring
    leaves the frame), the share of each ring inside the frame, and phi.
    """
    r = (np.arange(POLAR_N_R) + 0.5) / POLAR_N_R * geometry.a
    phi = 2.0 * math.pi * np.arange(POLAR_N_PHI) / POLAR_N_PHI
    c, s = math.cos(math.radians(geometry.pa_deg)), math.sin(math.radians(geometry.pa_deg))
    along = r[:, None] * np.cos(phi)[None, :]
    across = geometry.q * r[:, None] * np.sin(phi)[None, :]
    fine = bilinear(work, geometry.cx + along * c - across * s, geometry.cy + along * s + across * c)

    per = POLAR_N_R // N_RINGS
    fine = fine.reshape(N_RINGS, per, POLAR_N_PHI, -1)
    weight = np.broadcast_to(r.reshape(N_RINGS, per, 1, 1), fine.shape)
    seen = np.isfinite(fine)
    coverage = (weight * seen).sum(axis=(1, 2))[:, 0] / weight.sum(axis=(1, 2))[:, 0]
    # A ring's profile at an azimuth is the area-weighted mean over its fine radii; NaN if any is outside.
    profiles = (fine * weight).sum(axis=1) / weight.sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        means = np.where(seen, fine * weight, 0.0).sum(axis=(1, 2)) / (weight * seen).sum(axis=(1, 2))
    return {
        "r": (np.arange(N_RINGS) + 0.5) / N_RINGS,
        "phi": phi,
        "profiles": profiles,
        "means": means,                              # N_RINGS x C, over the samples inside the frame
        "coverage": coverage,
        "area": r.reshape(N_RINGS, per).sum(axis=1),  # each ring's weight in a band mean
    }


def _colour(numerator: float, denominator: float) -> float:
    if not (numerator > 0 and denominator > 0):
        return math.nan
    return -2.5 * math.log10(numerator / denominator)


def radial_colour(rings: dict) -> dict:
    """Metric 1: ring means of R, G, B and the colours B-R and G-R in magnitudes."""
    means, r, cover = rings["means"], rings["r"], rings["coverage"]
    usable = cover >= 0.5
    b_r = np.array([_colour(m[2], m[0]) if ok else math.nan for m, ok in zip(means, usable)])
    g_r = np.array([_colour(m[1], m[0]) if ok else math.nan for m, ok in zip(means, usable)])

    def band(lo: float, hi: float) -> dict:
        pick = (r >= lo) & (r < hi) & usable
        if not pick.any():
            return {"b_r": math.nan, "g_r": math.nan, "rings": 0}
        w = (rings["area"] * cover)[pick]
        rgb = (means[pick] * w[:, None]).sum(axis=0) / w.sum()
        return {"b_r": _colour(rgb[2], rgb[0]), "g_r": _colour(rgb[1], rgb[0]), "rings": int(pick.sum())}

    inner, outer = band(*COLOUR_INNER), band(*COLOUR_OUTER)
    return {
        "r_over_a": r, "mean_r": np.where(usable, means[:, 0], np.nan), "mean_g": np.where(usable, means[:, 1], np.nan),
        "mean_b": np.where(usable, means[:, 2], np.nan), "b_r": b_r, "g_r": g_r, "coverage": cover,
        "inner": inner, "outer": outer,
        "b_r_gradient": outer["b_r"] - inner["b_r"], "g_r_gradient": outer["g_r"] - inner["g_r"],
    }


def fourier_amplitudes(rings: dict) -> dict:
    """Metric 2: A_m = |sum I exp(-i m phi)| / sum I per ring on the luminance, m = 1..M_MAX, and the crest's azimuth."""
    lum = luminance(rings["profiles"])
    phi, r = rings["phi"], rings["r"]
    amplitude = np.full((M_MAX, N_RINGS), np.nan)
    phase = np.full((M_MAX, N_RINGS), np.nan)
    for k in range(N_RINGS):
        total = lum[k].sum()
        if not (np.isfinite(total) and total > 0):
            continue
        for m in range(1, M_MAX + 1):
            c = (lum[k] * np.exp(-1j * m * phi)).sum()
            amplitude[m - 1, k] = abs(c) / total
            phase[m - 1, k] = math.degrees((-np.angle(c) / m) % (2 * math.pi / m))
    pick = (r >= PATTERN_RANGE[0]) & (r < PATTERN_RANGE[1]) & np.isfinite(amplitude[0])
    mean = amplitude[:, pick].mean(axis=1) if pick.any() else np.full(M_MAX, np.nan)
    known = bool(np.isfinite(mean).all())
    return {
        "r_over_a": r, "amplitude": amplitude, "phase_deg": phase,
        "mean_amplitude": mean, "rings": int(pick.sum()),
        "dominant_m": int(np.argmax(mean)) + 1 if known else None,
        "dominant_m_from_2": int(np.argmax(mean[1:])) + 2 if known else None,
    }


def arm_contrast(rings: dict) -> dict:
    """Metric 3: per ring, the 90th over the 10th percentile of the blue profile cut to m <= M_MAX."""
    blue, r = rings["profiles"][..., 2], rings["r"]
    contrast = np.full(N_RINGS, np.nan)
    for k in range(N_RINGS):
        if not np.isfinite(blue[k]).all():
            continue
        spectrum = np.fft.rfft(blue[k])
        spectrum[M_MAX + 1 :] = 0.0
        low, high = np.percentile(np.fft.irfft(spectrum, n=POLAR_N_PHI), CONTRAST_PERCENTILES)
        if low > 0:
            contrast[k] = high / low
    pick = (r >= PATTERN_RANGE[0]) & (r < PATTERN_RANGE[1]) & np.isfinite(contrast)
    return {
        "r_over_a": r, "contrast": contrast, "rings": int(pick.sum()),
        "median": float(np.median(contrast[pick])) if pick.any() else math.nan,
    }


# --------------------------------------------------------------------------------------------------------------
# The image-plane metrics: 4, 5, 6
# --------------------------------------------------------------------------------------------------------------

def dark_fraction(lum: np.ndarray, rho: np.ndarray, geometry: Geometry) -> dict:
    """Metric 4: the share of the annulus's pixels below (1 - DARK_T) x the median of the lattice around them."""
    rows, cols = np.nonzero((rho >= DISC_INNER) & (rho < 1.0))
    spacing = max(1, int(round(DARK_SPACING * geometry.a)))
    out = {"fraction": math.nan, "pixels": int(rows.size), "lattice": DARK_LATTICE, "spacing_px": spacing}
    if rows.size == 0:
        return out
    median = np.median(lattice_values(lum, rows, cols, DARK_LATTICE, spacing), axis=1)
    dark = (median > 0) & (lum[rows, cols] < (1.0 - DARK_T) * median)
    out["fraction"] = float(dark.sum() / rows.size)
    return out


def _window(rho: np.ndarray) -> np.ndarray:
    """The raised-cosine window of metric 5: 0 at DISC_INNER and at 1, 1 between the two tapers."""
    rise = np.clip((rho - DISC_INNER) / TAPER, 0.0, 1.0)
    fall = np.clip((1.0 - rho) / TAPER, 0.0, 1.0)
    return 0.25 * (1 - np.cos(math.pi * rise)) * (1 - np.cos(math.pi * fall))


def power_slope(lum: np.ndarray, background: np.ndarray, rho: np.ndarray, geometry: Geometry) -> dict:
    """Metric 5: the slope of log10 P against log10 k of the windowed unsharp-masked luminance."""
    window = _window(rho) * (background > 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        unsharp = np.where(background > 0, (lum - background) / background, 0.0)
    norm = float((window**2).sum())
    out = {"slope": math.nan, "unsharp_rms": math.nan, "kappa": [], "power": [], "reason": None}
    if norm <= 0:
        out["reason"] = "the annulus is empty"
        return out
    mean = float((window * unsharp).sum() / window.sum())
    field = window * (unsharp - mean)
    out["unsharp_rms"] = math.sqrt(float((field**2).sum()) / norm)
    if SLOPE_KAPPA[1] > 0.5 * geometry.a:
        out["reason"] = f"a = {geometry.a:.0f} px: {SLOPE_KAPPA[1]:.0f} cycles per a is past the pixel grid's Nyquist"
        return out

    n = 2 * int(math.ceil(geometry.a)) + 2
    x0, y0 = int(round(geometry.cx)) - n // 2, int(round(geometry.cy)) - n // 2
    box = np.zeros((n, n))
    h, w = field.shape
    ya, yb, xa, xb = max(y0, 0), min(y0 + n, h), max(x0, 0), min(x0 + n, w)
    box[ya - y0 : yb - y0, xa - x0 : xb - x0] = field[ya:yb, xa:xb]

    power = np.abs(np.fft.rfft2(box)) ** 2
    kappa = geometry.a * np.hypot(np.fft.fftfreq(n)[:, None], np.fft.rfftfreq(n)[None, :])
    edges = np.geomspace(SLOPE_KAPPA[0], SLOPE_KAPPA[1], SLOPE_BINS + 1)
    which = np.digitize(kappa.ravel(), edges) - 1
    ks, ps = [], []
    for i in range(SLOPE_BINS):
        sel = which == i
        if sel.sum() < 4:
            continue
        ks.append(float(kappa.ravel()[sel].mean()))
        ps.append(float(power.ravel()[sel].mean()))
    out["kappa"], out["power"] = ks, ps
    if len(ks) < 3 or min(ps) <= 0:
        out["reason"] = "too few bins hold power"
        return out
    out["slope"] = float(np.polyfit(np.log10(ks), np.log10(ps), 1)[0])
    return out


def point_sources(lum: np.ndarray, background: np.ndarray, rho: np.ndarray) -> dict:
    """Metric 6: compact local maxima of the small-scale relative residual, inside the ellipse and outside it."""
    annulus = (rho >= DISC_INNER) & (rho < 1.0)
    level = float(np.median(background[annulus])) if annulus.any() else float(np.median(background))
    soft = POINT_SOFT * max(level, 0.0)
    denominator = np.maximum(background, 0.0) + soft
    with np.errstate(invalid="ignore", divide="ignore"):
        residual = (gaussian_smooth(lum, POINT_SIGMAS[0]) - gaussian_smooth(lum, POINT_SIGMAS[1])) / denominator
    residual = np.where(denominator > 0, residual, 0.0)

    h, w = residual.shape
    core = residual[2 : h - 2, 2 : w - 2]
    peak = np.ones_like(core, dtype=bool)
    compact = np.ones_like(core, dtype=bool)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dy == 0 and dx == 0:
                continue
            other = residual[2 + dy : h - 2 + dy, 2 + dx : w - 2 + dx]
            if max(abs(dy), abs(dx)) == 1:
                peak &= core > other
            else:
                compact &= other < POINT_COMPACT * core
    candidate = np.zeros((h, w), dtype=bool)
    candidate[2 : h - 2, 2 : w - 2] = peak & compact

    # The robust sigma is local: the residual's scatter on a lattice about each candidate over the floor.
    rows, cols = np.nonzero(candidate & (residual > POINT_FLOOR))
    around = lattice_values(residual, rows, cols, POINT_LATTICE, POINT_SPACING)
    middle = np.median(around, axis=1)
    sigma = 1.4826 * np.median(np.abs(around - middle[:, None]), axis=1)
    stands = residual[rows, cols] - middle > POINT_K * sigma
    inside = rho[rows, cols] < 1.0

    out = {"softening": soft}
    for name, side, pixels in (("inside", inside, rho < 1.0), ("outside", ~inside, rho >= 1.0)):
        out[name] = {
            "count": int((side & stands).sum()),
            # The same sources by the floor alone: what the robust sigma, which in a textured disc is the
            # picture's own grain as much as its noise, took away.
            "count_above_floor": int(side.sum()),
            "median_sigma": float(np.median(sigma[side])) if side.any() else math.nan,
            "pixels": int(pixels.sum()),
        }
    return out


# --------------------------------------------------------------------------------------------------------------
# Everything
# --------------------------------------------------------------------------------------------------------------

def definitions() -> dict:
    """Every metric's definition with the numbers this module holds; written into the JSON."""
    lo, hi = PATTERN_RANGE
    return {
        "pixel_value": "an 8-bit channel / 255, sRGB-decoded to linear display light unless 'encoded'; luminance = "
                       f"{LUMA[0]} R + {LUMA[1]} G + {LUMA[2]} B. Statistics of a picture, not photometry.",
        "coordinates": "x right, y down, px, pixel centres at integers; the position angle is the long axis in degrees "
                       "from +x towards +y, [0, 180); phi from the long axis in the deprojected plane, same sense.",
        "geometry": f"the picture's outline, not an inclination. On the picture area-averaged to a longer side <= {GEOM_WORK} px: "
                    f"sky = per-channel median of a border {GEOM_BORDER:.0%} of the shorter side wide; luminance less sky smoothed "
                    f"by a Gaussian of sigma {GEOM_SMOOTH:.0%} of the longer side; the outline = the brightest pixels holding "
                    f"{GEOM_LIGHT:.0%} of that light; centre = their light-weighted centroid; q, angle, a = 2 sqrt(l1) from their "
                    "unweighted second moments.",
        "standard_scale": f"sky subtracted; area-averaged by a/{STANDARD_A} so that a = {STANDARD_A} px (never enlarged: "
                          f"below_standard says so); polar grid {POLAR_N_R} radii x {POLAR_N_PHI} azimuths, bilinear, short axis "
                          f"stretched by 1/q; {N_RINGS} rings of width a/{N_RINGS}, area-weighted.",
        "radial_colour": "per ring, mean R, G, B and B-R = -2.5 log10(B/R), G-R = -2.5 log10(G/R) of the means, mag. Headline: "
                         f"the colour of the area-weighted means over {COLOUR_INNER[0]} <= r/a < {COLOUR_INNER[1]} (inner) and "
                         f"{COLOUR_OUTER[0]} <= r/a < {COLOUR_OUTER[1]} (outer), and outer minus inner.",
        "fourier": f"per ring on the luminance, A_m = |sum I(phi) exp(-i m phi)| / sum I(phi), m = 1..{M_MAX}; 1 + A cos(m phi) "
                   f"gives A/2. Phase = the crest's azimuth, [0, 360/m) deg. Headline: the mean of each A_m over the complete "
                   f"rings centred in {lo} <= r/a < {hi}, and the m of the largest.",
        "arm_contrast": f"per ring, the blue channel's azimuthal profile cut to Fourier terms m <= {M_MAX}; its "
                        f"{CONTRAST_PERCENTILES[1]:.0f}th percentile over its {CONTRAST_PERCENTILES[0]:.0f}th. 1 + A cos(m phi) gives "
                        f"(1 + A cos 18 deg)/(1 - A cos 18 deg). Headline: the median over the complete rings centred in "
                        f"{lo} <= r/a < {hi}.",
        "dark_fraction": f"local level = the median of the luminance on a {DARK_LATTICE} x {DARK_LATTICE} lattice of pixels "
                         f"{DARK_SPACING * 256:.0f}a/256 apart centred on the pixel (frame reflected); of the pixels with "
                         f"{DISC_INNER} <= r/a < 1 (elliptical), the fraction with luminance < (1 - {DARK_T}) x that median.",
        "power_slope": f"U = (luminance - background)/background, background sigma {BACKGROUND_SIGMA} a, on {DISC_INNER} <= r/a < 1, "
                       f"less its weighted mean, times a raised-cosine window (edges {TAPER} a wide); 2-D power in a square of side "
                       f"2a + 2 px; mean power in {SLOPE_BINS} logarithmic bins of {SLOPE_KAPPA[0]:.0f}-{SLOPE_KAPPA[1]:.0f} cycles per a; "
                       "least-squares slope of log10 P on log10 k. unsharp_rms = the windowed rms of U.",
        "point_sources": f"residual = (luminance smoothed at {POINT_SIGMAS[0]:.0f} px - at {POINT_SIGMAS[1]:.0f} px, at the working "
                         f"scale) / (background + {POINT_SOFT} x the background's median over the annulus); a source = a strict "
                         f"8-neighbour maximum above {POINT_FLOOR}, more than {POINT_K:.0f} x 1.4826 MAD above the median of the "
                         f"residual on a {POINT_LATTICE} x {POINT_LATTICE} lattice of pixels {POINT_SPACING} px apart centred on it, "
                         f"whose 16 pixels two away are all under {POINT_COMPACT} of the peak. Counted for r/a < 1 and r/a >= 1; "
                         "count_above_floor leaves the sigma test out.",
    }


def measure(image: np.ndarray, geometry: Geometry | None = None, *, sky=None, values: str = "linear",
            standard_a: float = STANDARD_A, estimate: dict | None = None) -> dict:
    """Every metric of ``image`` (H x W x 3 float, the values the caller decoded) as one dictionary.

    ``geometry`` None estimates the outline; ``sky`` None takes the border's per-channel median; ``estimate`` is
    an ``estimate_outline`` result already in hand (else it is made here: it is reported even when not used).
    ``values`` only labels the output ("linear" or "encoded"): the arrays are measured as given. NaN marks what
    could not be measured; ``to_json`` turns it into null.
    """
    image = np.asarray(image)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"an H x W x 3 array is needed, not {image.shape}")
    if estimate is None:
        try:
            estimate = estimate_outline(image)      # always reported, beside what was used
        except ValueError:
            if geometry is None or sky is None:
                raise
    used = geometry if geometry is not None else estimate["geometry"]
    sky_used = np.asarray(sky if sky is not None else estimate["sky"], dtype=np.float64)

    factor = max(1.0, used.a / standard_a)
    work = resample_area(image, factor) - sky_used
    g = used.scaled(factor)

    rings = polar_rings(work, g)
    lum = luminance(work)
    background = gaussian_smooth(lum, BACKGROUND_SIGMA * g.a)
    rho, _ = elliptical_radius(lum.shape, g)

    colour = radial_colour(rings)
    fourier = fourier_amplitudes(rings)
    contrast = arm_contrast(rings)
    dark = dark_fraction(lum, rho, g)
    slope = power_slope(lum, background, rho, g)
    points = point_sources(lum, background, rho)

    headline = {
        "a_px": used.a, "axis_ratio": used.q, "position_angle_deg": used.pa_deg,
        "b_r_inner": colour["inner"]["b_r"], "b_r_outer": colour["outer"]["b_r"], "b_r_gradient": colour["b_r_gradient"],
        "g_r_inner": colour["inner"]["g_r"], "g_r_outer": colour["outer"]["g_r"], "g_r_gradient": colour["g_r_gradient"],
        **{f"A{m}": float(fourier["mean_amplitude"][m - 1]) for m in range(1, M_MAX + 1)},
        "dominant_m": fourier["dominant_m"], "dominant_m_from_2": fourier["dominant_m_from_2"],
        "arm_contrast": contrast["median"],
        "dark_fraction": dark["fraction"],
        "power_slope": slope["slope"], "unsharp_rms": slope["unsharp_rms"],
        "points_inside": points["inside"]["count"], "points_outside": points["outside"]["count"],
    }
    return {
        "tool": "goal_metrics", "version": VERSION,
        "note": "statistics of a picture's pixel values; display targets, not acceptance rows, and not photometry",
        "image": {"height": int(image.shape[0]), "width": int(image.shape[1]), "values": values},
        "geometry": {
            "used": asdict(used),
            "source": "given" if geometry is not None else "estimated from the picture's outline",
            "estimated": None if estimate is None else {
                **asdict(estimate["geometry"]),
                "threshold_over_sky": estimate["threshold"], "sky_noise": estimate["sky_noise"],
                "outline_centre": estimate["outline_centre"], "work_factor": estimate["work_factor"],
            },
        },
        "sky": {"subtracted": [float(v) for v in sky_used], "source": "given" if sky is not None else "the border's median"},
        "standard": {
            "a_px": float(standard_a), "factor": factor, "working_a_px": g.a,
            "working_shape": [int(lum.shape[0]), int(lum.shape[1])], "below_standard": bool(used.a < standard_a - 1e-9),
        },
        "headline": headline,
        "metrics": {
            "radial_colour": colour, "fourier": fourier, "arm_contrast": contrast,
            "dark_fraction": dark, "power_slope": slope, "point_sources": points,
        },
        "definitions": definitions(),
    }


def to_json(value):
    """``value`` as plain JSON types: arrays to lists, floats to six significant figures, NaN to null (B9)."""
    if isinstance(value, dict):
        return {str(k): to_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return to_json(value.tolist())
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(f"{float(value):.6g}") if math.isfinite(value) else None
    return value


# --------------------------------------------------------------------------------------------------------------
# The table and the command line
# --------------------------------------------------------------------------------------------------------------

COLUMNS: tuple[tuple[str, str, str], ...] = (
    # (heading, headline key, format)
    ("a px", "a_px", ".0f"), ("q", "axis_ratio", ".3f"), ("PA°", "position_angle_deg", ".1f"),
    ("B−R in", "b_r_inner", "+.3f"), ("B−R out", "b_r_outer", "+.3f"), ("Δ(B−R)", "b_r_gradient", "+.3f"),
    *((f"A{m}", f"A{m}", ".4f") for m in range(1, M_MAX + 1)),
    ("m", "dominant_m", "d"), ("arm/interarm B", "arm_contrast", ".3f"), ("dark frac", "dark_fraction", ".4f"),
    ("PS slope", "power_slope", "+.2f"), ("points in", "points_inside", "d"), ("points out", "points_outside", "d"),
)


def table_header() -> str:
    names = ["image", "values", *(c[0] for c in COLUMNS)]
    return "| " + " | ".join(names) + " |\n|" + "---|" * len(names)


def table_row(name: str, result: dict) -> str:
    cells = [name, result["image"]["values"]]
    for _, key, fmt in COLUMNS:
        v = result["headline"][key]
        missing = v is None or (isinstance(v, float) and not math.isfinite(v))
        cells.append("—" if missing else format(v, fmt))
    return "| " + " | ".join(cells) + " |"


def summary(name: str, result: dict, seconds: float) -> str:
    g, h, s = result["geometry"], result["headline"], result["standard"]
    used = g["used"]

    def f(v, fmt):
        return "none" if v is None or (isinstance(v, float) and not math.isfinite(v)) else format(v, fmt)

    lines = [
        f"{name}: {result['image']['width']} x {result['image']['height']} px, {result['image']['values']} values, {seconds:.1f} s",
        f"  geometry ({g['source']}): centre ({used['cx']:.1f}, {used['cy']:.1f}), q {used['q']:.3f}, "
        f"angle {used['pa_deg']:.1f} deg, a {used['a']:.1f} px",
        f"  standard scale: a = {s['working_a_px']:.1f} px after area-averaging by {s['factor']:.3f}"
        + ("  (BELOW STANDARD: image-plane metrics not comparable)" if s["below_standard"] else ""),
        f"  sky subtracted: {', '.join(f'{v:.5f}' for v in result['sky']['subtracted'])} ({result['sky']['source']})",
        f"  1 colour B-R: inner {f(h['b_r_inner'], '+.3f')}, outer {f(h['b_r_outer'], '+.3f')}, outer - inner {f(h['b_r_gradient'], '+.3f')} mag"
        f"   (G-R: {f(h['g_r_inner'], '+.3f')}, {f(h['g_r_outer'], '+.3f')}, {f(h['g_r_gradient'], '+.3f')})",
        "  2 Fourier A_m, m = 1..8: " + " ".join(f(h[f"A{m}"], ".4f") for m in range(1, M_MAX + 1))
        + f"   dominant m {f(h['dominant_m'], 'd')} (from 2: {f(h['dominant_m_from_2'], 'd')})",
        f"  3 arm-interarm contrast, blue: {f(h['arm_contrast'], '.3f')}",
        f"  4 dark-lane covering fraction: {f(h['dark_fraction'], '.4f')}",
        f"  5 power-spectrum slope: {f(h['power_slope'], '+.2f')}   (unsharp rms {f(h['unsharp_rms'], '.3f')})",
        f"  6 point sources: {h['points_inside']} inside, {h['points_outside']} outside",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="Six statistics of a picture of a disc galaxy (display targets, not rows).")
    parser.add_argument("image", nargs="?", help="a JPEG or PNG: a goal picture or a capture of the viewer")
    parser.add_argument("--centre", nargs=2, type=float, metavar=("X", "Y"), help="the centre, px (else estimated)")
    parser.add_argument("--axis-ratio", type=float, metavar="Q", help="short axis over long axis (else estimated)")
    parser.add_argument("--position-angle", type=float, metavar="DEG", help="the long axis, degrees from +x towards +y (else estimated)")
    parser.add_argument("--radius", type=float, metavar="PX", help="the outer semi-major radius a, px (else estimated)")
    parser.add_argument("--sky", nargs=3, type=float, metavar=("R", "G", "B"), help="the sky to subtract (else the border's median)")
    parser.add_argument("--encoded", action="store_true", help="keep the display-encoded values (default: sRGB decoded to linear)")
    parser.add_argument("--json", metavar="OUT", help="write everything as JSON to OUT ('-' for stdout)")
    parser.add_argument("--table", action="store_true", help="print one Markdown table row of the headline scalars")
    parser.add_argument("--table-header", action="store_true", help="print the table's header (needs no image)")
    parser.add_argument("--name", help="the row's label (default: the file's name)")
    args = parser.parse_args(argv)

    if args.table_header:
        print(table_header())
    if args.image is None:
        if args.table_header:
            return 0
        parser.error("an image is needed")
    if args.axis_ratio is not None and not 0 < args.axis_ratio <= 1:
        parser.error("--axis-ratio is short over long: 0 < Q <= 1")

    start = time.perf_counter()
    image = load_image(args.image, encoded=args.encoded)
    given = (args.centre, args.axis_ratio, args.position_angle, args.radius)
    geometry, which = None, "estimated from the picture's outline"
    try:
        estimate = estimate_outline(image)
    except ValueError as error:
        print(f"{args.image}: {error}", file=sys.stderr)
        return 1
    if any(v is not None for v in given):
        geometry = estimate["geometry"]
        names = []
        if args.centre is not None:
            geometry, names = replace(geometry, cx=args.centre[0], cy=args.centre[1]), names + ["centre"]
        if args.axis_ratio is not None:
            geometry, names = replace(geometry, q=args.axis_ratio), names + ["axis ratio"]
        if args.position_angle is not None:
            geometry, names = replace(geometry, pa_deg=args.position_angle % 180.0), names + ["angle"]
        if args.radius is not None:
            geometry, names = replace(geometry, a=args.radius), names + ["radius"]
        which = "given: " + ", ".join(names) + ("" if len(names) == 4 else "; the rest estimated")
    result = measure(image, geometry, sky=args.sky, values="encoded" if args.encoded else "linear", estimate=estimate)
    result["geometry"]["source"] = which
    result["image"]["path"] = Path(args.image).name
    seconds = time.perf_counter() - start
    result["seconds"] = seconds

    name = args.name or Path(args.image).name
    if args.json:
        text = json.dumps(to_json(result), indent=1, ensure_ascii=False) + "\n"
        if args.json == "-":
            sys.stdout.write(text)
        else:
            Path(args.json).write_text(text, encoding="utf-8", newline="\n")
    if args.table:
        print(table_row(name, result))
    if not args.table and args.json != "-":
        print(summary(name, result, seconds))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
