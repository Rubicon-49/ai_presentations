---
name: deck-brief
description: Interrogate and lock a presentation brief before any slides are
  written. Use at the very start of any deck / slides / presentation request —
  clarifies audience, the single core message, presenter-vs-document mode, and
  the throughline, then writes brief.md and a terms glossary. Blocks slide
  generation until the brief is signed off.
---

# Deck brief — grill first, build later

This is the alignment gate. Do NOT write an outline or any slides until
`brief.md` exists and the user has signed off on it. Stress-test the thinking
first, capture it, then hand a locked brief to the outline stage.

## How to run
Ask ONE question at a time — do not batch. Push back on vague answers:
"raise awareness", "share results", "align the team" are not messages. Make the
user name the specific claim and the specific action they want. Keep going until
every slot below is filled and unambiguous. Expect 8–15 questions.

## Slots to fill (all required)
- **Audience** — who exactly is in the room, what do they already know/believe,
  and what's their disposition (skeptical, bought-in, hostile, uninformed)?
- **The one message** — the single sentence the audience should repeat
  afterward. If it needs an "and", it's two messages — pick one or split the deck.
- **Desired action** — what should they DO or DECIDE as a result? No action =
  it's a document, not a talk; say so if that's the case.
- **Mode** — presenter (live, you narrate, ≤25 words/slide) or document (read
  alone, denser, every slide has a headline). Gates every downstream design rule.
- **Throughline** — the spine in 3–5 beats (e.g. problem → evidence →
  implication → ask). Each beat becomes a section.
- **Constraints** — time slot, rough slide budget, format (Slidev|Marp),
  brand rules, must-include / must-avoid.
- **Evidence on hand** — data, charts, quotes, or source docs that already
  support the message. Note gaps to fill later; don't invent support.

## Stress tests (apply while grilling)
- Message unsayable in one sentence without "and" → two messages.
- Audience already believes the message → ask what the deck is FOR.
- Desired action missing → surface one, or explicitly mark the deck informational.
- Supporting claim with no evidence → flag as a gap, don't paper over it.

## Output — write these, then STOP for sign-off
1. `decks/<name>/brief.md` — the seven slots, with the throughline as a numbered
   beat list.
2. `decks/<name>/glossary.md` — the ubiquitous language of THIS deck: exact
   terms, names, and preferred phrasings for the core concepts, one per line, so
   the outline and slides don't drift in wording.

End the turn after writing these. `deck-outline` reads `brief.md` — do not
proceed to it without the user confirming the brief is right.
