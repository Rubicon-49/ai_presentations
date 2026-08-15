---
marp: true
theme: golden-deck
size: golden
paginate: true
---

<!-- _class: title -->

<p class="eyebrow">make-deck</p>

# Codify the design rules and the pipeline enforces them for you.

<!-- State this once, live, as the whole point of the talk. Everything after is proof. -->

---

<!-- _class: statement -->

# AI decks look generic because the rules live in <span class="accent">prose</span>.

<!-- "Prose" means design advice written as guidance a model can politely ignore, not enforce. Set up the contrast for the next slide. -->

---

<!-- _class: compare -->

<div class="cards">
<div class="card"><p>Rules as numbers.</p></div>
<div class="card"><p>Tokens as the look.</p></div>
<div class="card"><p>QA as the gate.</p></div>
</div>

<!-- Narrate what each phrase cashes out to — rule → token → check. The next slide makes "rules as numbers" concrete. -->

---

<!-- _class: compare -->

<div class="cards">
<div class="card"><p>&ge;7:1 contrast (AAA)</p></div>
<div class="card"><p>8-pt spacing grid</p></div>
<div class="card"><p>&le;4 type sizes per slide</p></div>
</div>

<!-- These are the actual numbers deck-qa checks against — not a curated sample, the same values live in tokens.css and get read by scripts/check_contrast.py. -->

---

<!-- _class: framed -->

<svg class="diagram" viewBox="0 0 1600 240" role="img" aria-label="Five-stage pipeline diagram: brief, outline, build, images, QA — brief and outline marked as human sign-off gates, QA marked as an automated pass/fail gate.">
<title>Five-stage pipeline diagram: brief, outline, build, images, QA — brief and outline marked as human sign-off gates, QA marked as an automated pass/fail gate.</title>
<defs>
<marker id="arrowhead" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" class="arrow-head"/>
</marker>
</defs>

<line x1="288" y1="165" x2="352" y2="165" class="arrow" marker-end="url(#arrowhead)"/>
<line x1="608" y1="165" x2="672" y2="165" class="arrow" marker-end="url(#arrowhead)"/>
<line x1="928" y1="165" x2="992" y2="165" class="arrow" marker-end="url(#arrowhead)"/>
<line x1="1248" y1="165" x2="1312" y2="165" class="arrow" marker-end="url(#arrowhead)"/>

<g class="node-gate">
  <rect x="40" y="110" width="240" height="110"/>
  <circle class="gate-icon-bg" cx="160" cy="55" r="28"/>
  <rect class="gate-icon-mark" x="149" y="42" width="6" height="26" rx="3"/>
  <rect class="gate-icon-mark" x="165" y="42" width="6" height="26" rx="3"/>
  <text class="node-label" x="160" y="173" text-anchor="middle">brief</text>
</g>

<g class="node-gate">
  <rect x="360" y="110" width="240" height="110"/>
  <circle class="gate-icon-bg" cx="480" cy="55" r="28"/>
  <rect class="gate-icon-mark" x="469" y="42" width="6" height="26" rx="3"/>
  <rect class="gate-icon-mark" x="485" y="42" width="6" height="26" rx="3"/>
  <text class="node-label" x="480" y="173" text-anchor="middle">outline</text>
</g>

<g class="node-plain">
  <rect x="680" y="110" width="240" height="110"/>
  <text class="node-label" x="800" y="173" text-anchor="middle">build</text>
</g>

<g class="node-plain">
  <rect x="1000" y="110" width="240" height="110"/>
  <text class="node-label" x="1120" y="173" text-anchor="middle">images</text>
</g>

<g class="node-gate">
  <rect x="1320" y="110" width="240" height="110"/>
  <circle class="gate-icon-bg" cx="1440" cy="55" r="28"/>
  <path class="gate-icon-check" d="M 1428 55 L 1438 65 L 1454 45"/>
  <text class="node-label" x="1440" y="173" text-anchor="middle">QA</text>
</g>
</svg>
<p class="caption">brief &rarr; outline &rarr; build &rarr; images &rarr; QA</p>
<p class="annotation">brief, outline: human sign-off &middot; QA: automated pass/fail</p>

---

<!-- _class: statement dark -->

# Run <span class="accent">make-deck</span> on your next deck.

<!-- Closing slide, dark sandwich per tokens.css. This is the single ask — land it and stop talking. -->
