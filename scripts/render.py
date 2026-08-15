#!/usr/bin/env python3
"""render.py — export every slide of a built deck to build/slide-XX.png (1920x1080).

Usage: python scripts/render.py decks/<name>

The deck declares its own format in slides.md frontmatter (`marp: true` → Marp,
otherwise Slidev), so no flag is needed. Marp and Slidev use their native
per-slide PNG export; anything else falls back to screenshotting built HTML with
Playwright. All downstream QA checks read the resulting slide-XX.png files.

Browser note: on this machine Marp's default `auto` browser discovery works and
needs no --browser flags. The Playwright fallback launches Chromium directly, so
on Ubuntu 23.10+ (restricted user namespaces) it needs either the chromium
apparmor profile (`sudo apt-get install -y chromium`) or the --no-sandbox arg
below.
"""
import shutil
import subprocess
import sys
import time
from pathlib import Path

CANVAS = (1920, 1080)


def detect_format(slides: Path) -> str:
    """Read the deck's own frontmatter to decide the renderer."""
    head = slides.read_text(encoding="utf-8")[:400]
    return "marp" if "marp: true" in head else "slidev"


def _prepare_out(deck_dir: Path) -> Path:
    """Create build/ (and any missing parents) and clear stale slide PNGs so the
    QA checks never measure images left over from a previous, longer render."""
    out = deck_dir / "build"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("slide-*.png"):
        old.unlink()
    for old in out.glob("slide.*.png"):   # marp's pre-normalization names
        old.unlink()
    return out


def render(deck_dir: Path) -> list[Path]:
    slides = deck_dir / "slides.md"
    if not slides.exists():
        sys.exit(f"no slides.md in {deck_dir}")

    out = _prepare_out(deck_dir)
    fmt = detect_format(slides)

    # Marp (default): native per-slide PNG export.
    if fmt == "marp" and shutil.which("marp"):
        cmd = ["marp", str(slides),
               "--images", "png",
               "--output", str(out / "slide.png"),
               "--allow-local-files",
               # Marp Core escapes tags outside its default allowlist, which
               # dumps inline <svg> diagrams onto the slide as literal source.
               # Decks here are locally authored, so raw HTML is safe to enable.
               "--html"]
        # A deck's theme.css is where `@size` and the layout classes live; the
        # directives only register from a theme file passed with --theme-set.
        theme = deck_dir / "theme.css"
        if theme.exists():
            cmd += ["--theme-set", str(theme)]
        subprocess.run(cmd, check=True)
        # marp emits slide.001.png, slide.002.png … → normalize to slide-01.png
        for i, p in enumerate(sorted(out.glob("slide.*.png")), 1):
            p.rename(out / f"slide-{i:02d}.png")
        return sorted(out.glob("slide-*.png"))

    # Slidev (alt): built-in per-slide PNG export.
    if fmt == "slidev" and shutil.which("slidev"):
        started = time.time()
        subprocess.run(
            ["slidev", "export", str(slides),
             "--format", "png",
             "--output", str(out),
             "--per-slide"],
            check=True)
        # Normalize whatever slidev names them to slide-XX.png. Only files this
        # run produced are eligible: globbing all *.png swept up unrelated
        # images living in build/ and renamed them into the slide sequence.
        exported = [p for p in sorted(out.glob("*.png"))
                    if not p.name.startswith("slide-") and p.stat().st_mtime >= started]
        for i, p in enumerate(exported, 1):
            p.rename(out / f"slide-{i:02d}.png")
        return sorted(out.glob("slide-*.png"))

    # Fallback: build HTML, then screenshot each slide with Playwright.
    return _playwright_fallback(deck_dir, out)


def _playwright_fallback(deck_dir: Path, out: Path) -> list[Path]:
    from playwright.sync_api import sync_playwright  # pip install playwright
    html = deck_dir / "build" / "index.html"          # produced by your build step
    if not html.exists():
        sys.exit("no built HTML; run the deck build first")
    pngs = []
    with sync_playwright() as p:
        # Ubuntu 23.10+: --no-sandbox avoids the "No usable sandbox" crash.
        # Prefer installing the chromium apparmor profile and dropping this arg.
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(
            viewport={"width": CANVAS[0], "height": CANVAS[1]},
            device_scale_factor=1)
        page.goto(html.as_uri())
        slides = page.locator(".slide")               # adjust to your slide selector
        for i in range(slides.count()):
            path = out / f"slide-{i + 1:02d}.png"
            slides.nth(i).screenshot(path=str(path))
            pngs.append(path)
        browser.close()
    return pngs


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/render.py decks/<name>")
    paths = render(Path(sys.argv[1]))
    print(f"rendered {len(paths)} slides")
