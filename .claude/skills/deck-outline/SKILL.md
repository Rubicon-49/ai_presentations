---
name: deck-outline
description: Convert a signed-off deck brief into a content-locked outline (the
  deck's spec). Use after deck-brief and before any slides are generated. Expands
  the throughline beats into one-idea-per-slide entries in plain Markdown — no
  styling, no Slidev/Marp directives — with every slide traced to a beat and its
  evidence noted. Blocks generation until the outline is signed off.
---

# Deck outline — brief to spec, content locked

Runs after `deck-brief`. Turns a signed-off `brief.md` into `outline.md`: the
deck's content spec, one idea per slide, in plain Markdown with zero styling.
This is the "draft first, style last" gate — lock what every slide SAYS before
anything decides how it looks. Do not generate slides, apply a theme, or add
Slidev/Marp markup here.

## Inputs — read both first
- `decks/<name>/brief.md` — the seven slots and the numbered throughline beats.
- `decks/<name>/glossary.md` — the deck's ubiquitous language; use these exact
  terms and phrasings so wording doesn't drift.

If either is missing or unsigned, stop and route back to `deck-brief`.

## How to run
Expand each throughline beat into a sequence of slides, one idea per slide, in
plain text — headlines and body as words, not markup. Respect the mode from the
brief:
- **presenter**: ≤25 words of on-slide content per slide; the detail lives in
  speaker-note seeds, not on the slide.
- **document**: every slide needs a headline; denser body allowed, still one idea.

Apply only the CONTENT-level rules from the slide-design reference: one idea per
slide; split a slide if it carries two claims, needs two headline-worthy points,
or busts the word budget. Do NOT apply typographic, color, spacing, or layout
rules — those belong to generation.

## Output — `decks/<name>/outline.md`, one block per slide, in order

    ## Slide N — <the slide's single message, as a claim, not a topic>
    - Beat: <which throughline beat this serves>
    - Type: title | statement | chart | image | diagram | quote | comparison | section-divider
    - Content:
      <the actual on-slide words / data points / bullet text, plain>
    - Evidence: <source ref from the brief, or GAP: needs …>
    - Note: <speaker-note seed or intent — optional>

Title, section dividers, and a closing slide count as slides — include them.

## Self-check before writing (fix, don't skip)
- Every beat has ≥1 slide; every slide maps to exactly one beat.
- Slide titles are claims ("Revenue grew 22%"), not topics ("Revenue").
- No slide carries two ideas — split any that do.
- Presenter mode: no slide over budget. Document mode: no slide without a headline.
- Every supporting claim cites evidence or is flagged GAP — never invent data.
- Slide count within the brief's budget; if over, propose cuts, don't cram.

End the turn after writing `outline.md`, and surface any GAPs and proposed cuts
for sign-off. Generation reads this file — do not proceed without confirmation.

For a large, multi-session deck, optionally break the signed-off outline into
per-section work items before generating — the `to-tickets` analog.
