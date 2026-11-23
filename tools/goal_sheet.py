"""Set captured frames beside their goal picture (S105, BUILD_VIII row 105): one sheet PNG per template.

The look capture (``npm --prefix frontend run look``, frontend/e2e/look.spec.ts) writes 1024 px frames named
``<template>-<anything>.png`` into a directory (default docs/goals/look/). This tool takes every frame there whose name
starts with a template's name and lays them in a row after that template's goal picture - the Milky Way's artist's
impression cropped to its centre square, NGC 4414's Hubble picture as it is, letterboxed onto a square - each tile with
its caption under it, and writes ``<out>/<template>-sheet.png`` about 1200 px wide, small enough to read.

A display tool for the illustrative look's tuning, not a measurement: it reads no number off a picture.

    uv run python tools/goal_sheet.py                       docs/goals/look -> docs/goals/look/<template>-sheet.png
    uv run python tools/goal_sheet.py --frames D --out O --only milky_way-physical,milky_way-illustrative
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
GOALS = ROOT / "docs" / "goals"

# Each template's goal picture (docs/goals/, local files, gitignored) and how it is set on its square tile.
TEMPLATE_GOALS = {
    "milky_way": ("Artist’s_impression_of_the_Milky_Way.jpg", "crop"),
    "ngc_4414": ("NGC_4414_(NASA-med).jpg", "letterbox"),
}

CAPTION_PX = 22
GAP_PX = 6


def square(img: Image.Image, how: str, side: int) -> Image.Image:
    """The picture on a square tile of `side` px: its centre square ("crop"), or the whole of it on black ("letterbox")."""
    img = img.convert("RGB")
    w, h = img.size
    if how == "crop":
        s = min(w, h)
        box = ((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)
        return img.crop(box).resize((side, side), Image.LANCZOS)
    scale = side / max(w, h)
    fit = img.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    tile = Image.new("RGB", (side, side), (0, 0, 0))
    tile.paste(fit, ((side - fit.width) // 2, (side - fit.height) // 2))
    return tile


def font() -> ImageFont.ImageFont:
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, 15)
        except OSError:
            continue
    return ImageFont.load_default()


def sheet(tiles: list[tuple[str, Image.Image]], width: int) -> Image.Image:
    """The tiles in one row (two rows past four), each with its caption under it, about `width` px wide."""
    per_row = len(tiles) if len(tiles) <= 4 else (len(tiles) + 1) // 2
    rows = (len(tiles) + per_row - 1) // per_row
    side = (width - GAP_PX * (per_row + 1)) // per_row
    out = Image.new("RGB", (GAP_PX + per_row * (side + GAP_PX), GAP_PX + rows * (side + CAPTION_PX + GAP_PX)), (24, 24, 24))
    draw = ImageDraw.Draw(out)
    f = font()
    for i, (caption, img) in enumerate(tiles):
        r, c = divmod(i, per_row)
        x = GAP_PX + c * (side + GAP_PX)
        y = GAP_PX + r * (side + CAPTION_PX + GAP_PX)
        out.paste(img.resize((side, side), Image.LANCZOS) if img.size != (side, side) else img, (x, y))
        draw.text((x + 2, y + side + 3), caption, fill=(230, 230, 230), font=f)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--frames", type=Path, default=GOALS / "look", help="the look capture's directory")
    ap.add_argument("--out", type=Path, default=None, help="where the sheets go (default: the frames' directory)")
    ap.add_argument("--only", default="", help="comma-separated frame names (without .png), in this order")
    ap.add_argument("--width", type=int, default=1200, help="the sheet's width, px")
    args = ap.parse_args(argv)
    out_dir = args.out or args.frames
    out_dir.mkdir(parents=True, exist_ok=True)
    only = [n.strip() for n in args.only.split(",") if n.strip()]
    written = 0
    for template, (goal_name, how) in TEMPLATE_GOALS.items():
        if only:
            frames = [args.frames / f"{n}.png" for n in only if n.startswith(f"{template}-")]
        else:
            frames = sorted(p for p in args.frames.glob(f"{template}-*.png") if not p.stem.endswith("-sheet"))
        frames = [p for p in frames if p.exists()]
        if not frames:
            continue
        side = (args.width - GAP_PX * (len(frames) + 2)) // (len(frames) + 1) if len(frames) < 4 else 512
        tiles: list[tuple[str, Image.Image]] = []
        goal = GOALS / goal_name
        if goal.exists():
            tiles.append((f"goal: {template}", square(Image.open(goal), how, max(side, 256))))
        else:
            print(f"goal_sheet: no goal picture {goal}", file=sys.stderr)
        for p in frames:
            tiles.append((p.stem, square(Image.open(p), "crop", max(side, 256))))
        path = out_dir / f"{template}-sheet.png"
        sheet(tiles, args.width).save(path)
        print(f"goal_sheet: {path} ({len(tiles)} tiles)")
        written += 1
    if not written:
        print(f"goal_sheet: no frames named <template>-*.png in {args.frames}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
