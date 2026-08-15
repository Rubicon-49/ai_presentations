---
description: Run the full deck pipeline — brief → outline → tokens → build →
  images → QA — pausing for sign-off after the brief and the outline. Use to
  produce a finished, checked deck from a standing start.
argument-hint: <deck-name>
---

# make-deck — orchestrate the pipeline

Produce a finished, QA-passing deck named `$1` by running the stage skills in
order. You are the conductor: invoke each skill, enforce the gates, and STOP where
a human sign-off is required. Do not do a stage's work yourself — delegate to its
skill so its rules apply.

## Preflight
- Confirm `theme/tokens.css` exists (or a `theme/brands/<name>.md` to resolve
  from). If neither, stop and say so.
- Create `decks/$1/` if absent. If `decks/$1/slides.md` already exists, ask
  whether to resume or overwrite before touching anything.

## Stage 1 — Brief  →  GATE
Invoke `deck-brief` for `decks/$1`. It grills, then writes `brief.md` + `glossary.md`.
**STOP.** Show the brief and ask the user to confirm or revise. Do not proceed to
the outline until they sign off. (A wrong message here wastes every later stage.)

## Stage 2 — Outline  →  GATE
Invoke `deck-outline`. It writes the content-locked `outline.md` and surfaces GAPs
and any proposed cuts.
**STOP.** Show the outline; get sign-off. This is the last cheap moment to change
what the deck says — after this, edits mean re-running build/images/QA.

## Stage 3 — Tokens (only if needed)
If `theme/tokens.css` is already the intended look, skip. If resolving a brand,
run the resolve step for the brief's chosen `brands/<name>.md` → `tokens.css`.
No gate — tokens are checked implicitly when QA runs.

## Stage 4 — Build
Invoke `deck-build`. Outline + tokens → `slides.md` (Marp by default, per the
brief's `format`). Note which slides it leaves as image/diagram placeholders.

## Stage 5 — Images
If Stage 4 left placeholders, invoke `deck-images` to fill them on-theme into
`assets/` and wire them in. If none, skip.

## Stage 6 — QA  →  LOOP
Invoke `deck-qa`: `scripts/render.py decks/$1`, then the checks, then the dual-axis
review. If anything fails, route each failure to its owning stage (design →
build/images; spec → outline), fix, and re-run QA. Repeat until clean.
**Do not report the deck done until QA exits clean on both axes.**

## Done
Report: path to `decks/$1/slides.md`, the rendered `build/slide-XX.png` set, and a
one-line QA summary (slides checked, all passing). Point the user at the build.

## Rules
- Delegate every stage to its skill; never inline a stage's logic here.
- Never skip a GATE. The brief and outline sign-offs are the point of the pipeline.
- Never skip QA or self-certify. render → check → fix → re-check is the contract.
- On any stage error, stop at that stage and report — don't limp forward.
