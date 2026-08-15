---
name: deck-images
description: Fill the image and diagram placeholders a built deck left behind. Use
  after deck-build, once content and layout are locked, before final QA. Generates
  or sources each visual on-theme from tokens, writes it into the deck's assets/,
  wires it into slides.md with the intended treatment (full-bleed + scrim, or
  framed), then hands back to deck-qa. Never invents visuals for un-flagged slides.
---

# Deck images — fill the placeholders (late, on-theme)

Runs after deck-build, before final QA. Resolve ONLY the slides deck-build marked
as image/diagram placeholders. Do not add visuals to slides that weren't flagged,
and do not touch text, layout, or the outline — content is locked.

## Inputs
- `decks/<name>/slides.md` — the built deck, with PLACEHOLDER markers.
- `decks/<name>/brief.md`, `glossary.md` — subject matter + exact terms for labels.
- `theme/tokens.css` — the palette/fonts every generated visual must match.
Collect the placeholder list first (each carries: treatment, alt text, one-line
brief). If there are none, report that and stop.

## Per placeholder — decide type, then produce
Use the outline `Type:` the placeholder came from:
- **diagram** (flow, structure, relationship) → generate as **code, not pixels**:
  a Mermaid block or an SVG authored with token colors (`--accent`, `--ink`,
  `--neutral-*`) and `--font-body`. Vector stays crisp at 1920×1080, is diffable
  in Git, and can't drift off-palette. Prefer this for anything schematic.
- **image** (photo, texture, mood) → generate/source a raster into `assets/`.
  Generate via the available image tool (e.g. mcp-image) with a prompt that names
  the deck's accent hue and mood so a set of images reads as one family. Target
  ≥1920px on the long edge; never upscale a small source.

## On-theme rules (all visuals)
- Colors come from tokens — diagram strokes/fills use `var(--…)`; generated images
  are prompted toward the accent family, not generic stock palettes.
- One visual language per deck: same diagram stroke weight, same corner radius,
  same illustration style. Carry it across every generated asset.
- Never bake text that belongs on the slide INTO an image (it dodges the type and
  contrast rules). Labels inside diagrams are fine; slide copy stays as slide copy.

## Wire into Marp (and Slidev)
Replace each placeholder with the real reference, keeping the treatment it specified:
- full-bleed image + overlay text → `![bg brightness:.45](assets/<file>)` (the
  brightness scrim is what lets headline text clear contrast over the photo).
- framed image → standard `![alt](assets/<file>)` inside the slide's layout class.
- diagram → inline Mermaid/SVG in the slide body, framed per its layout class.
  Marp Core escapes tags outside its default allowlist, and `<svg>` is not on it:
  without raw HTML enabled the whole diagram renders as literal source text on the
  slide. `render.py` passes `--html` for this reason — if you render Marp by hand,
  pass it too, and check the diagram slide's PNG rather than assuming.
  Style the SVG from the theme (`.diagram …` classes using `var(--…)`); a
  `font-size`/`fill` written inline is a literal and `lint_slide.py` will fail it.
- Slidev: `layout: image` with `image:` for full-bleed; components for diagrams.
Keep every non-color value on the token scale; keep alt text on every asset.

## Then re-run QA — do not self-certify
A filled image can fail exactly the checks an empty placeholder passed:
- text over a new photo can drop below the contrast floor → the scrim brightness
  is the knob; darken it, don't move the text off-grid.
- a busy full-bleed image can push the slide under its whitespace floor.
Run `scripts/render.py` then the checks (or the `deck-qa` skill). Fix by adjusting
the scrim / crop / asset, never the locked layout. Re-render, re-check, repeat.

## Output
Assets in `decks/<name>/assets/`, slides.md updated in place, placeholder list
cleared. Hand back to deck-qa for the final gate.
