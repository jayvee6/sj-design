# Design System Brief — for the design agent

**You've been handed the `sj-design` repo to build a design system from.** This
file is your orientation: what's here, where the canonical sources live, and the
spec already proven in shipped code — so you don't have to reverse-engineer 23
directories. Read this first, then the three starred files below.

> **TL;DR** — This repo *already is* a working design system (a 13-token CSS
> contract, 17 themes, a 5-layer glass recipe, a type system, two animated deck
> engines). It has never been **extracted** into a standalone, documented,
> tokens-first design system. That's the job. The raw material is all here and
> battle-tested; your task is to formalize it, not invent it.

---

## What this repo is

Studio Joe's design system + presentation engine. It generates **self-contained,
single-file animated HTML slide decks** (no framework, no build step, no runtime
deps) in an Apple-grade visual language: SF Pro type, glass/vibrancy surfaces,
Apple color tokens, GSAP motion, and a WebGPU shader-atmosphere engine.

Two deck engines exist, both driven from one JSON spec via
`scripts/build_presentation.py`:
- **GSAP/CSS engine** (`assets/template.html`) — the mature one. 17 themes,
  ambient atmosphere layers, 6 slide types, transition engine.
- **WebGPU engine** (`assets/webgpu-template.html`) — newer. A live GPU shader
  runs the whole-viewport backdrop (15 scenes + a compute-particle field) behind
  a 10-layout slide kit. Select with `"engine":"webgpu"` in the spec.

---

## ★ Read these three first (canonical sources)

1. **`skills/sj-design-expert/references/studio-design-system.md`** — the design
   system *already distilled from shipped code*. Your single best source. Has:
   the 13-token contract (§1), the 17-theme catalog (§2), the glass card recipe
   (§3), typography (§4), deck layout (§5), atmosphere layers (§6), GSAP
   conventions (§7), the transition engine (§8), single-file portability (§11),
   reduced-motion (§15), and Apple Style Guide copy rules (§16). **Start here.**
2. **`assets/template.html`** — the live source of truth for tokens. The `:root`
   block + every `[data-theme="…"]` block *are* the actual token values (don't
   trust a summary over this file). The WebGPU engine's tokens live in
   `assets/webgpu-template.html`.
3. **`skills/sj-design-expert/SKILL.md`** + **`references/generation-playbook.md`**
   — how the system is meant to be used (Builder/Coder/Consultant/Reviewer
   modes; the deck JSON schema; §0 covers the WebGPU engine, §2–5 the workflow).

Everything else below is a map and a spec summary so you can plan before reading.

---

## The spec, front-loaded

### 1. Token architecture — the 13-name contract
Every theme defines the **same 13 CSS custom properties**; switching themes =
swapping one `[data-theme]` block. This is the backbone of the whole system.

| Token | Role |
|---|---|
| `--bg` | base background color |
| `--bg-gradient` | the atmospheric backdrop gradient |
| `--label-1` / `--label-2` / `--label-3` | text: primary / secondary / tertiary (Apple label hierarchy) |
| `--accent` / `--accent-glow` | brand/interaction color + its glow |
| `--fill-1` / `--fill-2` | translucent fill surfaces |
| `--sep` | hairline separators |
| `--glass-bg` / `--glass-bdr` / `--glass-shd` | the glass surface: fill, border, the 5-layer shadow |

Plus a **typography token set**: `--font` (SF Pro stack), `--font-serif`,
`--font-garamond`, `--font-chicago`, `--font-geneva`, `--font-lucida` (Inter),
`--font-monaco` (JetBrains Mono). Retro Apple faces ship as WOFF2 in `fonts/`.

Example — the default dark theme (`:root` in `template.html`), verbatim:
```css
--bg:          #060618;
--bg-gradient: radial-gradient(ellipse at 35% 15%, #1A237E 0%, #191970 28%, #0d0d3a 58%, #050510 100%);
--label-1:     #ffffff;
--label-2:     rgba(255,255,255,0.55);
--label-3:     rgba(255,255,255,0.25);
--accent:      #0A84FF;          /* Apple systemBlue */
--accent-glow: rgba(10,132,255,0.35);
--glass-bg:    rgba(255,255,255,0.09);
--glass-bdr:   rgba(255,255,255,0.18);
--glass-shd:   0 8px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.18),
               inset 1px 0 0 rgba(10,132,255,0.10), inset 0 -1px 0 rgba(0,0,0,0.08),
               inset -1px 0 0 rgba(0,0,0,0.06);
```

### 2. Theme catalog — 17 themes
`dark` (the `:root` default) + 16 named `[data-theme]` blocks: `light`,
`obsidian`, `noir`, `deep-space`, `golden-hour`, plus a San-Francisco-places
series — `twin-peaks`, `embarcadero`, `muir-woods`, `the-mission`, `santa-cruz`,
`sausalito`, `half-moon-bay`, `redwood`, `the-richmond`, `nob-hill`, `haight`.
Each is just a 13-token swap. *(Note: `studio-design-system.md` §2 says "17
themes" counting `dark` as the default; the file shows 16 `[data-theme]` blocks
plus the `:root` default = 17. Reconcile against `template.html` as truth.)*

### 3. Glass surface — the signature component
A 5-layer `box-shadow` (outer drop + 4 inset bevels) plus a specular-highlight
pseudo-element. Full recipe in `studio-design-system.md` §3. This is the most
re-used surface in the system — it should be a first-class component/mixin in
whatever you build.

### 4. Typography
SF Pro system stack for UI; a curated set of display/serif/retro faces for
character. Type scale, weights, and the retro-Apple WOFF2 wiring are in
`studio-design-system.md` §4 and `fonts/README.md`.

### 5. Motion
- **GSAP conventions** (easing, slide/element transitions, the iris-reflow
  gotcha): `studio-design-system.md` §7–8 + `references/slide-animations.md`.
- **WebGPU scene atmosphere** (15 fragment-shader scenes + compute particles,
  one 24-float uniform contract): `assets/webgpu-template.html` /
  `showcase/webgpu-lookbook.html`; design rationale in
  `references/viz-motion-craft.md`.
- **Reduced-motion** is a hard requirement, not optional: §15 + every engine
  freezes time/parallax under `prefers-reduced-motion`.

---

## Repo map (where things live)

| Path | What |
|---|---|
| `assets/template.html` | GSAP deck template + **token source of truth** (all themes) |
| `assets/webgpu-template.html` | WebGPU deck engine shell (tokenized) |
| `assets/transitions.js` | slide transition engine (slide/fade/cube/iris/particles) |
| `scripts/build_presentation.py` | JSON spec → self-contained `.html` (both engines) |
| `lib/` | shared single-file libs: `webgpu-bootstrap.js` (SJGpu), `synthetic-pulse.js`, `envelopes.js`, `canvas-size.js` |
| `fonts/` | WOFF2 faces (Inter, JetBrains Mono, EB Garamond, retro Apple: Chicago, Geneva) |
| `showcase/` | live demos — `webgpu-lookbook.html` is the proven WebGPU reference deck |
| `evals/` | example JSON specs (`webgpu-lookbook.json` = the look-book as a spec) |
| `index.html` | the repo's own showcase/landing page |
| `skills/sj-design-expert/references/` | **the distilled design system** — read these |
| `references/` (root) | `emoji-visualizations.md`, `image-fx.md`, `slide-animations.md`, `webgpu-viz-patterns.md`, `apple-hig/` |
| `docs/swiftui-conventions.md` | the system's native (SwiftUI/Apple) expression |
| `README.md` / `CLAUDE.md` | repo overview + working notes |

---

## Constraints — keep these true in anything you build

- **Self-contained, single-file output.** Generated decks inline everything (CSS,
  JS, fonts-as-needed, base64 media). No framework, no bundler, no runtime deps
  beyond GSAP via CDN. The portability pattern is the product
  (`studio-design-system.md` §11). A design system here should preserve that.
- **Apple-grade or don't ship it.** SF Pro, Apple label hierarchy, Apple system
  colors, glass/vibrancy. Copy follows the Apple Style Guide (§16).
- **One token contract, many themes.** Don't fork token *names* per theme — a new
  look = a new 13-token block. Keep that invariant.
- **Reduced-motion + accessibility are requirements**, not nice-to-haves (§15;
  contrast, 44px targets, photosensitivity/strobe limits live in
  `motion-game-ux.md` and `viz-motion-craft.md`).
- **Image-FX attribution.** Any hover-distortion / depth-parallax / explosion FX
  derived from akella's work requires a visible credit (§14 / §3 of
  `studio-design-system.md`). Don't strip it.

---

## Suggested deliverables (a starting frame — adapt freely)

If "make a design system" is open-ended, a high-value shape is:
1. **`tokens/`** — *a starter already exists:* `tokens/design-tokens.json` (W3C
   DTCG) holds all 17 themes × the 13-name contract + 7 font families, generated
   from `template.html` via `scripts/extract_tokens.py` (re-run to regenerate;
   `tokens/README.md` explains the custom `cssGradient`/`cssShadow` types). Build
   your pipeline on this rather than re-parsing CSS.
2. **Component specs** — glass surface, typography scale, slide layouts (the 10
   WebGPU layouts + 6 GSAP slide types), atmosphere layers, buttons/HUD.
3. **Foundations doc** — color (Apple system mapping), type, spacing, elevation
   (the glass shadow stack), motion (GSAP easings + scene catalog), a11y.
4. **A theming guide** — how a 13-token swap produces a new look; how to add one.
5. **Usage** — how it feeds `build_presentation.py` and both engines.

Confirm scope/format with the owner before committing to a direction — they may
want DTCG tokens, a Style-Dictionary pipeline, a Storybook, or a Figma-ready
spec. The material supports any of these.

---

*Owner: Studio Joe (`jayvee6/sj-design`). The `sj-design-expert` skill in this
repo is the system's own principal-design-engineer agent — its `references/` are
the authoritative distillation; prefer them over guessing.*
