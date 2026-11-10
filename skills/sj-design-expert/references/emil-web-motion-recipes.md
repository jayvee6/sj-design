# Web motion recipes, choreography + gestures (Emil Kowalski, external)

Distilled from emilkowalski/skills (MIT, © Emil Kowalski), commit 715c180.

Lens: motion language, choreography, enter/exit, gestures, springs, where animation earns its place. GPU/shader internals excluded.
Tags: **[any-web]** = CSS/WAAPI/GSAP-translatable, **[react-only]** = needs React + `motion` (Framer), **[native]** = concept transfers to SwiftUI, no code given in source.
Source codes: A = `skills/animate/SKILL.md`, AR = `skills/animate/RECIPES.md`, C = `skills/choreograph/SKILL.md`, CR = `skills/choreograph/RECIPES.md`, G = `skills/gestures/SKILL.md`, F = `skills/find-animation-opportunities/SKILL.md`.

---

## Sources read

All files read in full:

| File | Bytes |
|---|---|
| `skills/animate/SKILL.md` | 11910 |
| `skills/animate/RECIPES.md` | 7957 |
| `skills/choreograph/SKILL.md` | 15958 |
| `skills/choreograph/RECIPES.md` | 10147 |
| `skills/gestures/SKILL.md` | 8632 |
| `skills/find-animation-opportunities/SKILL.md` | 9808 |

Deduped against (read): `references/viz-motion-craft.md` (§7 wellness easing, §2 attack/release), `references/motion-game-ux.md` (§7 juice, §9 reduced motion), `references/studio-design-system.md` (§7 GSAP conventions, §8 transitions). Items already covered there are only cross-referenced, not re-explained.

Not read (out of slice): other Emil skills (`review-animations`, `improve-animations`, `pick-ui-library`, `animation-performance`, `animate-expo`), referenced by name only.

---

## Distilled patterns

### 1. The gate: does it animate at all? [any-web] [native]
Source: A "Build Sequence" step 1-2, F "The Gate".

| Frequency | Verdict |
|---|---|
| 100+/day (keyboard shortcuts, command palette) | No animation, ever. Keyboard-initiated = disqualifier, not judgment |
| Tens/day (hover, list nav) | Near-imperceptible only, or nothing |
| Occasional (modal, drawer, toast) | Standard |
| Rare / first-time (onboarding, success, celebration) | Delight budget lives here (only tier where bounce/generous stagger is OK) |

Purpose must be named: Feedback / Spatial consistency / State indication / Preventing a jarring change / Explanation (marketing only) / Delight (rare tier only). "Looks cool" on a frequent element = stop. Function check: data the user is reading or acting on must not move for style (A step 2, F gate 4).
F also requires a **rejected-candidates list** in any opportunity sweep (2-5 items, each citing the gate question that killed it) and caps suggestions at 5-7 per app.

### 2. Property and origin rules [any-web]
Source: A step 4.
- Animate `transform` + `opacity` only. `clip-path` is the sanctioned third (hold, tab indicator, reveal). `height` tolerated only for accordions.
- Never `scale(0)`: start `scale(0.9-0.97)` + `opacity:0` ("nothing appears from nothing"). Values in source: popover 0.95, tooltip 0.97, modal 0.96 (AR).
- `transform-origin` at the trigger for popovers/menus/tooltips (Base UI: `var(--transform-origin)`; vanilla: compute from trigger rect). **Modals stay centered**.
- `translate()` percentages (`translateY(100%)`) beat hardcoded px: relative to own size.
- Do not drive a child's transform from a parent CSS variable (restyles all descendants); write `transform` on the element (A step 4, G track rules, AR drag).
- Motion `x/y/scale` shorthand is hardware-accelerated only from motion 14.2+; a full `transform` string works in every version [react-only] (A).

### 3. Easing + duration tokens [any-web]
Source: A step 5.

```css
--ease-out:    cubic-bezier(0.23, 1, 0.32, 1);   /* enter/exit, default */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);  /* on-screen movement/morph */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);   /* iOS-like sheet */
```

| Situation | Easing | | Element | Duration |
|---|---|---|---|---|
| Enter / exit | ease-out | | Button press | 100-160ms |
| Move/morph on screen | ease-in-out | | Tooltip/small popover | 125-200ms |
| Hover / color | ease | | Dropdown/select | 150-250ms |
| Constant (marquee, progress, hold fill) | linear | | Modal/drawer | 200-500ms |
| Default | ease-out | | Marketing/explanatory | longer allowed |

Rules: UI under 300ms; never `ease-in` on UI (slow start delays the moment the user watches; ease-out at 200ms *feels* faster than ease-in at 200ms); built-in CSS easings "too weak"; curves not in the table come from easing.dev / easings.co, never hand-rolled. Extend the codebase's existing tokens, never fork a parallel set (A hard rule 3).
Other exact curves in source: tooltip/popover CSS use `--ease-out`; toast uses plain `ease` 400ms (AR); small floating drawer `cubic-bezier(0.165, 0.84, 0.44, 1)` 0.2s (G); resize-height `[0.25,1,0.5,1]` 0.27s, content swap `[0.26,0.08,0.25,1]` (CR); checkmark draw `cubic-bezier(0.645,0.045,0.355,1)` (CR).

### 4. Tool ladder (cheapest first) [any-web]
Source: A step 3.

| Need | Tool |
|---|---|
| Hover/press/toggle via class | CSS transition |
| Mount entry, no JS state | CSS `@starting-style` |
| Predetermined motion that must survive a busy main thread | CSS animation (off-main-thread; rAF JS drops frames during load) |
| Programmatic control, no library | WAAPI `element.animate()` |
| Springs, layout/exit animation, gesture-driven values | `motion` [react-only for the React API] |

GSAP is not in Emil's ladder. Translation: GSAP covers the last row for vanilla (tweens retarget via `overwrite`, drag via Draggable/Observer); not verified here (see UNVERIFIED).

### 5. Recipe card: press, popover, tooltip, modal, drawer [any-web]
Source: AR.

| Recipe | Exact values | Gotcha |
|---|---|---|
| Button press | `:active{transform:scale(0.97)}`, `transition: transform 160ms var(--ease-out)` | scale() scales children (label/icon), reads as physical. `:active` needs no hover gate |
| Popover/menu | enter/exit state `opacity:0; scale(.95)`, 200ms ease-out, origin = trigger | origin is the point |
| Tooltip | `scale(.97)`, 125ms ease-out; `[data-instant]{transition-duration:0ms}` | After first tooltip opens, neighbours open with zero delay and zero animation (initial delay prevents accidents; skip afterwards) |
| Modal | `scale(.96)` + opacity, 250ms ease-out, origin center | Animate backdrop opacity in same duration so they read as one surface |
| Drawer/sheet | `translateY(100%)`->0, 500ms `--ease-drawer` | Add drag and it becomes the gesture problem (section 9) |
| Accordion | `height`+`opacity` 200ms ease-out | Costs layout every frame: keep short; measure height in JS, never animate to `auto` |

Vanilla `@starting-style` replaces the `data-starting-style` attributes (those come from Base UI [react-only]); the CSS values carry over unchanged.

### 6. Toast and rapidly-triggered elements [any-web]
Source: AR toast, A step 6, G interruptibility.
- Toast: `opacity/translateY(100%)` in via `@starting-style`, 400ms plain `ease` (deliberately slower than the UI budget: "tuned to component personality"). Fallback if no `@starting-style`: set a `data-mounted` flag in an effect.
- **Transitions, not keyframes, for anything a user can fire twice in a second**: transitions retarget from the current value; keyframes restart from zero. (G cites Sonner's early keyframe enter making toasts jump when a second arrived.)
- Stacked-toast reflow: opacity change must fight height change; "no formula, adjust until it feels right, check again next day" (AR).
- Exit the way it entered (toast slides in from bottom, leaves via bottom; also what makes swipe-to-dismiss discoverable) (A step 6, G spatial consistency).

### 7. Choreography: cast, relate, budget [any-web] (concepts); variants/popLayout [react-only]
Source: C steps 1-5.

**Hard rules**
1. One entrance per container: panel slides, its content is already there. Never animate parent entrance AND stagger children.
2. No stagger on high-frequency / keyboard-opened UI (dropdown items, menu rows, palette, tab content).
3. Uniform stagger forbidden (metronome; "like `linear` easing for a group"). Vary delay, distance, duration by importance.
4. Choreography never blocks interaction: visible = clickable.
5. Every sequence must survive interruption.

**Cast roles** (do before writing any timing): Lead (moves first, travels most, stays longest) / Support (follows, shorter smaller) / Decoration (fade only or nothing) / Static (container, no motion). Two leads = hierarchy problem motion can't fix. Most groups shrink here.

**Relationship decision**: same object/moment -> TOGETHER; order without meaning -> TOGETHER (order without meaning is just delay); order meaningful and simultaneous would look broken -> SEQUENCE; meaningful but compatible -> OVERLAP (stagger); can't control child motion -> CARRY (animate the parent, e.g. images fall *into* a bin because the bin moves).

| Budget | Value |
|---|---|
| Product-UI stagger | 30-80ms between items, total under ~300ms; long lists: only first ~6 stagger, rest share the 6th's delay |
| Marketing/hero | 100-150ms steps on 0.5-0.6s entrances (seen once) |
| Hero example in source | `--step:120ms`, 0.6s `ease both`, rise 10px; title and first paragraph share beat 0 |
| Product exits | simultaneous, shorter, simpler; no reverse-stagger on close |

Lead/support/decoration example values (CR motion variants): lead 12px rise 0.5s, support 6px rise 0.4s, decoration fade 0.3s, all `[0.23,1,0.32,1]`; stagger step 0.06 with ease-out on the delays so gaps shrink.
Order follows importance not DOM order; direction follows reading order or outward from the interaction point.

**Together mechanics**
- Exiting element must leave layout at the moment of removal so siblings close the gap *while it fades*; otherwise a pause between fade and reflow makes it feel slow. Motion: `AnimatePresence mode="popLayout"` [react-only]. Vanilla: read offset, set `position:absolute` at that top/left (parent `relative`), animate out, let siblings FLIP/reflow (CR). GSAP Flip is the likely equivalent (untested).
- View swap in same container = crossfade (old exits while new enters), not sequential.
- Sub-animations of one component share a timing family (same duration, same easing family; inner curves may be lighter). Drawer 500ms + resize 200ms reads as two objects. Set once via `MotionConfig` or one CSS custom property.

**Sequence only when overlap looks wrong**: two dense states in a container resizing in both axes (`mode="wait"`; or duplicate-view crossfade, section 8); an element would visibly pass through another (time front-face reveal with a delay, not full sequence); cause-and-effect drawing (checkbox square then checkmark: second delay = first duration, `forwards`/`both`; start the second slightly early, 0.5s vs 0.6s, so it reads as one gesture).

**Sync secondary motion to the moment that matters**: background pulse on the *click*, not on hover; accent lines land in the last ~20% of the main timeline (`times:[0.7,0.9]`), main line first, others ~40ms behind; a repeat action skips the buildup (same proportions, earlier) (C step 3, CR).

### 8. Adaptive timing, direction, crossfade tricks
Source: C steps 4-5, CR, AR.
- **Scale duration by distance** [any-web]: container resize fade `clamp(0.15s, Δheight/500, 0.27s)`; big jump = full fade, tiny jump with same fade = flicker (CR).
- **Scale bounce by element size** [any-web]: smaller elements need more bounce; large views same bounce settle slower and feel heavy. With a small finite state set, hardcode per-transition values over a formula (C).
- **Direction follows mental model** [any-web]: Next moves content left (enters from right), Back reverses. Menu content enters from the side of the trigger the user came from. In Motion, `custom` must be passed to **both** `AnimatePresence` and the child or the exiting child uses the old direction [react-only]; vanilla equivalent: compute direction at click and write it to the outgoing element before animating it out. Exit matches entry (slid in from right -> leaves right, not just fade).
- **Small container / similar views**: swap the 110% slide for crossfade + 8px shift + light blur (CR).
- **Seam-masking blur** [any-web]: when a crossfade shows two objects, `filter: blur(2px); opacity:.7` on `.transitioning`, 200ms `ease`; keep blur under 20px (expensive, esp. Safari) (AR).
- **Duplicate-view crossfade** for two rich states: render the view twice; copy A animates enter only; copy B is `position:absolute`, opacity 0, visible only while exiting via keyframe; exit transform scales up if next state is larger, down if smaller, with `scaleX` pulling toward center when narrowing (CR). Hardcode per state pair.
- **Tab indicator via clip** [any-web]: duplicate the tab list styled as active, `clip-path: inset(0 60% 0 20%)` driven by active tab position, 250ms `--ease-in-out`; text and background change in perfect sync because it is one revealed element, not two interpolated colors (AR).
- **Scroll reveal** [any-web]: `clip-path: inset(0 0 100% 0)`->`inset(0)`, 600ms `--ease-in-out`, IntersectionObserver, fire once (`useInView {once:true, margin:"-100px"}`); marketing only (AR).
- **WAAPI example**: `element.animate([{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0)'}],{duration:1000,fill:'forwards',easing:'cubic-bezier(0.77,0,0.175,1)'})` (AR).

### 9. Gestures and drag feel [any-web] (physics concept); Motion API [react-only]; native: same two-phase model applies
Source: G, AR drag-to-dismiss.

**Two-phase model**: pointer down = TRACK (position maps 1:1, no easing/duration/spring, "element IS the finger"); pointer up = RELEASE (spring seeded with release velocity, never a keyframe).

| Phase | Rules |
|---|---|
| Track | Drive from motion values or direct `style.transform`; no React/framework state per pointermove; rubber-band at edges (`dragElastic` ~0.2, resistance rises with distance, friction not a wall) |
| Release | Spring with release velocity; dismiss on distance OR velocity; snap-back fast; bounce only after a drag (force applied), zero bounce when closed by button |
| Interrupt | Springs keep velocity if retargeted; keyframes cannot be caught. Never use keyframes on anything a gesture can touch |

Numbers (all from source): dismiss distance threshold ~40-50% of travel (G) / `SWIPE_THRESHOLD` constant unspecified (AR); flick velocity `Math.abs(swipeAmount)/timeTaken > 0.11` (px/ms, AR); Motion `onDragEnd` check `info.velocity.y > 500` (G, example); `dragMomentum` on by default (turn off for plain reposition).
Vanilla velocity: `const v = Math.abs(dy)/(Date.now()-dragStart)`; dismiss if `|dy| >= threshold || v > 0.11` (AR).
Drag details (AR): pointer capture once drag starts; multi-touch guard (`if (isDragging) return` on new touch points); damping past boundaries.
Linked values: derive overlay opacity from drag progress (`useTransform(y,[0,h],[1,0])`) so there is one source of truth and no drift when interrupted [react-only API; any-web: compute from the same pointer variable in one rAF-free handler].
Sheets: default to Vaul for bottom sheets (weeks of edge cases: momentum, overlay sync, velocity dismissal, focus trap, Escape). Vaul curve = `cubic-bezier(0.32,0.72,0,1)` 500ms (steep start = snappy + gentle settle); small floating (non-edge) drawer overrides to 0.2s `cubic-bezier(0.165,0.84,0.44,1)`; `data-vaul-no-drag` on interactive children.
Hold gestures: linear during hold (the animation visualizes time; any other curve lies), snap back fast ease-out on early release. Hold-to-confirm = `clip-path: inset(0 100% 0 0)` overlay, press 2s linear -> `inset(0)`, release 200ms ease-out, plus `scale(.97)` (AR/G).
Touch checklist (G): test on a real phone via local IP (60Hz desktop hides roughness a 120Hz phone shows); hit targets >= 44x44 using an invisible `::before` hitbox; `touch-action` set to the axis the BROWSER keeps (e.g. `pan-x` on a vertical-drag surface, so vertical moves reach your handler while horizontal scroll stays native) — Arbiter-checked 2026-11-10, source wording is correct; gate `:hover` with `@media (hover:hover) and (pointer:fine)`.
Weird spring -> raise `damping` first; stutter = perf problem (track-phase rules) not tuning.

### 10. Spring parameters [any-web via GSAP/WAAPI approximations; Motion API react-only; native: SwiftUI springs map by concept]
Source: A step 5, CR.
- Apple-style: `{type:"spring", duration:0.5, bounce:0.2}` (default for drag settle, interruptible gestures, "alive" elements, mouse-tracking).
- Physics: `{mass:1, stiffness:100, damping:10}`.
- Bounce range 0.1-0.3; "avoid bounce in most UI", reserve for drag-to-dismiss/playful. Step transitions use `bounce:0` (CR direction-aware example, `duration:0.5`).
- No source CSS/GSAP spring conversion given. GSAP `elastic`/`back` are not equivalents of Motion's duration+bounce spring; say so when translating.

### 11. Reduced motion and hover gating [any-web]
Source: A step 7, C "Reduced Motion", G.
- Reduced motion = **fewer and gentler**, not zero: keep opacity/color transitions that aid comprehension; remove translate/scale/position motion.
- Choreography under reduce: drop delays and movement, keep opacity, group appears together. If the sequence *is* the explanation, jump between frames.
- Gestures: tracking stays (direct manipulation); momentum flings, bounce, decorative extras reduce; settle with short opacity/position change.
- CSS stagger fallback: swap animation-name to opacity-only `fade`, `animation-delay:0ms` (CR).
- Hover motion gated by `@media (hover:hover) and (pointer:fine)`; ship both with the animation, not later (A hard rule 4).
- React: `useReducedMotion()`, e.g. `closedX = reduce ? 0 : '-100%'` [react-only].

### 12. CSS stagger, exact pattern [any-web]
Source: CR.
```css
.stagger > * { --step:120ms; animation: enter .6s ease both;
  animation-delay: calc(var(--step) * var(--i)); }
@keyframes enter { from { opacity:0; transform:translateY(10px); } }
```
`both` is required (`backwards` alone covers the delay; `forwards` keeps end state; `both` stops later items flashing final state first). Omit `to` so it animates to the element's own style. Per-item `--i` custom property: fine for one-shot entrance, not for per-frame values on big trees. GSAP: `stagger:{each:0.12}` plus `immediateRender` default on `from`/`fromTo` covers the flash problem (SJ pre-hide pattern already in studio-design-system §7).

### 13. Attention loops and idle [any-web]
Source: C "Attention Loops", CR useAnimate.
Idle invite (tapping hand, wiggle): first run after ~2.5s, `repeatDelay` ~6s, stops during interaction, resumes only after the reset animation finishes (`await Promise.all`). Gate click-after-buildup with a ref/plain variable, not render state. Always stop in-flight animations before starting new ones (never stack). Vanilla/GSAP: `tl.kill()` / `overwrite:'auto'`, `await tl.then()`.

---

## Reviewer checklist candidates

Each cites source; items already enforced by SJ references omitted.
- [ ] Every animation names a purpose from the allowed list and a frequency tier; nothing animates on 100+/day or keyboard-initiated actions (A, F).
- [ ] No `transition: all`; named properties only (A "Never Ship").
- [ ] No `scale(0)` entrances; start `scale(.9-.97)` + opacity (A).
- [ ] No `ease-in` on UI elements; built-in `ease-out` on deliberate motion replaced by the custom curve (A).
- [ ] Trigger-anchored popovers have transform-origin at trigger; modals centered (A).
- [ ] Rapid-fire elements (toasts, toggles) use transitions, not keyframes (A, G).
- [ ] No animation of width/height/margin/padding/top/left except accordion (A).
- [ ] Parent and children don't both animate entrance; list/menu rows on frequent surfaces have no stagger (C hard rules 1-2).
- [ ] Stagger is non-uniform (varied delay/distance/duration by role) and product-UI total stays under ~300ms (C).
- [ ] Items still being staggered are already clickable (C hard rule 4).
- [ ] Exiting items leave layout immediately (popLayout / absolute-before-exit); siblings reflow during, not after, the fade (C).
- [ ] Container resize + content swap share one timing family (C).
- [ ] Back/forward direction opposes; exits receive latest direction (`custom` on both) (C).
- [ ] Exits are simultaneous and simpler than entrances; exit mirrors entry axis (C, A, G).
- [ ] Re-trigger mid-sequence (hover-out, double Next, switch menu) stops in-flight animations; rapid view switch leaves one child mounted (C interruption).
- [ ] Dragged element tracks 1:1 with no spring/transition; no per-move framework state; transform written directly on element (G).
- [ ] Release uses velocity-seeded spring; dismiss checks distance OR velocity (G).
- [ ] Button-close has zero bounce; drag-release has small bounce (G).
- [ ] No keyframes on anything a gesture can touch (G).
- [ ] Hold gestures: linear during hold, fast ease-out cancel (G, AR).
- [ ] Reduced-motion variant is gentler not zero; hover motion gated to `(hover:hover) and (pointer:fine)` (A).
- [ ] Gesture and opacity roughness tested on a real 120Hz phone, and every non-trivial motion scrubbed at 2-5x duration / frame by frame, rechecked the next day (A output, G, C workflow).
- [ ] Opportunity sweeps include a Rejected list (F).

---

## Suggested decision-tree rows

| Task/question | Go to |
|---|---|
| Should this thing animate at all? / "make it feel more alive" | Distilled patterns §1 |
| Which easing and duration for a UI element? | §3 |
| CSS, WAAPI, GSAP, or a library? | §4 |
| Button press / popover / tooltip / modal / drawer values | §5 |
| Toast, or element the user can trigger rapidly | §6 |
| Staggering a list, hero entrance, multi-element sequence | §7, §12 |
| Element removed and siblings should close the gap | §7 (Together mechanics) |
| Swapping views / steps / tabs inside a container | §8 |
| Crossfade looks like two objects swapping | §8 (seam-masking blur, duplicate-view) |
| Drag, swipe-to-dismiss, bottom sheet, rubber-band | §9 |
| Spring numbers (bounce, duration, damping) | §10 |
| Reduced-motion or hover gating for a new animation | §11 |
| Idle/attention loop that invites a click | §13 |
| Review motion for restraint (find-opportunities style) | §1 + Reviewer checklist |

---

## UNVERIFIED

Divergences (recorded, not resolved):

| Topic | Emil says | Studio Joe says | Source |
|---|---|---|---|
| Primary ease-out | `cubic-bezier(0.23,1,0.32,1)` | `cubic-bezier(0.16,1,0.3,1)` "Apple expo-out" primary | A step 5 vs studio-design-system §7 |
| Default duration | UI under 300ms; 150-250ms typical | `DUR = 0.6` default | A vs studio-design-system §7 |
| Spring/bounce | bounce 0.1-0.3, avoid in most UI | `EASE_SPRING = back.out(1.5)` for "pop elements"; stats cards "spring up with scale" | A step 5 vs studio-design-system §7 |
| `ease-in` | never on UI | combo-shatter uses `.5s ease-in forwards` | A vs motion-game-ux §7e (arguably juice/exit) |
| `scale(0)`-like starts | never; start `.9-.97` | cheer pop starts at `scale(0.5)` | A vs motion-game-ux §7f |
| Reduced motion | gentler, not zero (keep opacity) | static final state, no animation; entrance stagger `animation:none` | A step 7 vs studio-design-system §15, motion-game-ux §9 |
| Stagger | 30-80ms, total ~300ms, never uniform | bullets stagger "one by one" (no numbers); level-up cards 0.06s uniform step | C vs studio-design-system §7, motion-game-ux §7d |
| Wellness / `linear` | linear only for constant motion/hold/progress; ease-in-out for on-screen moves | wellness: `power2.inOut` primary, `sine.inOut` holds, avoid `linear` | A vs viz-motion-craft §7 (mostly compatible; hold-fill linear is a different case) |
| Animation tool | CSS-first, WAAPI, library only for springs/layout | GSAP-first for all choreography | A step 3 vs studio-design-system §7 |
| Hover lift | gate hover motion by `(hover:hover) and (pointer:fine)`; tens/day hovers near-imperceptible | cabinet hover `translateY(-7px) scale(1.025)` (gating not confirmed in what I read) | A/F vs motion-game-ux §4 |
| Deck/marketing durations | marketing may exceed 300ms (compatible) | deck transitions 0.35-1.5s | A vs studio-design-system §8 |

Inferred or untested:
- GSAP translations (`stagger:{each, ease}` for non-uniform delays, `overwrite:'auto'`, GSAP Flip as `popLayout` equivalent, Draggable/Observer velocity) are my inference, not in source and not tested.
- Vanilla replacement for `var(--transform-origin)` (compute from trigger rect) and for `custom` direction passing is inference.
- `@starting-style` browser support not checked; Emil gives only the mount-flag fallback.
- ~~touch-action wording possibly inverted~~ — Arbiter ruling 2026-11-10: correct as written (`touch-action` names what the browser handles natively). Drag `SWIPE_THRESHOLD` value is unspecified in source.
- The `velocity > 0.11` is px/ms by construction in the snippet; `info.velocity.y > 500` is Motion's px/s; the two are not interchangeable and were not reconciled.
- Native/SwiftUI mapping is by concept only; source has no native code (Emil's `animate-expo` skill covers React Native and was not in this slice).
- Which Emil skills exist beyond this slice (`review-animations`, `improve-animations`, `pick-ui-library`, `animation-performance`) is known only from references inside the files read.
- "Delight/feel" judgments (stagger reads as wave, crossfade reads as one object) cannot be verified from code; source itself says to scrub recordings.
