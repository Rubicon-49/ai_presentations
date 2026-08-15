#!/usr/bin/env python3
"""lint_slide.py — source-level design gate for a built deck.

Usage:
    python scripts/lint_slide.py decks/<name> [--json]

Checks each slide in decks/<name>/slides.md against the codified rules that are
decidable from source (the pixel-level rules live in check_contrast.py and
check_whitespace.py):

  words     word count vs the brief's mode budget      [design-principles #20, §8]
  sizes     <=4 distinct type sizes per slide          [#7]
  accent    exactly one accent device per slide        [#13]
  grid      every spacing value on the 8-pt scale      [#15]
  tokens    no literal hex / px / pt in deck CSS       [deck-build rule 1]

The deck's own theme.css is linted for `grid` and `tokens`; theme/tokens.css is
NOT — that file is where the literals are supposed to live.

CSS matching is approximate by design: it resolves which rules could apply to a
slide from its `_class` directive and the tags/classes present in its body. It
does not implement the cascade, so a rule that matches structurally but loses to
specificity is still counted. That biases toward false alarms rather than misses,
which is the correct direction for a gate.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Word budgets, from design-principles.md §8 "Glanceable Comprehension". The
# per-type budgets are tighter than the mode default and win where they apply.
WORD_BUDGET = {"presenter": 25, "document": 75}
TYPE_BUDGET = {"title": 10, "divider": 8, "section": 8, "quote": 30, "closing": 10}
MAX_TYPE_SIZES = 4
GRID = 8                             # 8-pt scale; 4px allowed for tight icon work
GRID_EXCEPTIONS = {0, 4}

SPACING_PROPS = ("margin", "padding", "gap", "top", "right", "bottom", "left",
                 "width", "height", "inset")
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
LENGTH = re.compile(r"(?<![\w-])(\d+(?:\.\d+)?)(px|pt)\b")
COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


# ---------- deck source ----------

def split_slides(md: str) -> list[str]:
    """Slide bodies from a Marp markdown file, frontmatter removed."""
    if md.startswith("---"):
        end = md.find("\n---", 3)
        if end != -1:
            md = md[end + 4:]
    return re.split(r"^---\s*$", md, flags=re.MULTILINE)


def slide_classes(chunk: str) -> list[str]:
    m = re.search(r"<!--\s*_class:\s*([^>]*?)-->", chunk)
    return m.group(1).split() if m else []


def visible_words(chunk: str) -> list[str]:
    """On-slide words only: HTML comments are speaker notes and don't count."""
    body = re.sub(r"<!--.*?-->", " ", chunk, flags=re.DOTALL)   # notes + directives
    body = re.sub(r"<svg.*?</svg>", " ", body, flags=re.DOTALL)  # diagram labels aren't slide copy
    body = re.sub(r"<[^>]+>", " ", body)                    # tags
    body = re.sub(r"[#*`>|]", " ", body)                    # md syntax
    body = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", body)         # entities
    return [w for w in body.split() if any(c.isalnum() for c in w)]


def present_names(chunk: str) -> set[str]:
    """Tags and classes appearing in the slide body, for CSS applicability."""
    names = set(re.findall(r"<\s*([a-zA-Z][\w-]*)", chunk))
    for attr in re.findall(r'class\s*=\s*"([^"]*)"', chunk):
        names.update(attr.split())
    if re.search(r"^\s*#\s", chunk, re.MULTILINE):
        names.add("h1")
    if re.search(r"^\s*##\s", chunk, re.MULTILINE):
        names.add("h2")
    return names


# ---------- css ----------

def parse_css(css: str) -> list[tuple[str, str]]:
    """Flat list of (selector, declaration-block). Nested at-rules are skipped."""
    css = COMMENT.sub("", css)
    css = re.sub(r"@import[^;]*;", "", css)
    return [(sel.strip(), body) for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css)]


def rule_applies(selector: str, classes: set[str], names: set[str]) -> bool:
    """Could this selector match an element on a slide with these classes/tags?"""
    for part in selector.split(","):
        part = part.strip()
        if not part:
            continue
        # section-level classes must be classes the slide actually carries
        sect = re.match(r"section((?:\.[\w-]+)+)", part)
        if sect and not set(sect.group(1).lstrip(".").split(".")) <= classes:
            continue
        rest = part[sect.end():] if sect else re.sub(r"^section", "", part)
        rest = re.sub(r"::?[\w-]+(\([^)]*\))?", "", rest)   # drop pseudos
        need_cls = set(re.findall(r"\.([\w-]+)", rest))
        need_tag = set(re.findall(r"(?:^|[\s>+~])([a-zA-Z][\w-]*)", rest))
        if need_cls <= (classes | names) and need_tag <= names:
            return True
    return False


def accent_device_key(selector: str) -> str:
    """Name the visual device a selector accents, so one device counted once.

    Rule 13 limits accent *moments*, not declarations. A single device is
    routinely expressed across several rules — a diagram's nodes, icon fill,
    icon stroke and check mark are one accented idea, and a base rule plus its
    dark-mode override are the same span — so counting declarations reports a
    slide as having six accents when a viewer sees two. Key on the outermost
    component instead: the first class after the section qualifier.
    """
    part = selector.split(",")[0].strip()
    part = re.sub(r"^section(?:\.[\w-]+)*", "", part)
    part = re.sub(r"::?[\w-]+(\([^)]*\))?", "", part)
    m = re.search(r"\.([\w-]+)", part)
    if m:
        return m.group(1)
    sect = re.match(r"section((?:\.[\w-]+)+)", selector.strip())
    return sect.group(1) if sect else part.strip() or selector.strip()


def decls(block: str) -> list[tuple[str, str]]:
    out = []
    for d in block.split(";"):
        if ":" in d:
            prop, val = d.split(":", 1)
            out.append((prop.strip().lower(), val.strip()))
    return out


# ---------- checks ----------

def lint_css_literals(css_path: Path) -> list[str]:
    """`tokens` + `grid`: deck CSS must reference tokens and stay on the scale."""
    fails = []
    for sel, block in parse_css(css_path.read_text(encoding="utf-8")):
        for prop, val in decls(block):
            if HEX.search(val):
                fails.append(f"tokens: literal colour in `{sel} {{ {prop}: {val} }}` "
                             f"— every colour must be a var(--…)")
            for num, unit in LENGTH.findall(val):
                n = float(num)
                if prop.startswith(SPACING_PROPS) or "font-size" in prop:
                    fails.append(f"tokens: literal {num}{unit} in `{sel} {{ {prop} }}` "
                                 f"— use a token")
                if prop.startswith(SPACING_PROPS) and n not in GRID_EXCEPTIONS \
                        and n % GRID:
                    fails.append(f"grid: {num}{unit} in `{sel} {{ {prop} }}` "
                                 f"is off the {GRID}-pt scale")
    return fails


def lint_slide(chunk: str, idx: int, css_rules, mode: str) -> list[str]:
    classes, names = set(slide_classes(chunk)), present_names(chunk)
    fails = []

    # --- words ---
    budget, label = WORD_BUDGET.get(mode), mode
    for c in classes:
        if c in TYPE_BUDGET and (budget is None or TYPE_BUDGET[c] < budget):
            budget, label = TYPE_BUDGET[c], f"{c} slide"
    words = visible_words(chunk)
    if budget and len(words) > budget:
        fails.append(f"words: {len(words)} on-slide words, {label} budget is {budget}")
    if mode == "document" and not (names & {"h1", "h2"}):
        fails.append("words: document mode requires a headline on every slide")

    # --- sizes / accent, over the rules that can reach this slide ---
    sizes, accent_devices = set(), set()
    for sel, block in css_rules:
        if not rule_applies(sel, classes, names):
            continue
        for prop, val in decls(block):
            if prop == "font-size":
                sizes.add(val.strip())
            if "--accent" in val:
                accent_devices.add(accent_device_key(sel))
    if len(sizes) > MAX_TYPE_SIZES:
        fails.append(f"sizes: {len(sizes)} type sizes ({', '.join(sorted(sizes))}), "
                     f"max {MAX_TYPE_SIZES}")
    if len(accent_devices) != 1:
        fails.append(f"accent: {len(accent_devices)} accent device(s), expected exactly 1"
                     + (f" — {', '.join(sorted(accent_devices))}" if accent_devices else ""))
    return fails


def deck_mode(brief: Path) -> str:
    if brief.exists():
        m = re.search(r"^\s*[-*]?\s*\**Mode\**\s*[:—-]\s*(\w+)", brief.read_text(encoding="utf-8"),
                      re.MULTILINE | re.IGNORECASE)
        if m:
            return m.group(1).lower()
    return "presenter"


def main():
    ap = argparse.ArgumentParser(description="Source-level design gate for a deck.")
    ap.add_argument("deck_dir", type=Path, help="decks/<name>")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    slides_md = args.deck_dir / "slides.md"
    if not slides_md.exists():
        sys.exit(f"no slides.md in {args.deck_dir}")
    mode = deck_mode(args.deck_dir / "brief.md")

    theme = args.deck_dir / "theme.css"
    css_rules = parse_css(theme.read_text(encoding="utf-8")) if theme.exists() else []

    results, bad = [], False
    if theme.exists():
        css_fails = lint_css_literals(theme)
        bad |= bool(css_fails)
        results.append({"scope": theme.name, "failures": css_fails})
        print(f"{'FAIL' if css_fails else 'PASS'} {theme.name}"
              + ("" if not css_fails else f": {len(css_fails)} issue(s)"))
        for f in css_fails:
            print(f"  - {f}")

    for i, chunk in enumerate(split_slides(slides_md.read_text(encoding="utf-8")), 1):
        if not chunk.strip():
            continue
        fails = lint_slide(chunk, i, css_rules, mode)
        bad |= bool(fails)
        results.append({"scope": f"slide-{i:02d}", "failures": fails})
        print(f"{'FAIL' if fails else 'PASS'} slide-{i:02d}"
              + ("" if not fails else f" ({mode})"))
        for f in fails:
            print(f"  - {f}")

    if args.json:
        print(json.dumps(results, indent=2))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
