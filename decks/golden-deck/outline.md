# Outline — golden-deck

## Slide 1 — Codify the design rules and the pipeline enforces them for you
- Beat: 1 (title / frame)
- Type: title
- Content:
  Eyebrow: "make-deck"
  Headline: "Codify the design rules and the pipeline enforces them for you."
- Evidence: brief.md, one message (verbatim)
- Note: State this once, live, as the whole point of the talk. Everything after
  is proof.

## Slide 2 — AI decks look generic because the rules live in prose
- Beat: 1 (the problem)
- Type: statement
- Content:
  "AI decks look generic because the rules live in prose."
- Evidence: brief.md, throughline beat 1 (deck's stated premise — the thesis
  being argued, not an external data claim)
- Note: "Prose" means design advice written as guidance a model can politely
  ignore, not enforce. Set up the contrast for slide 3.

## Slide 3 — The fix is three enforced mechanisms, not more advice
- Beat: 2 (the fix)
- Type: comparison
- Content:
  Three cards, one phrase each (glossary terms, verbatim):
  "Rules as numbers." · "Tokens as the look." · "QA as the gate."
- Evidence: brief.md throughline beat 2; glossary.md (exact phrasing)
- Note: Narrate what each phrase cashes out to — rule → token → check. Slide 4
  makes "rules as numbers" concrete.

## Slide 4 — The rules are numbers, not adjectives
- Beat: 2 (the fix, made concrete)
- Type: comparison
- Content:
  Three thresholds, no framing text:
  "≥7:1 contrast (AAA)" · "8-pt spacing grid" · "≤4 type sizes per slide"
- Evidence: references/design-principles.md rules #6 (type scale), #7 (max 4
  sizes), #11 (WCAG contrast), #15 (8-pt grid); theme/tokens.css (same
  thresholds as token values)
- Note: These are the actual numbers deck-qa checks against — not a curated
  sample, the same values live in tokens.css and get read by
  scripts/check_contrast.py.

## Slide 5 — Five stages, two human gates, one automated gate
- Beat: 3 (the pipeline)
- Type: diagram
- Content:
  Flow: "brief → outline → build → images → QA"
  Two annotations: "brief, outline: human sign-off" / "QA: automated pass/fail"
- Evidence: brief.md throughline beat 3; glossary.md (exact stage order and
  wording); .claude/skills/deck-qa/SKILL.md, deck-build/SKILL.md (gate
  mechanics: sign-off vs. automated check)
- Note: Distinguish the two gate kinds explicitly — this is the "the gate"
  glossary term. Don't let the audience assume QA is a suggestion pass.

## Slide 6 — Run make-deck on your next deck
- Beat: 4 (the ask)
- Type: statement
- Content:
  "Run make-deck on your next deck."
- Evidence: brief.md, desired action (verbatim)
- Note: Closing slide, dark sandwich per tokens.css. This is the single ask —
  land it and stop talking.
