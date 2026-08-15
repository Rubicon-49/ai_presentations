# power-deck

**Presentations as code.** A brief → outline → build → images → QA pipeline that turns codified design rules into automated pass/fail gates, so a generated deck is checked against numbers instead of vibes.

The premise: AI-generated decks look generic because design guidance lives in prose — advice a model can politely ignore. This project expresses the same guidance three times over, in forms that can actually be enforced:

| Layer | Where it lives | What it does |
|---|---|---|
| **Rules as numbers** | `references/design-principles.md` | 20 codified, sourced rules — every one a threshold, ratio, or if-X-then-Y |
| **Tokens as the look** | `theme/tokens.css` | those numbers expressed as CSS custom properties every slide reads from |
| **QA as the gate** | `scripts/*.py` | render the deck to PNGs and fail the build when a number is missed |

A rule that isn't a number can't be checked, so it doesn't make it in.

---

## Table of contents

- [How it works](#how-it-works)
- [Repository layout](#repository-layout)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [The pipeline stages](#the-pipeline-stages)
- [The quality gates](#the-quality-gates)
- [Design tokens](#design-tokens)
- [The golden deck](#the-golden-deck)
- [Branding a deck](#branding-a-deck)
- [Known limitations](#known-limitations)

---

## How it works

```
brief ──▶ outline ──▶ build ──▶ images ──▶ QA
  ▲          ▲                              │
  │          │                              │
 human    human                      automated pass/fail
sign-off  sign-off                    (loops until clean)
```

Five stages, three gates. The first two gates are human sign-offs — a wrong message in the brief wastes every stage after it, and the outline is the last cheap moment to change what the deck *says*. The final gate is automated and non-negotiable: the deck is not done until every check exits zero.

Two principles run through the whole thing:

- **Draft first, style last.** The outline locks content in plain Markdown with zero styling. The build stage applies the look and is forbidden from rewriting a single word.
- **Implement and review stay separate.** The stage that generates slides never certifies them. QA renders the slides to images and judges *those*, never the source markup.

---

## Repository layout

```
.
├── references/
│   └── design-principles.md    # 20 codified rules + ~75 numeric values (Appendix A)
├── theme/
│   └── tokens.css              # the rules as CSS custom properties — the brand swap point
├── scripts/
│   ├── render.py               # deck → build/slide-XX.png at 1920×1080
│   ├── check_contrast.py       # WCAG contrast gate (pixel-level)
│   ├── check_whitespace.py     # whitespace-ratio gate (pixel-level)
│   └── lint_slide.py           # word/size/accent/grid/token gate (source-level)
├── decks/
│   └── golden-deck/            # the worked reference deck
│       ├── brief.md            # audience, one message, mode, throughline
│       ├── glossary.md         # this deck's ubiquitous language
│       ├── outline.md          # the content-locked spec
│       ├── slides.md           # generated Marp source
│       ├── theme.css           # deck theme; imports tokens.css
│       └── build/slide-*.png   # rendered output, checked by QA
└── .claude/
    ├── commands/make-deck.md   # /make-deck — the orchestrator
    ├── skills/                 # one skill per stage
    │   ├── deck-brief/         │ deck-outline/  │ deck-build/
    │   └── deck-images/        │ deck-qa/
    └── examples/golden-deck/   # brief fixture used as a worked example
```

---

## Requirements

- **Python ≥ 3.13** — the checks are typed for modern Python.
- **[uv](https://docs.astral.sh/uv/)** — dependency management (`uv.lock` is committed).
- **[Marp CLI](https://github.com/marp-team/marp-cli)** — the default renderer, installed via npm.
- **Claude Code** — the pipeline stages are skills; the scripts run standalone without it.

Optional:

- **Slidev** — alternative renderer, selected by the deck's own frontmatter.
- **Tesseract** — only for `check_contrast.py --text-mask` (see [limitations](#known-limitations)).

---

## Installation

```bash
git clone git@github.com:Rubicon-49/ai_presentations.git
cd ai_presentations

# Python dependencies
uv sync

# Renderer
npm install -g @marp-team/marp-cli

# Optional: Playwright fallback renderer
uv run playwright install chromium

# Optional: OCR text-masking for the contrast check
uv sync --extra ocr
```

**Linux note.** On Ubuntu 23.10+ restricted user namespaces break headless Chromium. `render.py` passes `--no-sandbox` in the Playwright fallback path, but the cleaner fix is installing the AppArmor profile: `sudo apt-get install -y chromium`. Marp's own browser discovery works without any flags.

---

## Quick start

### With Claude Code (the intended path)

```
/make-deck my-deck
```

The orchestrator runs each stage in order, **stops** for your sign-off after the brief and after the outline, then builds, fills images, and loops QA until it exits clean. It delegates every stage to that stage's skill rather than inlining the work, so each stage's rules actually apply.

### Standalone (checking an existing deck)

The gates are ordinary Python and need no agent:

```bash
uv run python scripts/render.py           decks/golden-deck
uv run python scripts/check_contrast.py   decks/golden-deck/build
uv run python scripts/check_whitespace.py decks/golden-deck/build
uv run python scripts/lint_slide.py       decks/golden-deck
```

Each exits non-zero on failure, so a clean gate is three zero exits — which also makes them drop-in CI steps.

---

## The pipeline stages

### 1. `deck-brief` → **human gate**

Interrogates before it writes. Asks one question at a time — never batched — and pushes back on vague answers: "raise awareness" and "align the team" are not messages. Expect 8–15 questions filling seven required slots: audience, the one message, desired action, mode, throughline, constraints, and evidence on hand.

Applies stress tests as it goes. A message that needs an "and" is two messages. An audience that already believes the message needs a reason for the deck to exist. A claim with no evidence is flagged as a GAP, never papered over.

Writes `brief.md` and `glossary.md` — the deck's ubiquitous language, so wording doesn't drift downstream. **Stops for sign-off.**

### 2. `deck-outline` → **human gate**

Expands each throughline beat into one-idea-per-slide entries in plain Markdown — no styling, no Marp directives. Every slide traces to exactly one beat and cites its evidence or is flagged GAP.

Applies only *content*-level rules: split a slide carrying two claims, split a slide over its word budget. Typography, color, and layout are explicitly out of scope here. Slide titles must be claims ("Revenue grew 22%"), not topics ("Revenue"). **Stops for sign-off.**

### 3. Tokens *(only if needed)*

Skipped when `theme/tokens.css` is already the intended look. Otherwise resolves a brand file into tokens. No gate — tokens get verified implicitly when QA runs.

### 4. `deck-build`

Outline + tokens → `slides.md`. Two hard rules make QA meaningful downstream:

1. **Tokens only.** Every color, size, space, and line-height is a `var(--…)`. Zero literal hex/px/pt in slide styles. A value that isn't a token is a `tokens.css` gap, not a slide hack.
2. **Content is frozen.** No adding, cutting, reordering, merging, or rewording. If the outline looks wrong, flag it and route back — never fix it here.

Maps each outline `Type:` to a layout class, and leaves image/diagram slides as explicit placeholders carrying their intended treatment, alt text, and a one-line brief.

> **Marp gotcha, encoded in the skill:** `@theme` and `@size` are only honored from a theme file registered via `--theme-set`. Put them in an inline `<style>` block and they're silently ignored — the deck falls back to a 1280×720 canvas and every token calibrated for 1920×1080 overflows.

### 5. `deck-images`

Fills *only* the flagged placeholders. Diagrams are generated **as code, not pixels** — inline SVG or Mermaid styled from tokens, so they stay crisp, diffable in Git, and can't drift off-palette. Raster images are prompted toward the deck's accent family so a set reads as one visual family.

Text that belongs on the slide is never baked into an image — that would dodge the type and contrast rules.

### 6. `deck-qa` → **automated gate, loops**

Renders every slide, runs all three checks, then reviews on two axes: **design compliance** (automated) and **spec faithfulness** (judgment — does the slide still carry its beat's message, are glossary terms verbatim, is the detail in speaker notes rather than smuggled onto the slide).

Failures route back to their owning stage: design failures to build/images, spec failures to the outline. Re-render, re-check, repeat.

> If a check *cannot run* — missing dependency, missing script — the gate has **not** passed. A check that silently fails to execute is the one failure mode that makes every later "QA passed" claim false.

---

## The quality gates

### `check_contrast.py` — WCAG contrast, pixel-level

```bash
uv run python scripts/check_contrast.py <build-dir> [--aaa] [--text-mask]
```

Samples a 3×3 grid of interior cells per slide and computes WCAG relative luminance ratios. Default floor is AA body (4.5:1); `--aaa` raises it to 7:1. The tokens target AAA deliberately — projectors wash out contrast by 30–50%, so a 4.5:1 design lands at 2–3:1 on real hardware.

### `check_whitespace.py` — negative space, pixel-level

```bash
uv run python scripts/check_whitespace.py <build-dir> [--slides <slides.md>] [--json]
```

Measures the fraction of pixels matching the slide's background color against the floor for its type: **content ≥40%**, **hero/title/section ≥60%**, **quote ≥70%**. Slide types are read from `_class` directives in the source.

Two design decisions worth noting. Background color is the modal color of the slide's *outer edge*, not of the whole image — on an overfull slide the content is the majority color, so a whole-image mode names the content as background and reports the exact inverse of the truth. And the tolerance is deliberately tight (4 per channel): the neutral ramp puts `--surface` only 8/7/5 away from `--bg`, so a loose tolerance counts every card as empty and reports ~99% on a full slide.

### `lint_slide.py` — source-level design gate

```bash
uv run python scripts/lint_slide.py decks/<name> [--json]
```

Checks what's decidable from source:

| Check | Rule |
|---|---|
| `words` | word count vs mode budget (presenter 25 / document 75) and tighter per-type budgets (title 10, divider 8, quote 30) |
| `sizes` | ≤4 distinct type sizes per slide |
| `accent` | exactly one accent *device* per slide |
| `grid` | every spacing value on the 8-pt scale |
| `tokens` | no literal hex/px/pt in deck CSS |

The accent check counts *devices*, not declarations — a diagram's nodes, icon fill, icon stroke, and check mark are one accented idea, and a base rule plus its dark-mode override are the same span. Counting declarations would report six accents where a viewer sees one.

Speaker notes (HTML comments) and diagram labels inside `<svg>` are stripped before counting words — they aren't slide copy.

---

## Design tokens

`theme/tokens.css` is the single source of truth for the look. Every generated slide and every QA script reads from it, so changing a value once moves the whole deck.

- **Canvas** — 1920×1080, 16:9.
- **Spacing** — strict 8-pt scale (4…256). Slide margin 96px = the 5% edge safe-zone.
- **Type** — 6 sizes on a 1.333 modular ratio (84/64/36/28/20/16), ≤4 usable on any one slide. Body floor 28px, headline floor 48px.
- **Color** — 60-30-10 split, neutral ramp plus a single accent ramp — an "ember" orange (h≈18-21), deliberately not generic AI blue.

The tokens carry their own audit trail. Two values were moved to satisfy contrast over aesthetics, and the file says so inline:

```css
--footer-opacity: 0.75;   /* was 50–60%, which put 16px footer text at 3.9:1 —
                             below the 4.5:1 body floor. 0.75 → 7.6:1 ✓ AAA.
                             Contrast wins over the aesthetic band. */
--accent: var(--accent-700);  /* 7.4:1 ✓ AAA (was accent-600 at 4.9:1,
                                 which missed the 7:1 this deck advertises) */
```

---

## The golden deck

`decks/golden-deck/` is the worked reference — a 6-slide presenter-mode Marp deck that argues for the pipeline itself, built *by* the pipeline and passing its own gates. Every intermediate artifact is committed (`brief.md` → `glossary.md` → `outline.md` → `slides.md` → `build/*.png`), so you can read the full chain from one message to rendered pixels.

It's the most useful thing to read first: the brief's evidence line points at the exact files backing each claim, and the pipeline diagram on slide 5 is inline SVG styled entirely from tokens — the practice the `deck-images` skill preaches.

---

## Branding a deck

`tokens.css` marks its swap point explicitly:

```css
/* >>> BRAND SWAP POINT: to brand a deck, change only the two font names below
   and the accent ramp (--accent-*). Everything else is derived and gets
   verified by the QA contrast/whitespace checks at build. <<< */
```

Change the two font families and the accent ramp, then re-run QA. If a new accent misses the contrast floor, the gate says so with the measured ratio — which is the entire point of having the checks.

---

## Known limitations

Each check documents its own failure mode in its docstring. Summarized honestly:

**`check_contrast.py` has a miss bias in default mode.** Background and foreground per cell are approximated by the darkest and lightest pixels present. A cell containing *both* a high-contrast pair (a logo, a photo edge) *and* unreadable low-contrast text will PASS on the strength of the high-contrast pair. It is reliable as a floor for text on solid fills, and unreliable exactly where text overlays images. Use `--text-mask` (requires the `ocr` extra) on those slides. The bias is toward misses, not false alarms — so a PASS on an image slide is weaker evidence than a PASS on a text slide.

**`check_whitespace.py` fails full-bleed slides by construction.** A full-bleed photo has no modal background — the image *is* the slide — so the reported ratio is near zero. Correct for framed art, wrong for intentional full-bleed. Mark those slides `_class: bleed` and they're reported as SKIP, never silently passed.

**`lint_slide.py` approximates the CSS cascade.** It resolves which rules *could* apply to a slide from its `_class` directive and the tags/classes in its body, but doesn't implement specificity. A rule that matches structurally but loses the cascade is still counted. This biases toward false alarms rather than misses — the correct direction for a gate, but it means an occasional failure needs a human to overrule.

**The judgment axis is not automated.** Steps 3–5 of QA — spec faithfulness and visual review — need a reader. The numeric gate catches thresholds; it can't see an awkward line wrap, a focal point that isn't dominant, or a title softened from a claim into a topic.

---

## License

No license file yet — add one before treating this as reusable by others.
