# Native & mobile motion feel (Emil Kowalski, external)

Distilled from emilkowalski/skills (MIT, © Emil Kowalski), commit 715c180.

**Lens:** Apple design conventions, touch UX, native motion feel (springs, interruptibility, gestures, haptics), mobile-web fixes.
**Excludes:** GPU/Metal internals; Swift code-correctness (handed off, see end of Distilled patterns).
**Tags:** `[native-swiftui]` applies to SwiftUI apps as-is or via direct translation. `[mobile-web]` applies to touch-first web games/pages. `[expo-only]` dropped (API detail not kept).
**Note on source nature:** `apple-design` is Apple WWDC talks *translated for the web*; spring/velocity numbers are Apple's, the code is web (Motion/Pointer Events). Native-SwiftUI mapping of those numbers is flagged where it is my translation.

---

## Sources read

| Path (under `skills/`) | Lines | What it covers |
|---|---|---|
| `apple-design/SKILL.md` | 290 | WWDC fluid-interface principles: response, direct manipulation, interruptibility, springs (damping/response), velocity handoff, momentum projection, rubber-band, materials, multimodal feedback, reduced motion/transparency/contrast, type tracking/leading, Apple's 8 design principles |
| `mobile-native/SKILL.md` | 311 | Web-on-phone fix table: sticky hover, tap highlight, dvh/svh, 16px inputs, tap latency, overscroll, safe-area, user-select, touch-action, theme-color, real-hardware testing, baseline + never-ship |
| `animate-expo/SKILL.md` | 263 | Build sequence (frequency gate, purpose, tool, properties, spring-vs-timing, thread, press, haptics, reduced motion). Read in full; only platform-agnostic principles kept |
| `animate-expo/RECIPES.md` | 385 | Press feedback, drag-dismiss sheet, swipe-delete, collapsing header, list entrance, keyboard-synced UI, tab indicator, screen transitions, toast, threshold-fire. Only the gesture-feel logic kept |
| `write-swift/SKILL.md` | 396 | Swift language/concurrency/perf/testing. Read in full; **not distilled** (see hand-off list) |

Dedupe baseline read: `references/apple-native-design.md` (P7 StudioJoeMotion tokens, P6 chrome auto-hide, P11 a11y) and `references/motion-game-ux.md` (§2 touch, §9 reduced motion, §11 viewport boilerplate). Sibling skill descriptions skimmed: swiftui-pro, swiftui-ui-patterns, swiftui-liquid-glass, swiftui-performance-audit, swift-concurrency-pro.

---

## Distilled patterns

### N1. The five "feel" laws (gotcha-first: what makes an interface feel dead)

| # | Law | Gotcha it prevents | Tag | Source |
|---|---|---|---|---|
| 1 | **Respond on touch-down, commit on touch-up** | Feedback only on release reads as lag even at 0 ms | both | apple-design §1, §10; mobile-native §5 |
| 2 | **1:1 tracking, respect grab offset** | Snapping element center to finger on grab breaks directness | both | apple-design §2 |
| 3 | **Everything interruptible; animate from the *presentation* (live on-screen) value, never the target** | Starting from the logical value = visible jump on re-grab | both | apple-design §3; RECIPES drag-dismiss (`onStart` captures current value) |
| 4 | **Hand release velocity to the spring** | Seam between finger-release and animation ("fine" vs "fluid") | both | apple-design §5; RECIPES sheet |
| 5 | **Project momentum, decide by velocity not distance** | Distance-only dismissal makes sheets feel heavy; a flick should be enough | both | apple-design §6; animate-expo Never-Ship row |

Also: never lock out input during a transition; decompose 2D motion into independent X and Y springs (single spring on 2D distance desyncs); at a reversal, blend velocity rather than hard-cutting ("brick wall"). Source: apple-design §3.
Avoid fixed-duration CSS transitions/keyframes for anything gesture-driven (cannot be grabbed and reversed). `[mobile-web]` apple-design §3.

### N2. Spring parameters (exact values from source)

Apple's two designer parameters: **damping ratio** (1.0 = critically damped, no overshoot; <1 overshoots) and **response** (seconds to reach target; *not* a duration). Source: apple-design §4.

| Interaction | Damping | Response | Source |
|---|---|---|---|
| Move / reposition (e.g. PiP) | 1.0 | 0.4 | apple-design §4 table |
| Rotation | 0.8 | 0.4 | apple-design §4 table |
| Drawer / sheet | 0.8 | 0.3 | apple-design §4 table |
| Default UI settle | 1.0 | 0.3–0.4 | apple-design Quick Reference |
| Momentum/flick landing | ~0.8 | 0.3–0.4 | apple-design Quick Reference |

Rules: start at damping **1.0**; add bounce (~0.8) **only when the gesture carried momentum** (flick/throw/release). Overshoot on a menu that just faded in is wrong; on a flicked card it is right. (apple-design §4; animate-expo §5.)
Sheet dismissal: use damping 1.0 + overshoot clamped (otherwise the sheet springs past the screen edge and flashes a gap); snap-back uses 0.8 + release velocity (RECIPES drag-dismiss: duration 300).
`[native-swiftui]` SwiftUI's spring is natively response/dampingFraction, so these numbers map directly (my translation; see UNVERIFIED).

### N3. Momentum projection + rubber-band (formulas as shipped in source)

```
project(v_px_per_s, d=0.998) = (v/1000) * d / (1 - d)     // d 0.998 normal, 0.99 snappier
target = nearestSnap(position + project(releaseVelocity))
relativeVelocity = gestureVelocity / (target - current)    // only for APIs wanting relative velocity
rubberband(overshoot, dim, c=0.55) = (overshoot*dim*c) / (dim + c*|overshoot|)
```
Gotchas: the textbook `v²/(2·decel)` is NOT what Apple ships. Reverse-vs-commit decided by velocity **sign**, not position. Hard stops at edges read as "frozen"; use progressive resistance. Sources: apple-design §5, §6, §9, Quick Reference; RECIPES "Two worklets".
`[native-swiftui]` the 0.998 constant is described in source as from Apple's *Designing Fluid Interfaces* sample code. `[mobile-web]` use same formulas in Pointer-Events handlers.

### N4. Gesture arbitration & thresholds

| Rule | Value / detail | Tag | Source |
|---|---|---|---|
| Direction-commit hysteresis before tracking | ~10 px | both | apple-design §10; RECIPES (`activeOffsetY/X [-10,10]`) |
| Tap hit padding / cancel-by-drag-away-and-back | ~10 px hysteresis | both | apple-design §10 |
| Detect all plausible gestures in parallel from first move, cancel losers when intent is clear | avoid recognizers that only report a final state (`swipeleft`) | both | apple-design §10 |
| Declare the pan axis, or a pan inside a scroll view steals vertical scroll and looks like a scroll bug | | both | RECIPES swipe-delete |
| Double-tap detection delays single taps; pay only where double-tap exists | | both | apple-design §10 |
| Hint in gesture direction: in-between frames should telegraph the outcome | | both | apple-design §8 |

### N5. Spatial consistency

- Enter and exit along the **same path**; in-from-right must dismiss to the right. Anchor menus/popovers/sheets to the trigger (`transform-origin` = trigger, not center). Mirror easing on reversible transitions (inverse cubic-bezier). apple-design §7.
- Toast: exits the way it entered; exit ~20% faster than entry; honors bottom safe-area inset. RECIPES Toast. `[both]`
- Custom `animation` on a pushed screen: make the back-swipe run the same transition in reverse under the finger, or drag-back looks like a different app. RECIPES Screen transitions (Expo-specific option name dropped). `[native-swiftui]` principle only.

### N6. Frequency gate (should this animate at all?)

| Frequency | Decision | Source |
|---|---|---|
| 100+/day (tab switch, keyboard, scroll, settings toggles) | No animation | animate-expo §1 |
| Tens/day (press feedback, row select) | <150 ms or nothing | animate-expo §1 |
| Occasional (sheets, modals, toasts, onboarding) | Standard | animate-expo §1 |
| Rare / first-time (success, celebration) | Delight budget | animate-expo §1 |

Gotchas: **Tab switches never slide** (peers, not hierarchy; pays cost dozens of times/session). Name the purpose in one word (feedback, spatial consistency, state indication, preventing jarring change, explanation, delight) or don't build it. Entrance animation is for content the user asked for and waits on, not lists they scroll past all day. animate-expo §1–2, RECIPES List entrances. `[both]`

### N7. Timing values, easing, press feedback

| Item | Value | Source |
|---|---|---|
| Press feedback | 100–150 ms, `scale(0.97)`, ease-out | animate-expo §5/§7; mobile-native §5 (100–160 ms) |
| Toggle/chip/small state | 150–200 ms | animate-expo §5 |
| Sheet/modal/drawer | spring, ~300 ms perceived | animate-expo §5 |
| Mobile UI animations | stay under 300 ms; navigation = platform default (iOS push 350 ms), beat the platform everywhere else | animate-expo §5 |
| Strong ease-out (UI enter/exit) | cubic-bezier(0.23, 1, 0.32, 1) | animate-expo §5 |
| On-screen move/morph | cubic-bezier(0.77, 0, 0.175, 1) | animate-expo §5 |
| iOS sheet curve | cubic-bezier(0.32, 0.72, 0, 1) | animate-expo §5 |
| Stagger | 30–80 ms (longer = slow, shorter = simultaneous) | RECIPES List entrances |
| Never | `ease-in` on UI (delays the moment the user is watching); `scale(0)` entrances (use 0.9–0.97 + opacity 0) | animate-expo §4–5 |

Rule: if a finger was involved, use a spring; otherwise timing. animate-expo §5. `[both]`

### N8. Haptics (timing + budget rules; API names dropped)

| Moment | Weight | Source |
|---|---|---|
| Value ticks past a step (picker, slider detent) | selection tick | animate-expo §8 |
| Snap home / detent catches / drag commits | light impact | animate-expo §8 |
| Heavy landing / destructive action | medium impact | animate-expo §8 |
| Success / failure | notification success / error | animate-expo §8 |

Absolute rules: (1) **same frame as the visual, at the causal moment** (detent catching, not animation end); (2) **one per user action**, never per frame, never on scroll, never on an entrance the user did not cause; (3) **never the only feedback** (off system-wide for many users). Fire on press for a tab indicator, not when it lands. Threshold haptic fires once on crossing (arming a pull-to-refresh), not polled. animate-expo §8, RECIPES. Multimodal "Harmony": visual, sound, haptic on the same frame; "Utility": reserve for meaningful moments. apple-design §13. `[native-swiftui]` `[mobile-web]` (web Vibration API only mentioned, apple-design §13).

### N9. Materials & depth (principles; web CSS shown in source)

| Rule | Source |
|---|---|
| Translucent layers with content scrolling underneath, not opaque bars | apple-design §12 |
| Material weight = hierarchy: heavier for structure (sidebars), lighter for interactive elements; **never stack a light translucent surface on another** | apple-design §12 |
| Bigger surface reads thicker: stronger blur + deeper shadow | apple-design §12 |
| Modal = dim scrim + push background back; parallel panel = translucency + offset, **no scrim** | apple-design §12 |
| Over translucency: higher-contrast, slightly heavier text with small tracking bump, not flat gray; put color on a solid layer | apple-design §12 |
| Scroll-edge fade/blur mask instead of a 1 px divider, only where floating chrome overlaps content | apple-design §12 |
| "Materialize": animate blur radius and scale together on enter/exit, not plain opacity | apple-design §12 |
| Bright top-edge border = light catching the material (source CSS: `rgba(255,255,255,.4)` 1 px top) | apple-design §12 |

`[native-swiftui]` principles feed glass-tier choice; API usage belongs to swiftui-liquid-glass.

### N10. Reduced motion / transparency / contrast

| Signal | Response | Source |
|---|---|---|
| reduce motion | gentler, **not zero**: keep opacity/color that explain state, drop translation/scale/parallax/overshoot; screen transitions become fade | apple-design §14; animate-expo §9 |
| reduce transparency | raise bg opacity, drop blur (frostier/solid) | apple-design §14 |
| increase contrast | near-solid bg + defined contrasting border | apple-design §14 |
| Also | avoid full-viewport moving backgrounds, slow loops near 0.2 Hz (one cycle per 5 s), abrupt brightness jumps (ease dark/light changes); large moving objects semi-transparent while traveling | apple-design §14 |
| Text scales | never animate to a hardcoded height; measure or animate a transform | animate-expo §9 |

### N11. Mobile-web symptom table (verbatim-minimal; all `[mobile-web]`)

| Symptom | Fix | Why (source) |
|---|---|---|
| Hover stuck after tap | wrap `:hover` in `@media (hover:hover) and (pointer:fine)` | touch fakes a sticky hover (mobile-native §1) |
| Gray/blue flash on tap | `-webkit-tap-highlight-color: transparent` globally, then give every tappable its own `:active` | removes the only feedback the browser gave (§2) |
| Wrong height | `100dvh` app shell, `100svh` hero; `100vh` = largest viewport; `lvh` almost never | URL bar overflow; dvh mid-scroll shifts marketing content (§3) |
| Page zooms into input | input font-size >= 16 px (can gate with `pointer:coarse`); set `inputmode`, `enterkeyhint`, `autocapitalize` | iOS zooms <16 px and does not zoom back (§4) |
| Laggy tap | `touch-action: manipulation` + press feedback on `pointerdown`/`:active` | 300 ms double-tap-zoom wait + release-only feedback (§5) |
| Pull-to-refresh/rubber-band hijack | `overscroll-behavior:none` on html/body, `contain` on inner scrollers; never `touchmove`+`preventDefault` | passive-listener cost (§6) |
| Content under notch | `viewport-fit=cover` + `env(safe-area-inset-*)` (all 0px without the meta) | §7 |
| Long-press selects button text | `user-select:none` + `-webkit-touch-callout:none` on **controls only**, never body | §8 |
| Carousel scrolls vertically | `touch-action: pan-y` (horizontal carousel), `none` (custom gesture owns all axes), `pan-x` (vertical sheet handle); native scroll-snap beats hand-rolled spring | values name what the *browser* may still do (§9) |
| Status bar mismatch | `theme-color` per `prefers-color-scheme`, match top-of-page color; `interactive-widget=resizes-content` for keyboard | §10, Baseline |
| Right in Chrome, wrong on phone | test on real hardware, older phone, keyboard open, landscape, installed-PWA mode | emulation misses sticky hover, tap delay, safe areas, keyboard (§11) |

Hard rules from source: media queries over UA sniffing; touch and mouse are not exclusive (iPad trackpad, touchscreen laptops); **never disable zoom** (`user-scalable=no` / `maximum-scale=1`). mobile-native Hard Rules.

### N12. Press / hit-target rules

- **44x44 pt minimum target** (48 dp Android); if visual is smaller, expand hit area, do not grow the visual. Allow a finger drifting a few px without cancelling the press. animate-expo §7. `[both]`
- Same scale-press on every platform is more coherent than a Material ripple in a custom-designed app. animate-expo §7. `[both]`
- Prefer the platform's own sheet/tab bar/context menu/large-title/pull-to-refresh over rebuilding; hand-roll only for a signature interaction. animate-expo §3 table (Expo component names dropped). `[native-swiftui]` principle.
- Keyboard-following UI must be driven by the keyboard's real position frame by frame; a fixed-duration animation fired on the keyboard event visibly lags or leads (private system curve). RECIPES Keyboard. `[both]`

### N13. Performance gotchas that are platform-agnostic

- Animate only transform + opacity; `width/height/margin/top/left` trigger layout every frame (exception: absolutely positioned childless element, e.g. tab-pill, keeps corner radius that scaleX would smear). animate-expo §4. `[mobile-web]` (`[native-swiftui]` analog is UNVERIFIED).
- Collapsing header: fixed-height container, translate content, clip; clamp interpolation (otherwise opacity goes negative and header reappears inverted). RECIPES. `[both]`
- Entrance animation on recycled/virtualized rows re-fires on scroll-back and flickers; animate container once or animate reflow only. RECIPES. `[both]`
- Animating blur intensity or shadow/elevation per frame is costly on Android; crossfade a static pre-rendered layer. animate-expo §4 (Android-specific). `[mobile-web]` low relevance.
- Smoothness is what is in the frames: keep per-frame positional delta under the strobing threshold; subtle motion blur/stretch for very fast motion. apple-design §11.
- Judge feel on a release build on the slowest supported device, not simulator/dev build. animate-expo Hard Rule 5. `[both]`

### N14. Apple's 8 design principles (naming vocabulary) + tactical rules

Purpose, Agency (undo over confirmation dialogs; confirm only genuinely destructive), Responsibility, Familiarity (identical things behave and live identically; break a pattern only if proven and tested), Flexibility, Simplicity (not minimalism), Craft (every value defensible; iterate), Delight (outcome of the other seven). apple-design §16 (cites WWDC 2026 session). Tactical: four feedback kinds (status, completion, warning, error); validate inline not on submit; every screen answers where am I / where can I go / what's there / how do I get out; proximity implies grouping; name nav items for contents ("Library") not umbrellas ("Home"). `[native-swiftui]`

### N15. Type: size-specific tracking/leading (Dynamic Type adjacent)

Large display text wants negative tracking, small text slightly positive; leading tightens as size grows; hierarchy from weight+size+leading together; default to system font (optical sizing already tuned); scale spacing with text size. Source CSS example: display `line-height:1.05; letter-spacing:-0.02em`; body near 0. apple-design §15. `[native-swiftui]` `[mobile-web]`

### N16. Process

Prototype interactively; design interaction and visuals together; review motion in slow motion/frame-by-frame; test with real people. apple-design §17. Feel items (flick, interrupt mid-flight, reverse, haptic timing) cannot be judged from code. animate-expo Output.

### Divergences (recorded, NOT resolved)

| Topic | Emil says | Studio Joe says | Source |
|---|---|---|---|
| Interactive-control spring | Start at damping 1.0; bounce only after a momentum gesture | `springSnappy` = response 0.28, damping 0.78 for "interactive controls" (bouncy by default) | apple-design §4 vs apple-native-design.md P7 |
| Duration ceiling | Mobile UI animations stay under 300 ms | `durationSlow` 0.45 s for large movements; `springSmooth` response 0.45; Ripple 1.2 s/5.0 s (declared meditative exception) | animate-expo §5 vs apple-native-design.md P7 |
| Press/small-change timing | Press 100–150 ms, toggle 150–200 ms | `durationFast` 0.18 s for taps/toggles; hover row 0.12 s | animate-expo §5 vs apple-native-design.md P5/P7 (near-overlap; flagged for token review) |
| Viewport zoom | Never `user-scalable=no`/`maximum-scale=1`; fix with 16 px inputs | Game boilerplate sets `maximum-scale=1,user-scalable=no,viewport-fit=cover` | mobile-native Hard Rule 4 vs motion-game-ux.md §11 |
| Reduced-motion swap | Fewer/gentler, not zero: keep explanatory opacity/color; replace slides with cross-fade | `reduceMotion ? nil : animation` = instant snap; spring swapped for instant or opacity-only | apple-design §14 vs apple-native-design.md P7 (partially aligned) |
| `body` selection | `user-select:none` only on controls, never body | Game boilerplate sets `user-select:none` on `html, body` | mobile-native §8 vs motion-game-ux.md §11 (games have no copyable content; context differs) |
| Tab-bar transitions | Tabs never slide (`none`) | Not stated in dedupe files (no row); noted so reviewers can add | animate-expo §1 |
| Fixed-duration chrome fade | Gesture-driven things need springs, avoid fixed-duration | `ChromeAutoHide` uses `.easeInOut(0.22)` opacity (not gesture-driven; likely compatible) | apple-design §3 vs apple-native-design.md P6 |

### Hand-off: write-swift (NOT distilled; Swift code-correctness)

| write-swift section | Hands off to |
|---|---|
| §3 Concurrency progression, `@concurrent`, `nonisolated`, Approachable Concurrency / main-actor-by-default, actor reentrancy | swift-concurrency-pro |
| §4 Sendable, data-race fixes, `@unchecked Sendable`, `nonisolated(unsafe)`, delegate bridging | swift-concurrency-pro |
| §5 Structured concurrency, task groups, cancellation, continuations, AsyncStream | swift-concurrency-pro |
| §6 Concurrency in SwiftUI (`@Sendable` closures like `visualEffect`, sync callbacks for same-frame animation state change) | swiftui-pro + swift-concurrency-pro |
| §9 Performance (ARC traffic, `InlineArray`, `Span`, existential cost, algorithmic cost) | swiftui-performance-audit (UI side); swift-concurrency-pro not applicable, no Swift-perf skill found |
| §1 value types, §2 errors, §7 protocols/generics, §8 API design, §10 ARC lifetime, §12 macros, §13 Logger, §14 unsafe/interop, §15 modern syntax, §16 Swift 6 migration | swiftui-pro (modern API) / no dedicated owner found |
| §11 Swift Testing (`@Test`, `#expect`, parameterized, exit tests) | swift-testing-pro (listed in available skills; description not read here) |

---

## Reviewer checklist candidates

- [ ] Feedback fires on **press-down**, not on release/click? (`:active`/`pointerdown`, or SwiftUI pressed-state style) [N1]
- [ ] Anything a finger drags tracks 1:1, respects grab offset, and can be **re-grabbed mid-animation** without a jump? [N1]
- [ ] Release **velocity is passed** into the settling spring; dismiss/commit decided by projected endpoint or velocity, not distance only? [N1, N3]
- [ ] Default springs are damping 1.0; any bounce is justified by a preceding momentum gesture? (cross-check against StudioJoeMotion `springSnappy` 0.78 divergence) [N2]
- [ ] Edges rubber-band instead of hard-stop? [N3]
- [ ] Enter and exit paths symmetric; popover/menu origin is the trigger? [N5]
- [ ] Tab/peer navigation does not slide; high-frequency actions (100+/day) have no animation? [N6]
- [ ] No `ease-in` on UI; no `scale(0)` entrance; mobile UI animations <=300 ms (or documented exception like Ripple)? [N7]
- [ ] Haptic: one per user action, same frame as visual, causal moment, never sole feedback, never on scroll/entrance? [N8]
- [ ] No light translucent surface stacked on another; scrim only for modal tasks? [N9]
- [ ] Reduce-motion path keeps explanatory opacity/color (not blanket instant); reduce-transparency and increased-contrast also handled? [N10]
- [ ] Hit targets >= 44 pt with expanded hit area rather than grown visual? [N12]
- [ ] Hover styles gated by `(hover:hover) and (pointer:fine)`; tap-highlight cleared and replaced by `:active`? [N11]
- [ ] `100dvh` for shells, `100svh` for heroes; inputs >= 16 px; `viewport-fit=cover` present wherever `env(safe-area-inset-*)` is used? [N11]
- [ ] `touch-action` declared per gesture surface; `user-select:none` only on controls? [N11]
- [ ] Gesture pan axis declared so it does not steal scroll? [N4]
- [ ] Collapsing/entrance motion avoids layout-triggering properties; entrance not replayed on recycled rows? [N13]
- [ ] Verified on real hardware / slowest supported device, not just simulator/emulation? [N11, N13]
- [ ] Custom screen transition's back-swipe reverses the same transition under the finger? [N5]

---

## Suggested decision-tree rows

| Task/question | Go to |
|---|---|
| "Interaction feels dead / laggy on touch" | N1 (laws), N11 (tap latency row), N7 (press timing) |
| "Which spring values for a sheet / drawer / reposition?" | N2 |
| "Sheet/card should fling and land where the flick was heading" | N3 (projection + velocity handoff) |
| "Drag jumps when grabbed mid-animation" | N1 law 3 |
| "Edge of scroll/drag feels like a wall" | N3 (rubber-band) |
| "Pan gesture fights scrolling / carousel scrolls the page" | N4, N11 (touch-action row) |
| "Should this even animate?" | N6 |
| "How long / what easing for UI motion on mobile?" | N7 |
| "Add haptics" | N8 |
| "Glass/translucent chrome hierarchy, scrim or no scrim" | N9 |
| "Reduce motion / transparency / contrast support" | N10 |
| "Web game or page feels like a website on a phone" | N11 |
| "Min touch target / hit slop / ripple vs scale" | N12 |
| "Header collapse / list entrance / keyboard-following footer janks" | N13, N12 (keyboard bullet) |
| "Toast or screen-transition spatial logic" | N5 |
| "Naming the design principle behind a critique" | N14 |
| "Letter-spacing / line-height by size" | N15 |
| "Does Emil conflict with our tokens?" | Divergences table |
| "Swift concurrency / testing / language questions" | Hand-off table (swift-concurrency-pro, swiftui-pro, swift-testing-pro) |

---

## UNVERIFIED

- **SwiftUI API mapping.** The source states Apple's damping/response model and gives web mappings (Motion `bounce` + `duration`) and Reanimated config; it never shows SwiftUI code. That SwiftUI's `.spring(response:dampingFraction:)` takes the same two parameters, that `.interpolatingSpring`/`interactiveSpring` carry velocity, and that `UIScrollView.DecelerationRate.normal` equals 0.998 are my recollection, not read. Verify before baking into tokens.
- **iOS/macOS version availability** of any Liquid Glass, haptic (`sensoryFeedback`), or scroll-edge-effect API: not in source; not claimed.
- **Whether StudioJoeMotion values were derived from Apple's table.** Source does not mention Studio Joe; divergence rows are comparisons only.
- **`apple-design` principle count/date:** source cites "Principles of Great Design, WWDC 2026" (§16); not independently checked.
- **tvOS/macOS applicability:** all touch/gesture/haptic rules are phone-centric in source; tvOS focus engine, macOS pointer, and trackpad haptics are not covered by any file read.
- **Expo-only items dropped** (Reanimated worklets/UI-runtime, scheduleOnRN, NativeTabs, formSheet detents, Android caps, 120 fps Info.plist key). The 120 fps ProMotion note (`CADisableMinimumFrameDurationOnPhone`, 8 ms budget) was read but omitted; whether it applies to SwiftUI/Metal apps is unknown.
- **Native-SwiftUI analog of "animate only transform+opacity"** (N13) is not stated in source for SwiftUI; the rule is RN/web specific as written.
- **write-swift sibling coverage:** swift-testing-pro, swiftdata-pro owners listed from the available-skills list only; their SKILL.md bodies were not read, so the hand-off table's last two rows are unconfirmed ownership. swift-concurrency-pro, swiftui-pro, swiftui-ui-patterns, swiftui-liquid-glass, swiftui-performance-audit: frontmatter and headings only.
- **Divergence "Tab-bar transitions"** has no Studio Joe statement in the two dedupe files; recorded as gap, not conflict.
