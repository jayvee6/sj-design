# DESIGN.md — Studio Joe visual system

<!-- {{GENERATED_NOTICE}} -->

This file tells any agent working in this project how visual work must look.
It is a compact, portable export of the Studio Joe design system. For anything
not covered here, invoke the `sj-design-expert` skill; do not invent a
convention. Every rule below cites where it was proven
(`studio-design-system.md` = `sj-design/skills/sj-design-expert/references/studio-design-system.md`).

{{PROJECT_LINE}}

## 1. Tokens — the 13-name contract

Every surface uses exactly these 13 custom properties and nothing else for
color, surface, and depth. A new look is a new 13-value block; the names never
fork. Component code reads `var(--token)`; it never hard-codes a hex value.
(studio-design-system.md §1)

{{TOKEN_BLOCK}}

| Token | Role |
|---|---|
| `--bg` | flat fallback background |
| `--bg-gradient` | the real background (bound to `background`) |
| `--label-1` / `--label-2` / `--label-3` | primary / secondary / tertiary text |
| `--accent` / `--accent-glow` | brand color, CTAs, bullets / its glow shadow |
| `--fill-1` / `--fill-2` | subtle / stronger surface tint |
| `--sep` | dividers |
| `--glass-bg` / `--glass-bdr` / `--glass-shd` | glass card fill / border / 5-layer shadow |

Known divergence: studiojoe.dev names the gradient `--bg-g`, not
`--bg-gradient`; it is also dark-only (no theme toggle, since 2026-05-16).
Don't copy one name into the other. (studio-design-system.md §1)
{{DIVERGENCES}}

### Fonts

| Variable | Stack |
|---|---|
{{FONT_ROWS}}

Default is `--font` (system SF Pro). Retro faces (`ChicagoKare`, `Geneva-12`)
come from ryOS and are self-hosted WOFF2 in `sj-design/fonts/`.
(studio-design-system.md §4)

### All themes (switch with `data-theme` on `<html>`)

| Theme | Mode | `--bg` | `--accent` |
|---|---|---|---|
{{THEME_ROWS}}

## 2. Surfaces — glass

```css
.card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-bdr);
  border-radius: clamp(10px, 1.3vw, 20px);
  box-shadow: var(--glass-shd);          /* the 5-layer compound, never a single shadow */
  position: relative; overflow: hidden;
}
.card::before {                           /* specular lip, brightest top-left */
  content: ''; position: absolute; inset: 0; border-radius: inherit;
  background: radial-gradient(ellipse 80% 40% at 40% 20%, rgba(255,255,255,0.13) 0%, transparent 70%);
  pointer-events: none; z-index: 0;
}
.card > * { position: relative; z-index: 1; }
```

Add `backdrop-filter: blur(16px) saturate(180%)` (plus `-webkit-`) only when
the card floats over a gradient or image. Over a flat color it adds nothing and
costs GPU. (studio-design-system.md §3)

**Native (SwiftUI):** iOS/macOS 26+ use system Liquid Glass first:
`.glassEffect(.regular, in: shape)` / `GlassEffectContainer`. Fall back to
`.sjGlass(in:)` pre-26, or where macOS renders `.glass` flat. Guard with
`#available(iOS 26, *)`. Native token enums derive from the CSS source of
truth, never a parallel palette. (apple-native-design.md §P1–P2)

## 3. Type

| Role | Size | Weight / tracking |
|---|---|---|
| eyebrow | `clamp(17px, 2.2vw, 32px)` | uppercase, `letter-spacing: 0.14em` |
| headline | `clamp(26px, 4.6vw, 68px)` | 700, `-0.028em` |
| title headline | `clamp(32px, 6vw, 88px)` | 800, `-0.038em` |
| subheading | `clamp(17px, 2.2vw, 32px)` | 400, `line-height: 1.45` |
| body / bullets | `clamp(17px, 2.3vw, 34px)` | 500 |

On bright/warm themes (`light`, `golden-hour`, `santa-cruz`, `sausalito`) the
eyebrow is `rgba(255,255,255,0.92)`, not `--accent`; the accent is too low
contrast there. (studio-design-system.md §2, §4)

## 4. Motion

```js
const EASE_OUT    = 'cubic-bezier(0.16, 1, 0.3, 1)';        // Apple expo-out — the default
const EASE_SPRING = 'back.out(1.5)';                         // pops only
const EASE_SOFT   = 'cubic-bezier(0.25, 0.46, 0.45, 0.94)';  // UI transitions
const DUR = 0.6;
```

- Animate `transform` / `opacity` only, never `left` / `top`. (§6)
- Pre-hide animated children with `opacity: 0` in CSS so nothing flashes before JS runs. (§7)
- GSAP is pinned to `3.12.5` from cdnjs, and it's the only external dependency in single-file artifacts. (§11, §13)
- Honor `prefers-reduced-motion`: show the final state immediately, with no animation. (§15)

## 5. Copy (Apple Style Guide)

Headings in sentence case, at most 8 words. One idea per bullet, active voice.
Spell out zero to nine; use numerals for 10 and up. Always use the serial comma.
Banned words: *leverage, utilize, synergy, solution*. No superlatives without
evidence. (studio-design-system.md §16)

## 6. Slop tells — reject on sight

Each tell breaks a rule above:

1. A hex color, gradient, or shadow hard-coded in a component instead of a token. (§1)
2. A new token name (`--text-1`, `--primary`, `--card-bg`), or a Tailwind default palette standing in for the theme. (§1)
3. A single flat `box-shadow` on a card, or a glass card with no `::before` specular. (§2)
4. `backdrop-filter` over a flat background. (§2)
5. Accent-colored eyebrows on a bright/warm theme. (§3)
6. `ease-in-out` / `linear` defaults, or motion that animates `left`/`top`. (§4)
7. No reduced-motion path. (§4)
8. An unpinned or extra CDN dependency in a single-file artifact. (§4)
9. Title Case headings, banned filler words, or unevidenced superlatives. (§5)
10. A light-mode toggle on studiojoe.dev. (§1 divergence note)
11. An akella technique (3D explosion, fake3d parallax, hover distortion) without a visible credit and repo link. (studio-design-system.md §14)
12. Video overlays that aren't chyron practice: opaque mid-frame bars, AI badges, or text outside title-safe. Use lower-thirds that are translucent, animated, and brief. (Studio Joe on-screen-graphics rule)

General heuristics (common AI-generated tells, not yet proven in a Studio Joe
project; flag them, don't treat them as law): centered hero plus three identical
icon-over-text feature cards; gradient text on every heading; `border-radius:
9999px` on everything; placeholder names like *Acme* or *Lorem*; mixed icon
styles in one view.

## 7. Verify before calling it done

A visual claim needs a screenshot from real Chrome (chrome-devtools MCP), with
a clean console and navigation exercised. For WebGPU or canvas, probe for a
black canvas instead of trusting the headless preview. Metal (Mac) is the bar;
a pass on Windows alone is not a pass.
(review-verification-playbook.md §1–2, §5)
