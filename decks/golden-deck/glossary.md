# Glossary — golden-deck

Exact terms and phrasings for this deck. Use these verbatim; don't paraphrase.

- **make-deck** — the pipeline's name (lowercase, hyphenated, always this form
  — not "Make Deck" or "the deck maker").
- **the pipeline** — shorthand for the make-deck stage sequence once named once.
- **brief → outline → build → images → QA** — the five stages, always listed in
  this order, this wording (not "spec", not "generate", not "review").
- **design rules** — the codified rules in `references/design-principles.md`
  (not "guidelines", not "best practices" — this deck's claim is that they are
  rules, not suggestions).
- **rules as numbers** — the core mechanism: design-principles.md's 20 rules are
  thresholds/ratios, not prose advice.
- **tokens as the look** — the core mechanism: `theme/tokens.css` is the single
  source of the deck's visual values; nothing is hand-set.
- **QA as the gate** — the core mechanism: `deck-qa` renders and checks every
  slide against tokens.css before the deck can ship; QA is a pass/fail gate, not
  a suggestion pass.
- **the gate** / **sign-off** — a stage boundary that stops for human
  confirmation (brief, outline) or an automated pass/fail check (QA). Don't
  conflate the two kinds in the same slide.
- **token(s)** — a named design value in tokens.css (e.g. `--accent-600`,
  `--space-8`). Never "variable" or "style".
- **AAA contrast / 7:1** — the contrast target this deck's own tokens are tuned
  to; use as the concrete number when the deck needs a proof point.
- **8-pt grid** — the spacing system (all spacing is a multiple of 8px, 4px
  allowed for tight work).
- **presenter mode** — this deck's own mode: narrated live, ≤25 words per slide,
  detail lives in speaker notes. (Contrast: "document mode" — not used in this
  deck, don't reference unless explaining the distinction.)
- **ember** — the name of this deck's default accent ramp (an orange, not blue)
  in tokens.css; use when naming the deck's own look as a worked example.
