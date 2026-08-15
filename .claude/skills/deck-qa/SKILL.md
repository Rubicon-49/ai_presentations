---
name: deck-qa
description: Review a built deck against the design rules AND the brief before it
  ships. Use after deck-build, on any slides.md. Renders every slide to an image,
  runs the numeric checks (contrast, whitespace, word/size/accent budgets), then
  does a dual-axis review — design compliance + faithfulness to brief/outline.
  Reports failures per slide; the deck is not done until every check passes.
---

# Deck QA — the review gate (tests before done)

Runs after deck-build. A deck is DONE only when it renders clean on both axes.
Never certify from the source markup — certify from the rendered images.

## Inputs
- `decks/<name>/slides.md` — the built deck.
- `decks/<name>/brief.md`, `outline.md`, `glossary.md` — the spec to check against.
- `theme/tokens.css` — the same tokens the generator used (thresholds derive here).

## Step 1 — render every slide to an image
Run `scripts/render.py decks/<name>` → writes `build/slide-XX.png` per slide
(1920×1080). All numeric checks run on these PNGs, not the markup.

## Step 2 — Axis A: design compliance (automated)
Run all three; each exits non-zero on failure, so a clean gate is three zero exits.

    python scripts/check_contrast.py   decks/<name>/build
    python scripts/check_whitespace.py decks/<name>/build
    python scripts/lint_slide.py       decks/<name>

- `check_contrast.py` — text vs background ≥ the mode's ratio at ≥9 sample points
  (target AAA 7:1; hard-fail below AA). Read its LIMITATION note before trusting a
  PASS on any slide with text over an image — use `--text-mask` there.
- `check_whitespace.py` — background-pixel ratio ≥ floor for the slide type
  (content 40 / hero 60 / quote 70). Reads slide types from the `_class`
  directives; mark deliberate full-bleed slides `_class: bleed` to skip them.
- `lint_slide.py` — parses the slide source and `decks/<name>/theme.css`: word
  count vs mode/slide-type budget, ≤4 type sizes, exactly 1 accent device,
  spacing on the 8-pt scale, every value a token (no literal hex/px).
Collect every failure with slide number, check, expected, actual.

These three are the whole automated axis. If one cannot run — missing dependency,
missing script — the gate has NOT passed; say so and fix the tooling first. A
check that silently fails to execute is the one failure mode that makes every
later "QA passed" claim false.

## Step 3 — Axis B: spec faithfulness (judgment, per slide)
Automated checks can't see meaning. For each slide, confirm:
- It maps to its outline beat and carries that beat's single message.
- Title is still the claim the outline specified (not softened to a topic).
- Glossary terms are used verbatim; no drifted wording.
- Presenter mode: the detail lives in speaker notes, not smuggled onto the slide.
- Placeholders from deck-build are resolved or still correctly flagged.

## Step 4 — visual review (judgment, on the PNGs)
Look at each rendered slide. Numbers pass but the eye still catches: awkward line
wraps, a focal point that isn't dominant, a chart that reads wrong, collisions the
pixel checks missed. Flag these as review notes.

## Step 5 — report, don't silently fix
Emit a QA report: per slide, PASS or the list of failures across both axes.
Then fix ONLY what's reported — design failures in slides.md (never below a token
floor; if unfixable, it's a tokens.css or outline problem, route back), spec
failures back through the owning stage. Re-render, re-run, repeat until clean.
Never edit a PNG to pass a check.
