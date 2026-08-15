#!/usr/bin/env python3
"""check_whitespace.py — background-pixel ratio of each rendered slide against the
floor for its slide type. Implements design-principles.md rule 4 / §6 "Whitespace
Ratio": information slides ≥40% empty, hero/title/section ≥60%, quote ≥70%.

Usage:
    python scripts/check_whitespace.py <build-dir> [--slides <slides.md>] [--json]

    <build-dir>   directory of rendered slide-XX.png files
    --slides      deck source, used to map slide N → type via its `_class`
                  directive. Defaults to <build-dir>/../slides.md.
    --json        machine-readable output for the QA report

"Empty" = pixels matching the slide's own background colour (the modal colour of
the image) within a small tolerance, which absorbs anti-aliasing and the subtle
banding a PNG encoder leaves on a flat fill.

LIMITATION: a full-bleed photo slide has no modal background in this sense — the
image IS the slide — so the ratio it reports is near zero and the check will fail
by construction. That is deliberate for framed art, wrong for intentional
full-bleed treatments; mark those slides `_class: bleed` and they are skipped
(reported as SKIP, never silently passed).
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

# floor per slide type, from design-principles.md §6
FLOORS = {"content": 0.40, "hero": 0.60, "quote": 0.70}

# marp layout class → whitespace category
CLASS_TO_TYPE = {
    "title": "hero",
    "statement": "hero",
    "section": "hero",
    "divider": "hero",
    "quote": "quote",
}
BLEED = "bleed"          # full-bleed art: skipped, see LIMITATION above

# Per-channel RGB distance still counted as background. Keep this SMALL: it only
# needs to absorb PNG banding on a flat fill, not real surfaces. A neutral ramp
# puts --surface (#FFFFFF) just 8/7/5 off --bg (#F7F8FA), so a loose tolerance
# counts every card as empty and the check reports ~99% on a full slide.
TOLERANCE = 4


def slide_classes(slides: Path) -> list[list[str]]:
    """Return the list of layout classes for each slide, in order.

    Marp separates slides on a `---` fence and sets per-slide layout with a
    `<!-- _class: a b -->` directive. A slide with no directive gets [].
    """
    if not slides.exists():
        return []
    body = slides.read_text(encoding="utf-8")
    # drop the YAML frontmatter so its `---` terminator isn't read as a fence
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            body = body[end + 4:]
    out = []
    for chunk in re.split(r"^---\s*$", body, flags=re.MULTILINE):
        m = re.search(r"<!--\s*_class:\s*([^>]*?)-->", chunk)
        out.append(m.group(1).split() if m else [])
    return out


def slide_type(classes: list[str]) -> str:
    """Most specific category wins; unknown/unclassed slides are content slides."""
    if BLEED in classes:
        return BLEED
    for c in classes:
        if c in CLASS_TO_TYPE:
            return CLASS_TO_TYPE[c]
    return "content"


EDGE = 0.02              # outermost 2% of the slide, used to identify the background


def background_colour(rgb: np.ndarray) -> np.ndarray:
    """The slide's background colour, taken as the modal colour of its outer edge.

    Deliberately NOT the modal colour of the whole image: on an overfull slide the
    content is the majority colour, so the mode names the content as background and
    the check reports the inverse of the truth (a 70%-covered slide scores 70%
    empty). Rule 5 reserves the outer 5% as an empty safe-zone, so the extreme
    border is background by construction on any slide that respects the margin.
    """
    h, w = rgb.shape[:2]
    ey, ex = max(1, int(h * EDGE)), max(1, int(w * EDGE))
    frame = np.concatenate([
        rgb[:ey, :, :].reshape(-1, 3), rgb[-ey:, :, :].reshape(-1, 3),
        rgb[:, :ex, :].reshape(-1, 3), rgb[:, -ex:, :].reshape(-1, 3),
    ])
    sample = frame[:: max(1, len(frame) // 100_000)]
    return np.array(Counter(map(tuple, sample)).most_common(1)[0][0])


def background_ratio(png: Path) -> float:
    """Fraction of pixels within TOLERANCE of the slide's background colour."""
    rgb = np.asarray(Image.open(png).convert("RGB"))
    bg = background_colour(rgb)
    flat = rgb.reshape(-1, 3)
    return float((np.abs(flat.astype(np.int16) - bg) <= TOLERANCE).all(axis=1).mean())


def main():
    ap = argparse.ArgumentParser(description="Whitespace-ratio gate over rendered slides.")
    ap.add_argument("build_dir", type=Path, help="dir of slide-XX.png files")
    ap.add_argument("--slides", type=Path, default=None,
                    help="deck slides.md (default: <build-dir>/../slides.md)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    pngs = sorted(args.build_dir.glob("slide-*.png"))
    if not pngs:
        sys.exit(f"no slide-*.png in {args.build_dir}")

    slides = args.slides or args.build_dir.parent / "slides.md"
    classes = slide_classes(slides)
    if classes and len(classes) != len(pngs):
        print(f"warn: {len(classes)} slides in {slides} but {len(pngs)} rendered "
              f"— types may be misaligned", file=sys.stderr)

    results, bad = [], False
    for i, png in enumerate(pngs):
        cls = classes[i] if i < len(classes) else []
        stype = slide_type(cls)
        if stype == BLEED:
            results.append({"slide": png.name, "type": stype, "status": "SKIP"})
            print(f"SKIP {png.name}: full-bleed, whitespace floor not applicable")
            continue
        ratio = background_ratio(png)
        floor = FLOORS[stype]
        ok = ratio >= floor
        bad |= not ok
        results.append({"slide": png.name, "type": stype, "ratio": round(ratio, 3),
                        "floor": floor, "status": "PASS" if ok else "FAIL"})
        print(f"{'PASS' if ok else 'FAIL'} {png.name}: {ratio:.1%} empty "
              f"({stype}, floor {floor:.0%})")

    if args.json:
        print(json.dumps(results, indent=2))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
