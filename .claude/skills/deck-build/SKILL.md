---
name: deck-build
description: Generate the deck source (slides.md) from a signed-off outline. Use
  after deck-outline and theme/tokens.css exist, before QA. Turns each outline
  slide into Slidev/Marp markup, applying the design-principles LAYOUT rules and
  consuming theme tokens only — never literal colors, sizes, or spacing. Content
  is frozen: it styles the spec, it does not rewrite it. Leaves image/diagram
  slides as placeholders for the image stage.
---

# Deck build — spec to source (implement)

The implement stage. Read the content-locked outline and the resolved tokens,
emit `decks/<name>/slides.md`. This is the STYLE pass of "draft first, style
last": the outline was the draft — here you apply the look, never the content.

## Inputs — read all, in order
- `decks/<name>/brief.md` — mode + throughline.
- `decks/<name>/outline.md` — the spec: one block per slide, already signed off.
- `decks/<name>/glossary.md` — exact terms/phrasings; do not reword them.
- `theme/tokens.css` — the resolved look (whatever brand is active).
If the outline is missing or unsigned, stop and route back to `deck-outline`.

## Two hard rules (these are what make QA meaningful)
1. **Tokens only.** Every color, font size, space, and line-height references a
   `var(--…)` from tokens.css. Zero literal hex / px / pt in slide styles. If a
   value you need isn't a token, STOP — that's a tokens.css gap, not a slide hack.
2. **Content is frozen.** Do not add, cut, reorder, merge, or reword slides, and
   do not alter glossary terms. If the outline looks wrong, flag it and route
   back — never fix it here. You style the spec; you don't rewrite it.

## Setup (once per deck) — branch on brief `format`

**Marp (default).**
- slides.md opens with frontmatter: `marp: true`, `theme: <deck-theme>`,
  `size: <deck-size>`, `paginate: true`. Slide separator is `---`. Speaker notes
  are plain HTML comments.
- The theme lives in its own file, `decks/<name>/theme.css` — NOT in an inline
  `<style>` block. It opens with `/* @theme <deck-theme> */` and
  `/* @size <deck-size> 1920px 1080px */`, `@import`s tokens.css, and defines ONE
  class per slide layout (`section.title`, `section.statement`, `section.quote`,
  `section.compare`, …), all styled with `var(--…)`. `render.py` registers it with
  `--theme-set`. **Marp only honours `@theme` and `@size` from a registered theme
  file** — put them in an inline `<style>` and they are silently ignored, the deck
  falls back to the 1280×720 default canvas, and every token calibrated for
  1920×1080 overflows and clips.
- Do not set `width`/`height` on `section`: `@size` owns the canvas.
- Per-slide layout = a `<!-- _class: <name> -->` directive. Slides carry only a
  class + content — never inline styles.

**Slidev (alt).**
- A global style imports tokens.css; each layout is a Vue layout component;
  per-slide `layout:` in frontmatter selects it; notes go in the trailing
  `<!-- … -->` block.

## Per-slide: map the outline `Type:` to a layout (values from tokens both ways)

| Type            | Marp (default)                               | Slidev (alt)          |
|-----------------|----------------------------------------------|-----------------------|
| title / divider | `<!-- _class: title -->` (dark sandwich)     | `layout: cover`       |
| statement       | `<!-- _class: statement -->`                 | `layout: center`      |
| chart           | `<!-- _class: split -->` or full             | `layout: two-cols`    |
| image           | `![bg brightness:.45](path)` (full-bleed+scrim) | `layout: image`    |
| diagram         | `<!-- _class: framed -->` + caption          | framed layout         |
| quote           | `<!-- _class: quote -->` (≥70% ws)           | `layout: quote`       |
| comparison      | `<!-- _class: compare -->` (cards on grid)   | cards on 12-col grid  |

## Apply at generation (the checkable rules)
- ≤4 type sizes per slide, drawn only from the token ramp.
- Exactly one accent moment per slide (`--accent`); everything else neutral.
- All spacing from the 8-pt token scale; `--slide-margin` safe-zone on every slide.
- Hit the whitespace target for the slide type; if content won't fit, the slide
  is overfull — flag it, never shrink type below the floor.
- Speaker notes carry the detail; presenter mode keeps the on-slide body ≤25 words.

## Images — do NOT generate them here
Leave typed image/diagram slides as explicit placeholders carrying: intended
treatment (full-bleed vs framed, scrim on/off), alt text, and a one-line brief of
what the visual should show. The image stage fills these once content is final.

## Output — then hand off, don't self-certify
Write `decks/<name>/slides.md` (plus any setup file) and list the slides left as
placeholders. Do NOT declare the deck done — pass to `deck-qa`, which renders
every slide and runs the numeric checks. Fix only what QA reports, then re-run QA.
(implement → review, kept separate on purpose.)
