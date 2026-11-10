# Emil Kowalski skills — external source index + divergence register

**Source:** https://github.com/emilkowalski/skills @ `715c180` (2026-11-09), ingested 2026-11-10 via `ingest-design-source`.
**Status:** EXTERNAL TASTE, not first-party proof. Every other reference in this folder is distilled from Studio Joe's own
shipped projects; these five are a respected outside practitioner's rules. Cite them as "Emil (external)", never as a
proving Studio Joe project. Where they collide with house conventions, the register below decides.

## The five files

| File | Covers | Emil skills distilled |
|---|---|---|
| `emil-design-eng-principles.md` | Animate-or-not frequency gate, easing/duration tokens, feel micro-rules, UI cheatsheet, animation vocabulary, curated library picks, Sonner | emil-design-eng, animation-vocabulary, pick-ui-library, ask-sonner, ui-cheatsheet |
| `emil-web-motion-recipes.md` | Component recipes, choreography (Lead/Support/Decoration casting, stagger budget), clip-path tricks, gesture two-phase model | animate, choreograph, gestures, find-animation-opportunities |
| `emil-motion-review-audit.md` | Review standards mapped to Critic/Pedant/Arbiter, removal gate tree, compositor tiers, jank diagnosis order, whole-project audit | review-animations, improve-animations, remove-animations, animation-performance, performance-cheatsheet |
| `emil-native-mobile-motion.md` | Five feel laws, Apple spring table, projection/rubber-band formulas, haptics budget, mobile-web fix table | apple-design, mobile-native, animate-expo (principles only), write-swift (design parts only) |
| `emil-break-ui-prototype.md` | Worst-case fixtures, failure-signature table, truncate/wrap rubric, G1–G3 reviewer gates, variant-picker method | break-ui, prototype |

**Canonical values:** the easing curves, duration table and press/scale numbers appear in several files (each slice
cited them). `emil-design-eng-principles.md` is the canonical copy; if they ever disagree, it wins.

**Not distilled — handed off:** write-swift's concurrency, Sendable, structured-concurrency and testing sections belong
to `swift-concurrency-pro`, `swift-testing-pro`, `swiftui-pro`, `swiftui-performance-audit`. Expo-only APIs were dropped.

## Arbiter rulings — divergence register

Most collisions dissolve once you notice **Emil's rules target interactive product UI chrome** (menus, popovers,
toasts, buttons, tabs, sheets — things touched many times a day), while Studio Joe's longer, bouncier numbers live on
**presentation and expressive surfaces** (decks, hero/ambient layers, celebrations, game juice). Ruling R0, applied below:
*Emil governs UI chrome; house conventions govern expressive surfaces.*

| # | Topic | Emil (external) | Studio Joe (house) | Ruling |
|---|---|---|---|---|
| 1 | Primary ease-out curve | `cubic-bezier(0.23, 1, 0.32, 1)` | `EASE_OUT = cubic-bezier(0.16, 1, 0.3, 1)` | **OPEN — human call.** Both are expo-style ease-outs; no evidence either is better. Until decided, keep the house token in SJ artifacts. |
| 2 | Duration ceiling | UI < 300 ms; press 100–160 ms | `DUR = 0.6` (decks), `durationSlow` 0.45 s (native) | R0. Emil's budget for UI chrome; house durations stay for decks/ambient. Emil himself allows longer marketing/deck motion. |
| 3 | Overshoot / bounce | Avoid in UI; bounce 0.1–0.3 only after a gesture | `back.out(1.5)` pops, wellness `elastic.out` | R0. No bounce on UI chrome unless released from a drag; pops/celebrations/wellness keep theirs. |
| 4 | `ease-in` | Never on UI | `comboShatter` `.5s ease-in` | Compatible: shatter is an effect exit, not a UI response. |
| 5 | Scale-from origin | Never `scale(0)`; popovers start ≥ 0.95 | Arcade cheer pop from `scale(.5)` | R0. Popovers/menus/modals ≥ 0.95; game juice exempt. |
| 6 | Stagger | 30–80 ms, never uniform, ~300 ms total | Uniform 0.06 s steps | Adopt Emil's for UI lists (0.06 s is inside the budget; non-uniform is a refinement). Decks unchanged. |
| 7 | Reduced motion | Gentler, not zero — keep comprehension fades, drop movement | Static final state / `animation: none` | **OPEN — human call.** Real disagreement. Emil's version is friendlier and opacity fades are generally not vestibular triggers, but the house rule is the stricter, safer default. |
| 8 | Engine | CSS transitions / WAAPI first (interruptible, can run off main thread) | GSAP-first | R0. GSAP stays for timelines and deck choreography; interruptible UI state (hover, press, toggle, popover) uses CSS transitions. Under main-thread load, prefer CSS/WAAPI for chrome. |
| 9 | Infinite loops | Reduce or run once | Arcade INSERT COIN / combo pulses loop | R0. Attract-mode and ambient loops are decoration by design; no infinite loops on UI chrome. |
| 10 | Native interactive spring | Damping 1.0 default; bounce only after momentum | `springSnappy` damping 0.78 | **OPEN — human call.** Feel decision; try both on device. |
| 11 | Viewport zoom / `user-select` | Never `user-scalable=no` / `maximum-scale=1`; `user-select: none` on controls only | Game boilerplate (`motion-game-ux.md` §11) sets both on the whole page | **OPEN — human call.** Proposed: keep for full-screen games (pinch-zoom breaks play), never on sites/tools/decks. Accessibility tradeoff, so not ruled unilaterally. |
| 12 | Tuning surfaces | Prototype pickers/dev toggles are deleted before ship | Sliders-first: bake chosen defaults into `controls[]` | Compatible: Emil's picker for discrete directions, house sliders for continuous params in the winner, then bake. Viz control panels that are a user feature may ship. |
| 13 | Reviewer action | Report findings, fix only on request | Builder QA gate fixes then re-verifies | Scope: our own Builder output → fix + verify; reviewing someone else's work → report. |
| 14 | Browser verification | Optional | Mandatory real Chrome + screenshot proof | House rule wins. |
| 15 | `touch-action` wording | "`pan-x` for a vertical drag" | — | Slice B suspected an inversion. Arbiter checked: correct as written (`touch-action` names the axis the browser keeps). |
| 16 | Swipe velocity units | `Math.abs(distance)/elapsedMs > ~0.11` | — | Confirmed px/ms from source (`emil-design-eng/SKILL.md` L443, `animate/RECIPES.md` L266). Motion's `info.velocity` is px/s, so its `> 500` example is a different scale. |

## UNVERIFIED

- Library maintenance/adoption claims from the source (download counts, version thresholds) were not checked.
- All GSAP, vanilla-CSS and SwiftUI translations in the five files are the distillers' own, not in Emil's source, and untested.
- `@starting-style`, middle-ellipsis, `Intl.Segmenter` and `line-clamp` support on SJ target browsers not checked.
- The Critic/Pedant mapping in `emil-motion-review-audit.md` is an inference; Emil's skills have no auditor roles.
- tvOS/macOS focus and pointer behavior: not covered by the source.

## License (required by MIT for substantial portions)

```
MIT License

Copyright (c) 2026 Emil Kowalski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
