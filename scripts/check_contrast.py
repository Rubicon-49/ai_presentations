#!/usr/bin/env python3
"""check_contrast.py — WCAG contrast of text vs local background, sampled across
each rendered slide. Fails a slide if any sampled region drops below the floor.

Usage:
    python scripts/check_contrast.py <build-dir> [--aaa] [--text-mask]

    <build-dir>   directory of rendered slide-XX.png files (order-independent)
    --aaa         use the 7:1 AAA body floor instead of 4.5:1 AA
    --text-mask   restrict sampling to likely text pixels (fixes the miss bias
                  below); requires the `ocr` extra: uv sync --extra ocr

LIMITATION (default mode): background/foreground in each cell are approximated by
its darkest and lightest pixels. A cell that contains BOTH a high-contrast pair
(e.g. a logo, or a photo edge) AND unreadable low-contrast text will PASS on the
strength of the high-contrast pair — the bad text is missed. This is a MISS bias,
not a false-alarm bias: it is reliable as a floor for simple text-on-solid slides
and unreliable exactly where text overlays images. Use --text-mask for those.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image  # pip install pillow

AA_LARGE, AA_BODY, AAA_BODY = 3.0, 4.5, 7.0
GRID = 3           # 3x3 = 9 sample cells
MIN_SEP = 0.02     # skip near-flat cells (no real fg/bg separation)


def luminance(rgb: np.ndarray) -> np.ndarray:
    """Relative luminance (WCAG) for an array of sRGB values, shape (..., 3),
    values 0-255. Returns the leading shape. Computed once per pixel."""
    a = rgb.astype(np.float64) / 255.0
    a = np.where(a <= 0.03928, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def ratio(l_hi: float, l_lo: float) -> float:
    l1, l2 = (l_hi, l_lo) if l_hi >= l_lo else (l_lo, l_hi)
    return (l1 + 0.05) / (l2 + 0.05)


def sample_cells(w: int, h: int, n: int = GRID):
    """Yield interior (x0, y0, x1, y1) boxes — one per grid cell."""
    for gy in range(n):
        for gx in range(n):
            x0, y0 = int(w * (gx + 0.15) / n), int(h * (gy + 0.15) / n)
            x1, y1 = int(w * (gx + 0.85) / n), int(h * (gy + 0.85) / n)
            yield (x0, y0, x1, y1)


def _text_mask(cell_rgb: np.ndarray):
    """Optional: return a boolean mask of likely text pixels in the cell, using
    Tesseract word boxes. Returns None if pytesseract/tesseract is unavailable."""
    try:
        import pytesseract
    except ImportError:
        return None
    from PIL import Image as _I
    data = pytesseract.image_to_data(
        _I.fromarray(cell_rgb.astype(np.uint8)),
        output_type=pytesseract.Output.DICT)
    mask = np.zeros(cell_rgb.shape[:2], dtype=bool)
    found = False
    for i, conf in enumerate(data["conf"]):
        try:
            c = float(conf)
        except (TypeError, ValueError):
            continue
        if c < 40 or not data["text"][i].strip():
            continue
        x, y, bw, bh = (data["left"][i], data["top"][i],
                        data["width"][i], data["height"][i])
        mask[y:y + bh, x:x + bw] = True
        found = True
    return mask if found else None


def check_slide(png: Path, floor: float, use_text_mask: bool = False):
    """Return a list of (cell_index, ratio) for cells failing the floor."""
    rgb = np.asarray(Image.open(png).convert("RGB"))
    h, w = rgb.shape[:2]
    lum = luminance(rgb)                      # one luminance pass for the slide
    fails = []
    for i, (x0, y0, x1, y1) in enumerate(sample_cells(w, h)):
        cell_l = lum[y0:y1, x0:x1]
        if cell_l.size == 0:
            continue

        if use_text_mask:
            mask = _text_mask(rgb[y0:y1, x0:x1])
            if mask is None or not mask.any():
                continue                      # no detected text → nothing to judge
            text_l = cell_l[mask]
            bg_l = cell_l[~mask]
            if bg_l.size == 0:
                continue
            # worst realistic pairing: median text vs the bg it sits on
            l_text = float(np.median(text_l))
            l_bg = float(np.median(bg_l))
            r = ratio(l_bg, l_text)
        else:
            # coarse: extremes of the cell stand in for fg/bg (see LIMITATION)
            l_hi, l_lo = float(cell_l.max()), float(cell_l.min())
            if abs(l_hi - l_lo) < MIN_SEP:    # near-flat cell → no text here
                continue
            r = ratio(l_hi, l_lo)

        if r < floor:
            fails.append((i, round(r, 2)))
    return fails


def main():
    ap = argparse.ArgumentParser(description="WCAG contrast gate over rendered slides.")
    ap.add_argument("build_dir", type=Path, help="dir of slide-XX.png files")
    ap.add_argument("--aaa", action="store_true", help="use 7:1 AAA floor")
    ap.add_argument("--text-mask", action="store_true",
                    help="restrict to text pixels (needs the ocr extra)")
    args = ap.parse_args()

    floor = AAA_BODY if args.aaa else AA_BODY
    pngs = sorted(args.build_dir.glob("slide-*.png"))
    if not pngs:
        sys.exit(f"no slide-*.png in {args.build_dir}")

    bad = False
    for png in pngs:
        fails = check_slide(png, floor, use_text_mask=args.text_mask)
        if fails:
            bad = True
            detail = ", ".join(f"cell{i}:{r}:1" for i, r in fails)
            print(f"FAIL {png.name}: {len(fails)} region(s) < {floor}:1 — {detail}")
        else:
            print(f"PASS {png.name}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
