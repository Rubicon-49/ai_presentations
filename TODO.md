# Roadmap — trustworthy gates

Three improvements identified 2026-08-15, ordered by dependency. Each undermines
the project's own thesis ("encode rules as checks you can trust") until fixed.

Start with #1 — it is the precondition for changing #2 with any confidence.

---

## 1. Test the checkers

**Problem.** `pyproject.toml` declares `pytest>=8.3` in the dev group; there are
zero test files. Every check is a heuristic with a non-obvious failure mode, and
none is pinned down by an assertion. A silent regression in `background_colour()`
turns every whitespace PASS into noise and nothing notices.

**Highest-value units to cover:**

| Function | File | Why it needs pinning |
|---|---|---|
| `background_colour()` | `scripts/check_whitespace.py:88` | edge-modal sampling; correct only if the slide respects the margin rule |
| `background_ratio()` | `scripts/check_whitespace.py:107` | TOLERANCE=4 is load-bearing — a loose value reports ~99% on a full slide |
| `slide_classes()` / `slide_type()` | `scripts/check_whitespace.py:54,75` | regex Marp parsing incl. frontmatter stripping |
| `luminance()` / `ratio()` | `scripts/check_contrast.py:32,40` | WCAG math; test against known published pairs |
| `accent_device_key()` | `scripts/lint_slide.py:113` | three regex fallbacks collapsing selectors to a component |
| `rule_applies()` | `scripts/lint_slide.py:94` | hand-rolled partial CSS selector matcher |
| `visible_words()` | `scripts/lint_slide.py:63` | must strip notes, SVG labels, tags, entities |
| `split_slides()` | `scripts/lint_slide.py:49` | frontmatter + fence splitting |

**Fixtures are already committed** — `decks/golden-deck/build/slide-*.png` and
`decks/golden-deck/slides.md`, with known-good expected values. Add small
synthetic PNGs (solid fill, half-covered, low-contrast pair) for edge cases.

**Done when:** `uv run pytest` passes, covers every function above including its
documented failure mode, and a deliberately broken tolerance/threshold makes a
test go red.

---

## 2. Make the contrast gate mean what the deck claims

Two compounding problems.

**2a. Default mode is structurally near-unfailable.**
`scripts/check_contrast.py:105-109` takes each cell's lightest and darkest pixel
as bg/fg. A cell fails only if its *entire* dynamic range is under the floor —
so one dark pixel (pagination number, SVG stroke, icon) rescues the cell, and
low-contrast body text beside a black headline passes at 21:1. The docstring is
honest about this (lines 14-18), but the mitigation `--text-mask` sits behind an
optional extra that `uv sync` does not install.

Options, roughly increasing cost:
- promote `pytesseract` from the `ocr` extra to a main dependency and make
  text-masking the default path
- segment text by connected components instead of OCR (no Tesseract dependency)
- keep the coarse mode but make it fail loudly — and non-zero — when it cannot
  find a defensible text/background split on a slide that contains text

**2b. The gate runs at the wrong floor.**
`theme/tokens.css:57` says design to AAA (7:1), and two token values were moved
specifically to hit it (`--footer-opacity`, `--accent`). But
`.claude/skills/deck-qa/SKILL.md:27` invokes the check bare, so
`check_contrast.py:124` falls through to the 4.5:1 AA floor. The AAA the deck
advertises on slide 4 is never enforced. Fixing this is one flag; do it with 2a,
not before — raising the floor on a check that cannot fail changes nothing.

**Done when:** a slide with genuinely low-contrast text FAILS by default, with a
regression test proving it, and the QA skill enforces the floor the tokens claim.

---

## 3. Run the gates in CI

The three scripts are already ideal CI steps — clean argv, non-zero exit on
failure, `--json` on two of them. The golden deck and its rendered PNGs are
committed. There is no workflow.

Now that the repo is public this is also the most persuasive addition: a green
check per push, proving the pipeline passes its own gates. "QA as the gate" is
currently a claim the reader must reproduce locally to believe.

**Not a five-liner** — CI needs the Marp CLI and a headless browser. Sequence:
`uv sync` → `npm i -g @marp-team/marp-cli` → `render.py decks/golden-deck` →
the three checks. Consider caching npm + uv, and decide whether CI re-renders
the PNGs or checks the committed ones (re-rendering also guards against renderer
drift, but needs the browser).

**Done when:** a push runs render + all three gates against the golden deck, and
a deliberately broken token turns the build red.

---

## Runners-up (not in scope above)

- `scripts/check_whitespace.py:69` keeps empty slide chunks when mapping types
  while `scripts/lint_slide.py:232` skips them — a stray blank chunk misaligns
  slide types in one script but not the other. Only warns when counts disagree.
- `scripts/lint_slide.py:164` takes an `idx` parameter it never uses.
- No `LICENSE` file. Public repo with default copyright = nobody may reuse it.
- Three names for one project: directory `ai_expert_user`, GitHub repo
  `ai_presentations`, `pyproject.toml` name `power-deck`.
