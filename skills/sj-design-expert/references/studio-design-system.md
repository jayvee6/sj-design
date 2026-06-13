# draft-studio-design-system.md
<!-- T1 output — Web design system & deployment slice -->
<!-- Agent: READ-ONLY T1 · 2026-06-12 · Mac -->

---

## Sources read

| File | What I extracted |
|---|---|
| `sj-design/assets/template.html` (lines 1–1450) | Full token set, all 17 themes, glass mixin, typography, layout, ambient layers, JS engine |
| `sj-design/assets/transitions.js` | All 5 transition implementations + public API |
| `sj-design/CLAUDE.md` | Repo purpose, sja-automation tooling |
| `sj-design/skills/presentation/SKILL.md` (lines 1–120) | Skill description, slide workflow, Apple style rules |
| `sj-design/references/slide-animations.md` | Per-type GSAP choreography, canonical easing values |
| `sj-design/references/image-fx.md` | akella techniques, attribution rules |
| `sj-design/showcase/glass-refraction-demo.html` (lines 1–220) | Glass anatomy (4 CSS layers), SVG filter approach |
| `sj-design/showcase/components.html` (lines 1–200) | Stat card hover spring, tint modifier pattern |
| `sj-design/lib/liquidglass.js` (lines 1–100) | DEFAULTS object (blur, refraction, fresnel params) |
| `studiojoe/index.html` (lines 1–200) | Nocturne/Aurora palette, zone-atmosphere system, grain overlay |
| `studiojoe/vercel.json` | Deployment config (`outputDirectory: "."`, no build) |
| `studiojoe/CLAUDE.md` | Branching rules, CI gates, CDN pinning |
| `studiojoe/.github/workflows/ci.yml` | HTMLHint + Lychee checks |
| `Obsidian/joeOS/Projects/studiojoe.md` | Architecture decisions, deploy history, iPod API keys |
| `Obsidian/joeOS/Projects/sj-design.md` | Theme count, font stack table, retro font attribution |
| `Obsidian/joeOS/Projects/studiojoe-security.md` | Security playbook scope, `/security-hardening` skill |

---

## Distilled patterns

### 1. Token architecture — the 13-name contract

Every page in both repos shares exactly this set of CSS custom properties on `:root` or `[data-theme]`. Changing the theme means swapping one value block; component code never changes.

| Token | Role | Example (dark/Blue Hour) |
|---|---|---|
| `--font` | System sans stack | `-apple-system, BlinkMacSystemFont, "SF Pro Display"…` |
| `--bg` | Flat fallback color | `#060618` |
| `--bg-gradient` | Gradient (bound to `background`) | `radial-gradient(ellipse at 35% 15%, …)` |
| `--label-1` | Primary text | `#ffffff` |
| `--label-2` | Secondary text | `rgba(255,255,255,0.55)` |
| `--label-3` | Tertiary / hint | `rgba(255,255,255,0.25)` |
| `--accent` | Brand color, bullets, CTAs | `#0A84FF` |
| `--accent-glow` | Drop shadow for accent elements | `rgba(10,132,255,0.35)` |
| `--fill-1` | Subtle surface tint | `rgba(255,255,255,0.04)` |
| `--fill-2` | Slightly stronger surface | `rgba(255,255,255,0.08)` |
| `--sep` | Divider lines | `rgba(255,255,255,0.10)` |
| `--glass-bg` | Glass card background | `rgba(255,255,255,0.09)` |
| `--glass-bdr` | Glass border | `rgba(255,255,255,0.18)` |
| `--glass-shd` | Glass box-shadow (5-layer compound) | `0 8px 40px …, inset 0 1px 0 …` (see below) |

Source: `assets/template.html` lines 60–84, `studiojoe/index.html` lines 19–36.

> **Gotcha — studiojoe uses `--bg-g`, not `--bg-gradient`.**  
> The deck template uses `--bg-gradient`; studiojoe.dev uses `--bg-g`. Same concept, different name — don't copy one into the other.

> **Gotcha — studiojoe is dark-only since 2026-05-16.**  
> Light mode was removed (unreadable over the WebGPU hero). The presentation skill still supports 17 themes including light ones. Do not add a theme toggle to studiojoe.dev.

---

### 2. Theme catalog (17 named themes in sj-design)

All themes are `[data-theme="<name>"]` on `<html>`. Each overrides all 13 tokens + per-theme gobos/bokeh palette arrays. Source: `assets/template.html` lines 86–358, JS `THEME_GOBOS` object lines 1551–1640.

| Theme | Personality | Light/Dark | Accent |
|---|---|---|---|
| `dark` (default) | Blue Hour indigo night sky | Dark | `#0A84FF` |
| `light` | Crissy Field California bright | Light | `#E8450A` |
| `obsidian` | Matte charcoal, terminal green | Dark | `#34C759` |
| `deep-space` | Near-black, teal nebulae | Dark | `#32D2F2` |
| `noir` | Pure black, crimson editorial | Dark | `#FF3B5C` |
| `golden-hour` | Amber dusk, hospitality | Light | `#C43A00` |
| `twin-peaks` | City lights below fog | Dark | `#FF9F0A` |
| `embarcadero` | Pre-dawn bay water | Dark | `#5AC8FA` |
| `muir-woods` | Old-growth redwood | Dark | `#30D158` |
| `the-mission` | Mural purple/magenta | Dark | `#FF2D78` |
| `santa-cruz` | Warm Pacific surf | Light | `#FF6B35` |
| `sausalito` | Mediterranean bay calm | Light | `#F4A261` |
| `half-moon-bay` | Moody coastal gray | Dark | `#5B9BBF` |
| `redwood` | Old-growth forest amber | Dark | `#D4845A` |
| `the-richmond` | Foggy, muted, quiet | Dark | `#5E82A4` |
| `nob-hill` | Victorian opulence, gold | Dark | `#D4AF37` |
| `haight` | Psychedelic rainbow | Dark | `#FF6FD8` |

**Eyebrow color override rule:** On light/warm-gradient themes (`light`, `golden-hour`, `santa-cruz`, `sausalito`), `.eyebrow` gets `rgba(255,255,255,0.92)` instead of `var(--accent)` — the accent is too low-contrast against bright gradients. Source: `assets/template.html` lines 547–553.

**Starfield visibility rule:** Stars shown only in truly dark themes. `deep-space` = full opacity (1.0); `embarcadero` = 0.65; `half-moon-bay` = 0.45; `nob-hill` = 0.55. All other themes: `opacity: 0`. Source: `assets/template.html` lines 415–432.

---

### 3. Glass card recipe (5-layer box-shadow + specular pseudo-element)

```css
/* Standard glass card — works in any component */
.card {
  background:     var(--glass-bg);
  border:         1px solid var(--glass-bdr);
  border-radius:  clamp(10px, 1.3vw, 20px);
  box-shadow:     var(--glass-shd);   /* 5-layer compound shadow */
  position:       relative;
  overflow:       hidden;
}

/* Graduated specular highlight — approximates refractive lip() curve */
/* Brightest at top-left, fades toward center. No blur needed. */
.card::before {
  content:        '';
  position:       absolute;
  inset:          0;
  border-radius:  inherit;
  background:     radial-gradient(ellipse 80% 40% at 40% 20%,
                    rgba(255,255,255,0.13) 0%,
                    transparent 70%);
  pointer-events: none;
  z-index:        0;
}
/* All card content needs position:relative; z-index:1 to sit above ::before */
```

The 5-layer `--glass-shd` compound (dark/Blue Hour example):
```css
0 8px 40px rgba(0,0,0,0.5),        /* ambient drop shadow */
inset 0 1px 0 rgba(255,255,255,0.18),   /* top specular lip */
inset 1px 0 0 rgba(10,132,255,0.10),    /* left accent tint */
inset 0 -1px 0 rgba(0,0,0,0.08),        /* bottom darkening */
inset -1px 0 0 rgba(0,0,0,0.06)         /* right darkening */
```

Source: `assets/template.html` lines 83, 720–730, 965–975.

**Backdrop blur** is added when there's actual content behind the card to blur:
```css
backdrop-filter: blur(16px) saturate(180%);
-webkit-backdrop-filter: blur(16px) saturate(180%);
```
Source: `showcase/glass-refraction-demo.html` layer-2/3 anatomy, `showcase/components.html` line 113.

**When to add backdrop blur:** any glass card that floats over a gradient or image background. Omit when the card sits on a flat color (`#000`, `var(--bg)`) — blurring a single color adds no visual value and wastes GPU.

---

### 4. Typography system

**Font stack variables** (declared in `assets/template.html` `:root`):

| Variable | Typeface | Self-hosted WOFF2? | Use |
|---|---|---|---|
| `--font` | `-apple-system, SF Pro Display, Helvetica Neue` | No (system) | Body, UI, default |
| `--font-serif` | Georgia, Times New Roman | No (system) | Fallback serif |
| `--font-chicago` | ChicagoKare | Yes (`fonts/ChicagoKare-Regular.woff2`) | Retro Mac System 7 |
| `--font-geneva` | Geneva-12 | Yes (`fonts/geneva-12.woff2`) | Classic Mac |
| `--font-lucida` | Inter (mapped as Lucida) | Yes (`fonts/Inter-Regular/Bold.woff2`) | Modern sans |
| `--font-garamond` | EB Garamond | Yes (`fonts/EBGaramond-Regular/Medium.woff2`) | Elegant serif |
| `--font-monaco` | JetBrains Mono | Yes (`fonts/JetBrainsMono-Regular.woff2`) | Code/monospace |

Source: `assets/template.html` lines 15–68, `sj-design.md` font table.

**Attribution:** Retro fonts sourced from ryOS (github.com/ryokun6/ryos — Cursor's design lead). This is explicitly documented as the source.

**Font-face path note:** In `assets/template.html` the path is `../../fonts/`. This works for decks in `showcase/decks/` (two levels deep). Adjust if the generated deck lives elsewhere.

**Clamp-based sizing scale (deck template):**

| Element | Font-size clamp |
|---|---|
| `.eyebrow` | `clamp(17px, 2.2vw, 32px)` — `letter-spacing: 0.14em; text-transform: uppercase` |
| `.headline` | `clamp(26px, 4.6vw, 68px)` — `font-weight: 700; letter-spacing: -0.028em` |
| `.slide-title .headline` | `clamp(32px, 6vw, 88px)` — `font-weight: 800; letter-spacing: -0.038em` |
| `.subheading` | `clamp(17px, 2.2vw, 32px)` — `font-weight: 400; line-height: 1.45` |
| `.bullets li` | `clamp(17px, 2.3vw, 34px)` — `font-weight: 500` |
| `.slide-note` | `clamp(10px, 0.95vw, 14px)` — `font-style: italic` |

Three text-size modifier classes (`ts-sm`, `ts-lg`, `ts-xl`) scale all elements proportionally. Default is `ts-md` (no class needed). Source: `assets/template.html` lines 1238–1289.

---

### 5. Layout system — deck

```
#deck:  width: min(100vw, 177.78vh); height: min(100vh, 56.25vw)
        /* locked 16:9 at largest possible size — handles any viewport */
        perspective: 1400px; perspective-origin: 50% 38%
```

`.slide`: `position: absolute; inset: 0; padding: clamp(28px,5%,72px) clamp(36px,7%,108px)`

`.slide-inner`: `max-width: 1100px; max-height: 100%; overflow: hidden; display: flex; flex-direction: column; gap: clamp(10px,1.6vw,24px)`

Two-column: `grid-template-columns: 1fr 1fr; gap: clamp(16px,2.5vw,48px)`. Columns use `align-items: flex-start` (not stretch) to avoid Safari aspect-ratio bugs. Source: `assets/template.html` lines 493–529, 688–716.

Stats grid: `grid-template-columns: repeat(3, 1fr)`. Featured card: `grid-column: span 2`. Source: lines 940–979.

Glass gallery grid: `grid-template-columns: repeat(auto-fit, minmax(clamp(180px,22vw,260px), 1fr))`. Source: lines 862–873.

---

### 6. Ambient atmosphere layers (z-index stack)

```
z-index 0 : gobo-layer (Perlin blobs), starfield, bokeh, sun, dust, grain, blind-bars, city-glow
z-index 8 : sf-fog (Karl the Fog emoji particles — Embarcadero/Half Moon Bay only)
z-index 9 : #deck (slides + galleries)
z-index 200: #hud, #progress
z-index 999: #emoji-rain
```

**Perlin gobo blobs:** 2–4 radial-gradient divs per theme, driven by 2D Perlin noise via `gsap.ticker`. Speed factor = 0.038. Each blob wanders ±range% from a random center point. GPU-composited via `transform` (never `left/top`). Source: `assets/template.html` lines 1544–1679.

**Bokeh:** 15 blurred circles, per-theme color palette, slow GSAP drift + opacity breathe. Source: lines 1727–1776.

**Starfield:** Pure CSS + GSAP twinkle. Count varies by theme (deep-space=200, default=95). Source: lines 1682–1720.

**SF fog:** emoji ☁️ at 3 depth levels (deep=blur(32px), mid=blur(16px), near=blur(6px)), slow GSAP horizontal drift. Only active on Embarcadero + Half Moon Bay. Source: lines 1170–1207.

**Grain:** SVG `<feTurbulence>` noise as `background-image` data URI. `opacity: 0.035; mix-blend-mode: overlay`. Source: `studiojoe/index.html` lines 79–83.

---

### 7. GSAP animation conventions

**Canonical easing values** (used throughout both repos):
```js
const EASE_OUT    = 'cubic-bezier(0.16, 1, 0.3, 1)';  // Apple expo-out — primary
const EASE_SPRING = 'back.out(1.5)';                    // Spring for pop elements
const EASE_SOFT   = 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'; // Softer, UI transitions
const DUR         = 0.6; // default duration
```
Source: `assets/template.html` lines 1506–1509.

**Per-slide-type entrance choreography** (from `references/slide-animations.md`):

| Type | Choreography |
|---|---|
| `title` | icon drops from top → eyebrow → headline rises → subheading fades |
| `content` | eyebrow + headline slide from left → bullets stagger one by one |
| `stats` | eyebrow/headline in → cards spring up with scale → values count up from 0 |
| `quote` | watermark scales behind → icon springs → quote fades up → attribution |
| `two-column` | columns slide from opposite sides → bullets stagger inside |
| `gallery` | frame scales in → Ken Burns cycle begins |
| `media` | heading drops → frame scales up from 95% → caption fades |
| `closing` | headline spring-scales → CTA fades → emoji rain available |

**Pre-hide pattern:** All animatable children set to `opacity: 0` in CSS before JS loads, preventing flash of unstyled content. GSAP `fromTo()` overrides via inline styles. Source: `assets/template.html` lines 1428–1450.

**Stat count-up:** Supports `$`, `%`, commas. Values animate from 0. Source: `sj-design.md` slide types section.

**Ken Burns gallery:** 4 named keyframe animations (`kb-1`…`kb-4`), each combining `scale(1.00–1.18)` + `translate`. Negative `animation-delay` offsets (−0s to −6s) ensure photos are already in motion when they first appear — no snap-back. GSAP controls the crossfade; CSS handles the pan/zoom independently. Source: `assets/template.html` lines 813–839.

---

### 8. Slide transition engine (`assets/transitions.js`)

Five built-in transitions, selectable via `data-transition="<name>"` on `<html>`:

| Name | Technique | Duration |
|---|---|---|
| `slide` (default) | Outgoing fades+shifts −36px; incoming glides in from +22px with delay | ~0.35s |
| `fade` | Simple cross-dissolve | ~0.45s |
| `cube` | 3D rotateY flip using `#deck`'s existing `perspective:1400px` | 0.70s |
| `iris` | CSS `clip-path: circle()` expand — synchronous reflow trick to commit "closed" state | 0.80s |
| `particles` | Canvas shard dissolve — 130 physics-driven glass shards, accent-colored | ~1.5s |

**Required contract for any transition function:**
1. Call `toEl.classList.add('active')`
2. Call `fromEl.classList.remove('active')` when outgoing is gone
3. Call `opts.onComplete()` exactly once
4. Call `opts.onContentReady()` when content stagger should begin

Custom transitions: `SJTransitions.register('myName', fn)`. Source: `assets/transitions.js` lines 1–21.

**`particles` gotcha:** creates a persistent `#sj-fx-canvas` on first use. Reads `--accent` from computed styles for color palette. Source: lines 206–296.

**`iris` gotcha:** requires a synchronous `void el.offsetHeight` reflow between setting `clipPath: 'circle(0%…)'` and `clipPath: 'circle(150%…)'` — omitting this causes the browser to batch both states and the animation never plays. Source: lines 154–193.

---

### 9. Zone-atmosphere system (studiojoe.dev only)

```css
body { --atmo: 45,212,191; }
body[data-zone="showroom"]  { --accent: #2DD4BF; --atmo: 45,212,191; }
body[data-zone="sandbox"]   { --accent: #22D3EE; --atmo: 34,211,238; }
body[data-zone="shelf"]     { --accent: #8B7CF6; --atmo: 139,124,246; }
body[data-zone="workbench"] { --accent: #E8B450; --atmo: 232,180,80; }

#atmo {
  background: radial-gradient(ellipse 80% 60% at 50% 8%,
    rgba(var(--atmo), 0.14) 0%, rgba(var(--atmo), 0.05) 38%, transparent 70%);
  transition: background 0.8s ease;
}
```

An `IntersectionObserver` sets `body[data-zone]` as zones scroll into view. The `--atmo` token holds the RGB triplet (no `rgba()` wrapper) so it can be used in `rgba(var(--atmo), 0.14)` constructs. Source: `studiojoe/index.html` lines 59–68.

This is specific to studiojoe.dev. The deck template does not use this system.

---

### 10. Nocturne / Aurora palette (studiojoe.dev)

The site's current palette (distinct from the Blue Hour default in the deck template):

```css
--bg:       #060608;   /* graphite-near-black */
--bg-g:     radial-gradient(ellipse 90% 60% at 50% -10%, #122 0%, #0c1418 30%, #08090e 62%, #060608 100%);
--accent:   #2DD4BF;   /* electric teal */
--accent-bg: rgba(45,212,191,0.12);
```

Blue Hour indigo (`#0A84FF`) retired 2026-05-16 on studiojoe.dev. The deck template still uses Blue Hour as `data-theme="dark"` default. Source: `studiojoe/index.html` lines 19–33, `studiojoe.md`.

---

### 11. Single-file portability pattern

All `lib/` files are designed so demos can load them from a path OR inline a fallback:
```html
<script src="../../lib/synthetic-pulse.js"></script>
<!-- OR inline the whole file for true single-file portability -->
```

The template loads GSAP from CDN only — no other external dependencies. Source: `SKILL.md`, `sj-design.md`.

`studiojoe/lib/` = verbatim copy of `sj-design/lib/`. No divergence. Both repos share `canvas-size.js`, `synthetic-pulse.js`, `envelopes.js`, `webgpu-bootstrap.js`. Source: `studiojoe.md` files section.

---

### 12. Deployment & CI playbook

**studiojoe.dev:**
- `main` → auto-deploys to prod (direct push blocked; must go through PR)
- `staging` → auto-deploys to https://staging.studiojoe.dev
- Workflow: work on `staging` or feature branch → verify at staging URL → PR `staging → main` → CI → merge
- CI checks: HTMLHint (all `*.html`) + Lychee link-check (fails on broken links; excludes cdnjs/fonts/linkedin)
- `vercel.json`: `outputDirectory: "."`, no `buildCommand`, no framework — files served as-is
- No env vars in production code (Apple MusicKit JWT signed server-side via `api/apple-token.js` Vercel serverless)
- Merge strategy: merge-commits only (never squash — handoff log `.claude/handoff-*.md` references chunk SHAs)

Source: `studiojoe/CLAUDE.md`, `studiojoe/vercel.json`, `studiojoe/.github/workflows/ci.yml`, `studiojoe.md`.

---

### 13. Security playbook (`/security-hardening` skill)

Seven-point pre-ship checklist enforced by the `studiojoe-security` skill:

| Check | Requirement |
|---|---|
| Credential leaks | Scan tracked files + git history |
| `.gitignore` | `.env*`, `*.pem`, `*.key`, `.vercel`, private dirs |
| Vercel security headers | All 6 required headers in `vercel.json` |
| CSP quality | `default-src 'none'`, no `unsafe-eval`, no wildcards |
| Firebase auth gate | `body { visibility: hidden }` + `window.location.replace` guard before auth check |
| CDN SRI | `crossorigin="anonymous"` + integrity hashes on all CDN scripts |
| Firebase authorized domains | Review + remove localhost before production |

Source: `studiojoe-security.md`.

**CDN pinning:** GSAP is pinned to `3.12.5` across both repos:
```
https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js
https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js  (resume.html only)
```

---

### 14. Image FX attribution rule

Three WebGL techniques (3D object explosion, fake3d depth parallax, hover distortion/reveal) are independent reimplementations of work by **akella / Yuri Artyukh**. Licensing varies per repo (Codrops license for explosion + fake3d; MIT for hover).

**Hard rule:** Any generated artifact using these techniques must include a visible credit to akella with a link to the relevant repo. A small footer credit line is sufficient. Source: `references/image-fx.md` lines 183–205.

---

### 15. `prefers-reduced-motion` pattern

Both repos honor `prefers-reduced-motion`. Pattern: static draws; reveals shown in final state immediately (no animation). Source: `studiojoe.md` JS features table.

---

### 16. Apple Style Guide for slide copy

Enforced by the skill for all generated text:
- **Headings:** sentence case, max 8 words
- **Bullets:** one idea per line, active voice, no jargon without definition
- **Numbers:** spell out 0–9, numerals for 10+
- **Serial comma:** always
- **No filler words:** leverage, utilize, synergy, solution — banned
- **No superlatives** without evidence

Source: `skills/presentation/SKILL.md` lines 76–90.

---

## Reviewer checklist candidates

- [ ] All 13 token names present and spelled correctly (`--label-1` not `--text-1`)
- [ ] `--glass-shd` uses the 5-layer compound (not a single shadow)
- [ ] `::before` specular pseudo-element present on glass cards; content is `''`, `z-index: 0`; card content uses `z-index: 1`
- [ ] Eyebrow color override applied for light/warm themes (`light`, `golden-hour`, `santa-cruz`, `sausalito`)
- [ ] Starfield shown only for applicable dark themes; opacity values match spec
- [ ] `@font-face` src paths correct relative to output location (`../../fonts/` from showcase/decks/)
- [ ] GSAP loaded from pinned CDN URL `3.12.5` — not a newer/different version
- [ ] Transition function calls `onComplete()` exactly once and `onContentReady()` at the right timing
- [ ] Perlin gobo blobs use `transform` (not `left/top`) for GPU compositing
- [ ] Zone-atmosphere `--atmo` token uses RGB triplet without `rgba()` wrapper
- [ ] studiojoe.dev has NO light-mode toggle (retired 2026-05-16)
- [ ] Any akella technique (explosion/fake3d/hover) has visible credit + repo link in the output
- [ ] PRs to studiojoe `main` go through `staging` branch + CI (HTMLHint + Lychee)
- [ ] No `unsafe-eval` in CSP; no CDN scripts without SRI hashes on gated pages
- [ ] Slide count 6–12 (below 6 = thin, above 12 = loses audience)
- [ ] Slide headings: sentence case, ≤8 words
- [ ] `prefers-reduced-motion` honored (static final state, no animation)
- [ ] Stats slide count-up values support `$`, `%`, commas — no manual formatting needed

---

## Suggested decision-tree rows

| Question / task | Go to § |
|---|---|
| What CSS tokens does this system use? | §1 Token architecture |
| Which theme should I pick for this deck? | §2 Theme catalog |
| How do I make a glass card? | §3 Glass card recipe |
| When do I add `backdrop-filter`? | §3 (gotcha at end) |
| What fonts are available? | §4 Typography |
| What layout do I use for a stats slide? | §5 Layout system |
| How deep is the atmosphere layer stack? | §6 Ambient atmosphere |
| What easing should I use? | §7 GSAP conventions |
| How do I add a slide transition? | §8 Transition engine |
| How do I use the iris transition correctly? | §8 (iris gotcha) |
| What is the difference between studiojoe.dev and the deck template? | §9 Zone-atmosphere, §10 Nocturne/Aurora |
| How do I make a file fully self-contained? | §11 Single-file portability |
| What CI checks must pass before merging? | §12 Deployment & CI |
| What security headers are required? | §13 Security playbook |
| Does this image effect need an akella credit? | §14 Image FX attribution |
| How should I write slide copy? | §16 Apple Style Guide |

---

## UNVERIFIED

- **`scripts/build_presentation.py`** — not read. The Python build process (JSON spec → HTML) may have its own constraints (field names, escaping rules, slide type validation). The JSON schema in `SKILL.md` is verified; the Python implementation details are not.
- **`lib/liquidglass.js` full implementation** — only the `DEFAULTS` object was read (lines 1–100). The actual WebGL/Canvas rendering pipeline, the `feDisplacementMap` approach for resume.html's liquid glass, and interaction with the SJGpu bootstrap are not verified here. The DEFAULTS are confirmed: `refraction: 0.69`, `chromAberration: 0.05`, `fresnel: 1`, `cornerRadius: 65`.
- **studiojoe `resume.html`** — referenced in multiple places (ScrollTrigger, liquid glass, A−/A/A+ font sizer, `#method` section, reduced-motion) but not directly read. Behaviors inferred from vault notes and CLAUDE.md.
- **Vercel security headers content** — the playbook states "all 6 required headers" but the specific 6 headers were not verified (would require reading `studiojoe-security/templates/vercel-headers.json` which wasn't read).
- **CSP with injected styles** — the security vault mentions CSP for "static site" vs. "Firebase-gated" variants. The specific CSP directives and how they handle GSAP's inline style injection are not verified.
- **`evals/evals.json`** — not read. Evaluation test cases for the skill may surface additional constraints or failure modes not captured here.
- **Mouse parallax multipliers** — vault note states `18H/11V` asymmetric multipliers as "feel natural" but this was read from a secondary source (sj-design.md), not from the actual implementation file.
- **`showcase/atmosphere.html`** atmospheric effect specifics — not read beyond what's documented in SKILL.md references.
