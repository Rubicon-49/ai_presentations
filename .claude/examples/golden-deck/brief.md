# Brief — golden-deck (reference)

- Audience: internal engineers, already bought-in, want the shape not the sell.
- One message: "Codify the design rules and the pipeline enforces them for you."
- Desired action: adopt the make-deck workflow for their next deck.
- Mode: presenter
- Throughline:
  1. The problem — AI decks look generic because rules live in prose.
  2. The fix — rules as numbers, tokens as the look, QA as the gate.
  3. The pipeline — brief → outline → build → images → QA.
  4. The ask — run make-deck on your next deck.
- Constraints: format marp; ~6 slides; no brand, use default ember tokens.
- Evidence: `references/design-principles.md` (20 codified, sourced rules — the
  "rules as numbers" claim); `theme/tokens.css` (the rules expressed as tokens —
  the "tokens as the look" claim); `scripts/check_contrast.py` +
  `scripts/render.py` (the "QA as the gate" claim, automated not manual).
