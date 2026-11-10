# Design-engineering principles + library picks (Emil Kowalski, external)

Distilled from emilkowalski/skills (MIT, © Emil Kowalski), commit 715c180.

Tags: **[any-web]** = CSS/WAAPI/GSAP-translatable, **[react-only]** = needs React/library, **[native]** = SwiftUI-relevant (inferred translation, not in source).
Source abbreviations: `EDE` = `skills/emil-design-eng/SKILL.md`, `AV` = `skills/animation-vocabulary/SKILL.md`, `PUL` = `skills/pick-ui-library/SKILL.md`, `SON` = `skills/ask-sonner/SKILL.md`, `SON-API` = `skills/ask-sonner/API.md`, `CHEAT` = `ui-cheatsheet.md`.

---

## Sources read

| File | Lines | Notes |
|---|---|---|
| `EDE` | 676 | Read in full. Philosophy, animation decision framework, springs, components, transforms, clip-path, gestures, perf, a11y, Sonner principles, stagger, debugging, review checklist |
| `AV` | 181 | Read in full. Reverse-lookup glossary (vocabulary for naming effects), 14 groups |
| `PUL` | 85 | Read in full. Curated React-ecosystem library picks (`disable-model-invocation: true`) |
| `SON` | 88 | Read in full. Sonner (React toast lib) setup/recipes/troubleshooting |
| `SON-API` | 64 | Read in full. Toaster/toast() prop tables |
| `CHEAT` | 16 | Read in full. 11-row problem/solution table |
| Dedupe baseline | n/a | `studio-design-system.md` (§7 GSAP conventions, §15 reduced-motion, §16 copy rules) and `viz-motion-craft.md` (§7 wellness easing, §9 seekbar) read first |

Skill-mechanics notes (not design content): `EDE`, `AV`, `PUL`, `SON` each define an "Initial Response" one-liner when invoked with no question. `EDE` mandates a Before/After/Why **markdown table** for reviews (`EDE §Review Format`). `AV` says quote glossary verbatim, stay within glossary, lead with the term (`AV §Instructions`).

---

## Distilled patterns

### A. Should it animate? (frequency gate) [any-web] [native]

Source: `EDE §Animation Decision Framework 1-2`.

| Frequency of sight | Decision |
|---|---|
| 100+/day (keyboard shortcuts, command-palette toggle) | No animation, ever |
| Tens/day (hover, list nav) | Remove or drastically reduce |
| Occasional (modals, drawers, toasts) | Standard animation |
| Rare / first-time (onboarding, celebrations) | May add delight |

- Never animate keyboard-initiated actions (`EDE §1`; Raycast cited as having no open/close animation).
- Valid purposes only: spatial consistency, state indication, explanation, feedback, preventing jarring appear/disappear. "Looks cool" + seen often = don't (`EDE §2`).
- Decorative motion is fine only if decorative; functional data display (his example: banking graph) is better with none (`EDE §Spring-based mouse interactions`).
- Glossary names the same ideas: Purposeful animation, Frequency of use, Spatial consistency, Perceived performance (`AV §Principles to Know`).

### B. Easing selection [any-web]

Source: `EDE §Animation Decision Framework 3`.

| Situation | Easing |
|---|---|
| Entering or exiting | ease-out |
| Moving/morphing already on screen | ease-in-out |
| Hover / color change | `ease` |
| Constant motion (marquee, progress) | linear |
| Default | ease-out |

Custom curves (exact values, `EDE §3`): `--ease-out: cubic-bezier(0.23, 1, 0.32, 1)`; `--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1)`; `--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1)` (iOS-like, from Ionic).

- **Gotcha:** built-in CSS easings are "too weak"; use a custom curve. Never `ease-in` on UI: it delays the first movement, the moment the user watches hardest, so it feels slower at identical duration (`EDE §3`).
- Pick curves from easing.dev / easings.co, don't hand-build (`EDE §3`).
- Glossary adds: Asymmetric easing "feels more alive than a symmetric one"; linear reserved for spinners/marquees (`AV §Easing`).

### C. Duration budget [any-web]

Source: `EDE §Animation Decision Framework 4`.

| Element | Duration |
|---|---|
| Button press feedback | 100-160ms |
| Tooltips, small popovers | 125-200ms |
| Dropdowns, selects | 150-250ms |
| Modals, drawers | 200-500ms |
| Marketing / explanatory | can be longer |

- Rule: UI animation < 300ms. 180ms dropdown feels more responsive than 400ms; faster-spinning spinner reads as faster load (`EDE §4`, `§Perceived performance`).
- Asymmetric timing: slow where user is deciding, fast where system responds. Example: hold-to-delete press = 2s linear, release = 200ms ease-out (`EDE §Asymmetric enter/exit timing`). Review-table form: "make exit faster than enter" (`EDE §Review Checklist`).
- Cohesion exception: Sonner itself is deliberately a bit slower and uses `ease` not `ease-out` to feel elegant; match motion to component personality (playful = bouncier, dashboard = crisp) (`EDE §Cohesion matters`).

### D. Springs [react-only as written; any-web via GSAP/WAAPI approximation; native = SwiftUI springs]

Source: `EDE §Spring Animations`.

| Rule | Detail |
|---|---|
| Use for | drag with momentum, "alive" elements (Dynamic Island), interruptible gestures, decorative mouse-tracking |
| Two config styles | Apple-style `{ type:"spring", duration:0.5, bounce:0.2 }` (recommended) or physics `{ mass:1, stiffness:100, damping:10 }` |
| Bounce | keep 0.1-0.3; avoid in most UI; use for drag-to-dismiss and playful contexts |
| Interruptibility | springs keep velocity when interrupted; CSS keyframes restart from zero |
| Mouse-tracking | feed raw mouse value through a spring (`useSpring`, stiffness 100 / damping 10 in the example) instead of binding directly |

- **Translation note:** `useSpring`/`type:"spring"` are Motion (Framer) APIs [react-only]. Source gives no GSAP equivalent. Straightforward approximations: mouse-follow smoothing via `gsap.quickTo()` or a lerp in `gsap.ticker` [any-web, my translation, not in source]; interruptible tweens via GSAP `overwrite:'auto'` [UNVERIFIED]. Apple `duration`+`bounce` maps naturally to SwiftUI `.spring(duration:bounce:)` [native, inferred].
- Glossary terms for tuning vocabulary: Stiffness/Tension, Damping, Mass, Bounce, Perceptual duration, Momentum, Velocity (`AV §Spring Animations`).

### E. Interruptible UI: transitions over keyframes [any-web]

Source: `EDE §Use CSS transitions over keyframes`, `§Sonner Principles 5`.

- CSS transitions retarget mid-flight; keyframes restart from 0. Use transitions for anything triggerable rapidly (toast add, toggle).
- Entry without JS: `@starting-style { opacity:0; transform:translateY(100%) }` inside the rule; fallback is a `data-mounted` attribute set after mount (`EDE §@starting-style`).
- Percent translates: `translateY(100%)` = own height, size-independent; prefer over px (`EDE §translateY with percentages`).
- **Gotcha:** `@starting-style` support is browser-dependent; source says "when browser support allows" and gives no version table (see UNVERIFIED).

### F. Component feel recipes [any-web]

| Pattern | Rule | Source |
|---|---|---|
| Press feedback | `transform: scale(0.97)` on `:active`, range 0.95-0.98, `transition: transform 160ms ease-out`; applies to any pressable | `EDE §Buttons must feel responsive`; `CHEAT` |
| Never `scale(0)` entry | start `scale(0.95)` (>=0.9) + `opacity:0` | `EDE §Never animate from scale(0)` |
| Origin-aware popovers | `transform-origin` at trigger (Base UI: `var(--transform-origin)`); **modals stay centered** | `EDE §Make popovers origin-aware`; `CHEAT` |
| Tooltip skip-delay | delay first show; once one is open, adjacent ones open instantly with `transition-duration:0ms`; base transition 125ms ease-out, `scale(0.97)` start | `EDE §Tooltips` |
| Blur mask | `filter: blur(2px)` + opacity 0.7 during a crossfade that "feels off"; keep blur < 20px (Safari cost) | `EDE §Use blur to mask`; `CHEAT` |
| Stagger | 30-80ms between items, `translateY(8px)` + fade, 300ms ease-out; decorative, never block interaction | `EDE §Stagger Animations` |
| `scale()` scales children | font/icons scale with it; a feature | `EDE §scale() scales children too` |
| Opacity + height combo | for list enter/exit, pair them by trial; "no formula" | `EDE §opacity + height` |

### G. clip-path as an animation primitive [any-web]

Source: `EDE §clip-path for Animation`.

| Use | Recipe |
|---|---|
| Directional reveal | `inset(0 100% 0 0)` hidden to `inset(0 0 0 0)` visible |
| Hold-to-confirm | colored overlay at `inset(0 100% 0 0)`; `:active` -> `inset(0)` over **2s linear**; release 200ms ease-out; + `scale(0.97)` on the button |
| Seamless tab color change | duplicate the tab list styled "active", clip the copy to the active tab, animate the clip |
| Scroll image reveal | `inset(0 0 100% 0)` -> `inset(0)` on viewport entry (IntersectionObserver, `{once:true, margin:"-100px"}` analog) |
| Before/after slider | two stacked images, top clipped `inset(0 50% 0 0)`, drag edits the right inset |

- GSAP translation [any-web, mine]: GSAP tweens `clipPath` strings directly. Source's own programmatic example uses WAAPI: `el.animate([{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0 0)'}], {duration:1000, fill:'forwards', easing:'cubic-bezier(0.77, 0, 0.175, 1)'})` (`EDE §WAAPI`).

### H. Gesture / drag rules [any-web for pointer events; native for SwiftUI gestures]

Source: `EDE §Gesture and Drag Interactions`.

| Rule | Detail |
|---|---|
| Velocity dismissal | dismiss if `|distance|/elapsedMs > 0.11` OR distance >= threshold; a flick must be enough |
| Boundary damping | past a boundary, move less per px dragged (friction), never a hard wall ("Rubber-banding" in `AV`) |
| Pointer capture | capture pointer so drag continues outside element bounds |
| Multi-touch guard | ignore additional touches after drag starts (`if (isDragging) return`) |
| Test on real devices | USB phone + Safari remote devtools; Simulator is the fallback |

### I. Performance rules (animation-side only) [any-web]

Source: `EDE §Performance Rules`.

- Animate only `transform` + `opacity`; `padding/margin/width/height` trigger layout+paint (`§Only animate transform and opacity`; `AV` "Layout thrashing").
- **Gotcha (CSS vars):** setting a CSS variable on a parent recalcs all children's styles. For per-frame drag values write `element.style.transform` directly, not `setProperty('--swipe-amount')` (`§CSS variables are inheritable`).
- CSS/WAAPI animations run off the main thread and stay smooth during page load; rAF/JS (incl. Motion layout animations) drop frames. CSS for predetermined, JS for dynamic/interruptible (`§CSS animations beat JS under load`). Vercel tab-animation case study cited.
- Motion-specific [react-only]: shorthand `x/y/scale/rotate` hardware-accelerated from `motion` 14.2; before that use full `transform` string. `layout`/`layoutId`, `onUpdate`, `transformTemplate`, inertia, motion-value-driven drag stay main-thread in all versions (`§Motion hardware acceleration caveat`).

### J. Accessibility [any-web]

Source: `EDE §Accessibility`.

| Rule | Detail |
|---|---|
| Reduced motion != zero motion | keep opacity/color transitions that aid comprehension; remove movement/position. Example swaps slide for `animation: fade 0.2s ease` |
| Hover gating | wrap hover transforms in `@media (hover: hover) and (pointer: fine)`; touch fires hover on tap |
| Sonner a11y hooks | `hotkey` default `alt+T` focuses toast area; `containerAriaLabel` default `'Notifications'` (`SON-API`) |
| Seekbar-style aria | n/a (not in this slice) |

### K. Debugging motion [any-web]

Source: `EDE §Debugging Animations`.

- Slow-mo: temporarily 2-5x duration or DevTools Animations panel. Look for: two states visibly overlapping in color transitions, abrupt start/stop, wrong `transform-origin`, desynced opacity/transform/color.
- Frame-step in Chrome Animations panel.
- Re-review next day with fresh eyes (`§Review your work the next day`).

### L. UI micro-rules from the cheatsheet [any-web]

Source: `CHEAT` (all rows).

| Problem | Fix |
|---|---|
| Old timestamps "340 days ago" | absolute date after about a week |
| Jittering numbers | `font-variant-numeric: tabular-nums` (`AV` also lists Tabular numbers: "Essential for tickers, timers, counters") |
| Large headings look off | tracking about `-0.02em` |
| Body text line length | `max-width: 65ch` |
| Avatar squished to oval | `flex-shrink: 0` |
| Visible edge on gradient fade | eased gradient: extra stops along an ease curve |
| "1 members" | `Intl.PluralRules` |
| Dropdown sluggish / popover wrong origin / button unresponsive / transition off | see F, B, G above |

### M. Animation vocabulary (prompt-language) [any-web]

Source: `AV §Glossary` (14 groups; authoritative per its own rules). Most useful for briefing an AI/designer:

| Confusable pair | Distinction (paraphrased from `AV`) |
|---|---|
| Clip-path vs Mask | clip-path = hard shape; mask = soft/fadeable edges |
| Pop in vs Bounce | pop in = entrance with slight overshoot; bounce = spring overshoot-and-settle |
| Shared element transition vs Layout animation | shared = element travels between two positions/views; layout = element animates to its own new size/position instead of snapping |
| Morph vs Crossfade | morph = one shape becomes another (Dynamic Island); crossfade = fade over in same spot |
| Scroll reveal vs Scroll-driven animation | reveal = triggered on entering viewport; scroll-driven = progress tied to scroll position |
| Orchestration vs Stagger | orchestration = timing several animations as one motion; stagger = same animation cascaded by small delay |
| Idle animation vs Float vs Pulse | idle = any subtle waiting motion; float = soft up/down drift; pulse = repeating scale/opacity to draw attention |

- Principles list also names Anticipation, Follow-through, Squash & stretch as concepts (`AV §Principles to Know`) but gives no numeric guidance.
- Skill is name-only: "For naming an effect, not designing or building one" (`AV` frontmatter).

### N. Component-design philosophy (Sonner principles) [any-web, partly react-only]

Source: `EDE §The Sonner Principles`.

1. Zero-setup DX (mount once, call from anywhere). 2. Good defaults beat options (most users never customize). 3. Naming creates identity. 4. Handle edge cases invisibly: pause toast timers when tab hidden, fill gaps between stacked toasts with pseudo-elements so hover holds, capture pointer in drag. 5. Transitions not keyframes. 6. Docs site must be playable (interactive examples + copy-paste snippets).
- Related: "Beauty is leverage", "Unseen details compound", "Taste is trained" (`EDE §Core Philosophy`). Rhetorical, no rules to enforce.

### O. Toast system design (Sonner) [react-only library; pattern portable]

Source: `SON`, `SON-API`.

| Topic | Rule |
|---|---|
| Mounting | exactly one `<Toaster/>` at root; second mount duplicates every toast; `toast()` is client-only (call with server-action result) |
| Pick the call | plain / `.success|.error|.info|.warning` / `.loading` + update by `id` / `.promise(p,{loading,success,error})` / `{action:{label,onClick}}` (closes unless `preventDefault`) / `toast.custom` = headless |
| Update vs duplicate | same `id` updates in place; use stable `id` to survive StrictMode double-fire |
| Persist/dismiss | `duration: Infinity`; `toast.dismiss(id?)` |
| Close callbacks | `onDismiss` (close button or swipe) and `onAutoClose` (timeout) are separate; no single "closed" |
| Defaults | `duration` 4000ms, `visibleToasts` 3, `gap` 14, `offset` 32px, `mobileOffset` 16px (<600px), position `bottom-right`, `theme` `'light'` |
| Styling ladder | defaults+`richColors`/`invert` -> inline `style` -> `classNames` (needs `!important`) -> **headless `toast.custom`** (recommended end state for a design-system toast; wrap in own `toast()` abstraction) |
| Gotchas | `theme` does NOT track OS (set `"system"`); toast behind modal = ancestor stacking context (`transform/filter/overflow`), move Toaster to document root; unstyled in Astro/view-transitions = import `sonner/dist/styles.css`; Shadow DOM needs the `[data-sonner-toaster]` style tag copied in |

- Studio Joe relevance: only if a React project needs toasts (see Q). For vanilla artifacts, reuse the *behaviors* (single mount point, id-based update, hover-pause, hidden-tab pause, stable stacking) in a hand-rolled toast [any-web, my translation].

### P. Library-choice routing (curated list) [react-only unless noted]

Source: `PUL §The list`, `§How to use this`, `§Common mismatches`.

| Task | Pick | Portable to vanilla/Vite? |
|---|---|---|
| Accessible unstyled primitives | base-ui | react-only |
| Command palette | cmdk | react-only |
| Toasts | Sonner | react-only |
| OTP input | input-otp | react-only |
| Control panels | Leva (alt: dialkit) | react-only (Leva is pmndrs/React; note lil-gui already used in SJ viz repos, per `viz-motion-craft.md §5`) |
| General animation (springs, layout, enter/exit) | motion | JS core only; React API is react-only |
| Animated numbers | NumberFlow | source lists no vanilla build (UNVERIFIED) |
| Animated text | torph | UNVERIFIED |
| 3D globe | Cobe | UNVERIFIED if framework-agnostic |
| OG images HTML/CSS -> SVG/PNG | Satori | any-web/Node (server-side) |
| Syntax highlighting | shiki | any-web |
| Realtime charts / general charts | Liveline / recharts | react-only |
| Drag & drop / virtualization | dnd kit / Virtuoso | react-only |
| State / classNames / variants / theme | zustand / clsx / cva / next-themes | zustand+clsx framework-agnostic (UNVERIFIED); cva = Tailwind; next-themes = Next |

- Method rules: identify the **task** not the named library; check `package.json` first and don't churn existing competitors; recommend one library, no menu; say so explicitly when leaving the list (`PUL §How to use this`).
- Motion guard: "A simple hover or fade doesn't need [motion] — plain CSS transitions are the right tool" (`PUL §Motion & visuals`).
- Mismatch smells: hand-built toasts, `<div>` dropdown with manual focus, animating numbers by re-rendering text, 1,000+ row list unvirtualized, prop-drilled shared state, nested className ternaries (`PUL §Common mismatches`).

### Divergences from existing Studio Joe references (recorded, NOT resolved)

| Topic | Emil says | Studio Joe says | Source |
|---|---|---|---|
| Primary ease-out curve | `cubic-bezier(0.23, 1, 0.32, 1)` | `EASE_OUT = cubic-bezier(0.16, 1, 0.3, 1)` ("Apple expo-out") | `EDE §3` vs `studio-design-system.md §7` |
| Soft UI ease | built-in `ease` for hover/color; warns built-ins are weak | `EASE_SOFT = cubic-bezier(0.25, 0.46, 0.45, 0.94)` | `EDE §3` vs `§7` |
| Default duration | UI < 300ms; entries 150-250ms | `DUR = 0.6` (s) default; transitions 0.35-1.5s | `EDE §4` vs `studio-design-system.md §7-§8` |
| Spring/overshoot | bounce 0.1-0.3, "avoid bounce in most UI" | `EASE_SPRING = back.out(1.5)` for pop elements; stats cards "spring up with scale" | `EDE §Spring configuration` vs `§7` |
| Scale entrance origin | never from `scale(0)`; start >= 0.9-0.95 | stat cards "spring up with scale"; media frame "scales up from 95%" (consistent), watermark "scales behind" (start value not stated) | `EDE §scale(0)` vs `§7` table |
| Engine | prefer CSS transitions/WAAPI for interruptibility + off-main-thread; JS for dynamic | GSAP (`fromTo`, ticker-driven Perlin blobs) is the standard, pinned 3.12.5 | `EDE §Performance Rules` vs `§7, §13` |
| Entrance pattern | CSS `@starting-style`/transitions | pre-hide children `opacity:0` in CSS + GSAP `fromTo` | `EDE §@starting-style` vs `§7 Pre-hide` |
| Reduced motion | "fewer and gentler", keep opacity/color fades, drop movement | "static draws; reveals shown in final state immediately (no animation)" | `EDE §J` vs `§15` |
| Stagger delay | 30-80ms between items | not specified numerically in the existing reference (bullets "stagger one by one") | `EDE §Stagger` vs `§7` table (gap, not conflict) |
| Wellness easing | `ease-in-out` strong curve for on-screen movement; avoid `ease-in` | `power2.inOut` primary breath, `sine.inOut` holds, `elastic.out(1,0.45)` bounce-back; "avoid linear or bounce" | `EDE §3` vs `viz-motion-craft.md §7` (largely compatible; elastic is outside Emil's bounce range) |
| Linear easing | allowed only for constant motion + hold-press fill | Studio Joe checklist: avoid `linear` for wellness primary scale | `EDE §3, §G` vs `viz-motion-craft.md` checklist |
| Idle/ambient motion | frames "decorative" motion as OK only when rarely-seen/non-functional | ambient layers (gobos, bokeh, drift) always-on by design | `EDE §Spring-based mouse` vs `studio-design-system.md §6` |

---

## Reviewer checklist candidates

Use Emil's required output form: one markdown table, columns `| Before | After | Why |` (`EDE §Review Format`).

- [ ] No `transition: all`; list exact properties (`EDE §Review Checklist`)
- [ ] No `scale(0)` entrances; >= 0.9-0.95 + opacity
- [ ] No `ease-in` on UI; entering/exiting uses ease-out or custom curve
- [ ] No animation on keyboard-initiated or 100+/day actions
- [ ] UI duration <= 300ms unless modal/drawer/marketing
- [ ] Exit faster than enter; press-and-hold asymmetry respected
- [ ] Pressables have `:active` scale 0.95-0.98
- [ ] Popovers use trigger-based `transform-origin`; modals centered
- [ ] Hover animations gated by `@media (hover:hover) and (pointer:fine)`
- [ ] Rapidly-triggered UI uses transitions (interruptible), not keyframes
- [ ] Only `transform`/`opacity` animated; per-frame drag writes `transform`, not a parent CSS var
- [ ] Stagger 30-80ms and non-blocking
- [ ] Blur used as a crossfade mask is < 20px
- [ ] Reduced-motion variant keeps comprehension fades, drops movement (flag: conflicts with SJ static-final-state rule; decide per project)
- [ ] Changing numbers use `tabular-nums`; headings tracking about -0.02em; body `max-width: 65ch`
- [ ] Drag-dismiss has velocity path (about 0.11 px/ms), pointer capture, multi-touch guard
- [ ] Animation reviewed in slow-mo / frame-step before sign-off
- [ ] (React projects only) one Toaster mounted, `theme` wired to app theme, Toaster outside modal stacking contexts
- [ ] (React projects only) library choice checked against `package.json` before adding a competitor

---

## Suggested decision-tree rows

| Task/question | Go to |
|---|---|
| "Should this animate at all?" / keyboard-driven UI | Distilled patterns §A |
| "Which easing for this element?" | §B (and Divergences row 1-2) |
| "How long should it take?" | §C (and Divergences row 3) |
| "Springy / alive / draggable feel without a React lib" | §D translation note |
| "Rapid toggles feel janky / animation restarts" | §E |
| "Button / popover / tooltip feels off" | §F |
| "Reveal, wipe, tab color transition, before/after slider, hold-to-confirm" | §G |
| "Swipe-to-dismiss / drag thresholds" | §H |
| "Animation drops frames during load" | §I |
| "Reduced motion / touch hover audit" | §J (and Divergences row 8) |
| "Animation looks wrong, can't see why" | §K |
| "Numbers jitter / heading looks off / timestamp copy" | §L |
| "What is this motion effect called? / write a motion brief" | §M |
| "Design a loved reusable component" | §N |
| "Add toasts / notifications" | §O; if vanilla, adapt behaviors only |
| "Which library for X?" (React project only) | §P |
| "Review UI code, output format" | Reviewer checklist candidates |
| "Emil vs our GSAP/easing conventions" | Divergences table |

---

## UNVERIFIED

- **Library maintenance, versions, adoption**: source claims Sonner has "13M+ weekly npm downloads" (`EDE §Sonner Principles`); not checked. `motion` 14.2 hardware-acceleration threshold is stated by source only; not verified against Motion changelogs. No maintenance status checked for any `PUL` entry (Liveline, torph, dialkit, Cobe, NumberFlow, etc.).
- **Framework-agnostic status** of NumberFlow, torph, Cobe, zustand, clsx: `PUL` does not say; my "vanilla-portable?" column is inference, not read.
- **GSAP equivalents** of Emil's spring recipes (`gsap.quickTo`, `overwrite:'auto'`, `clipPath` tweening) are my translations, not in the source. Sonner behaviors (hover-pause, hidden-tab pause) are described by source; re-implementation guidance is mine.
- **`@starting-style` browser support** and `transition-behavior`: source says "when browser support allows" and gives no matrix.
- **Apple spring param mapping to SwiftUI**: inferred from "Apple's approach" wording (`EDE §Spring configuration`); source never mentions SwiftUI.
- **Velocity threshold 0.11** is from Sonner code in the source snippet (px/ms, units inferred from `distance / milliseconds`); not validated for touch vs mouse or other UIs.
- **Duration/curve numbers** are Emil's personal taste, presented in source as rules, not measured; no user-testing evidence in the source.
- **Divergences** are comparisons against the two existing references only; actual project code (templates, `transitions.js`) not re-read, so some Studio Joe rows rely on the existing references' accuracy.
- **Not in this slice / not read**: other skills in the repo (e.g. any additional reference docs), Emil's `/vocabulary` page that `AV` claims to mirror, and his course material.
