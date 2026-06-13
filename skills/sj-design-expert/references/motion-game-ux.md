# Motion & Game UX Patterns — sj-design-expert reference

Distilled from: emoji-arcade (shell + 3 games), emoji-slopes (standalone), star-speller.
Lens: durable design/UX/motion knowledge; GPU internals are cross-referenced to `graphics-api-expert`.

---

## Sources read

| File | What it covers |
|---|---|
| `emoji-arcade/index.html` | Shell CSS: cabinet grid, pause overlay, CRT transition, touch pause button, phone-layout media queries, safe-area |
| `emoji-arcade/shell/shell.js` | Shell lifecycle: launch/pause/quit, mute, visibilitychange, blur autopause, touch pause stopPropagation, headless hook |
| `emoji-arcade/shell/attract.js` | Attract-mode background loop; drifting emoji sprites |
| `emoji-arcade/GAME-API.md` | Cabinet contract: division of responsibilities, engine modules |
| `emoji-arcade/games/survivors/game.js` | Full HUD CSS + JS: damage numbers, toast, banner, XP hot-glow, boss bar, joystick anchor clamp, touch onboarding hint, screen entrance animations, card grid responsiveness, reduced-motion guards, touch target sizes |
| `emoji-arcade/games/slopes/game.js` | Arcade port of slopes: HUD layout for this variant |
| `emoji-arcade/games/squadron/game.js` | Squadron: difficulty select UX, banner, hit-stop, double-tap guard reference |
| `emoji-slopes/index.html` | Standalone slopes: combo meter, trick/hint/banner channel separation, tune panel, glass-blur HUD, safe-area, pointer:coarse pause button |
| `star-speller/src/main.ts` | Level select, HUD dock layout, loop generation token, cheer pop, settings modal, backdrop loop |
| `star-speller/src/curriculum.ts` | Phonics scope-and-sequence, typingMode bifurcation, pickWord with mastery weights |
| `star-speller/src/game.ts` | Pacing knobs per mode, typo forgiveness, combo/score, floor reservation, mastery recording |
| `star-speller/src/keyboard.ts` | On-screen keyboard: finger-zone coloring, highlight, flash feedback |
| `star-speller/src/settings.ts` | Persisted settings: dyslexiaFont, bigText, colorblind, reducedMotion, letterSounds |
| `star-speller/src/mastery.ts` | Adaptive word weighting (miss +2, clean complete −1, slow complete +1, cap 6) |
| `joeOS/Daily Notes/2026-06-12.md` | Mobile/touch UX pass session log; design rationale for shell-owned pause, safe-area, compact cabinet list, joystick edge-clamp, double-tap guards, entrance stagger, atlas shadow baking |

---

## Distilled patterns

### 1. Shell/Cabinet Contract (arcade architecture as UX)

The shell-versus-game responsibility split is a UX architecture decision, not just a code choice.

| Concern | Owner | Rationale |
|---|---|---|
| Title/start screen | **Shell** (forbidden to games) | Consistent launch feel; avoids duplicated skip-animation logic per game |
| Pause overlay (Esc/P/⏸) | **Shell** | One implementation; games can't accidentally double-bind pause keys |
| Touch pause button position | **Shell** (56×56 px, top-right safe corner) | Globally reserved; game HUDs must not place interactive/critical elements there on `pointer:coarse` devices |
| Mute key (M) + mute UI | **Shell** → `setMuted(m)` | Games receive a single boolean; no per-game mute logic |
| Game-over screen | **Game** | Context-specific copy and stats |
| In-game HUD | **Game**, scoped under `.game-<id>` | Injected as `<style>` inside the container; removed with it |
| High-score storage | **Both** (game: own key; shell: `emoji-arcade:hi:<id>`) | Shell renders the cabinet hi display |

Source: `emoji-arcade/GAME-API.md`, `shell/shell.js`

**CSS scoping rule:** All game styles use `.game-<id>` prefix, injected as a `<style>` element inside `container`; the shell removes the container on quit, which atomically removes the styles.

---

### 2. Touch UX Fundamentals

#### 2a. Safe-area HUD placement

All HUD elements that could sit behind a notch, Dynamic Island, or home indicator use `env()`:

```css
/* survivors/game.js CSS */
.game-survivors .lvlTag {
  top: calc(6px + max(14px, env(safe-area-inset-top, 0px)));
  left: max(16px, env(safe-area-inset-left, 0px));
}
.game-survivors .hpWrap {
  bottom: calc(26px + env(safe-area-inset-bottom, 0px));
}
/* shell touch-pause button */
#tpause {
  top:   calc(env(safe-area-inset-top, 0px)   + 8px);
  right: calc(env(safe-area-inset-right, 0px) + 8px);
}
```

The `max(14px, env(...))` pattern: env() returns 0 on desktop (no notch), so the `max` keeps a minimum margin. Source: `survivors/game.js`, `index.html`.

#### 2b. Touch pause button — stopPropagation is load-bearing

```js
// shell/shell.js
tp.addEventListener("touchstart", (e) => {
  e.preventDefault();
  e.stopPropagation();  // <-- REQUIRED: games register touchstart on window
  paused ? hidePause() : showPause();
}, { passive: false });
```

Games bind `window.addEventListener("touchstart", ...)` for joystick anchor and double-tap detection. Without `stopPropagation` the tap reaches the game and may start an unintended move. Source: `shell/shell.js` line 166.

#### 2c. Touch pause button visibility gate

```css
@media (pointer:coarse) {
  body:has(#stage.on) #tpause { display: flex; }
}
```

The `:has(#stage.on)` selector shows the button only while a game is mounted; it disappears on the menu. Source: `index.html`.

#### 2d. 44 px touch targets

Pause/mute/quit buttons in pause overlay: `min-height: 44px`. On-screen keyboard keys: `width: 40px; height: 44px`. Icon button: `padding: 8px 14px`. Source: `index.html` `.pbtn`, `star-speller/src/style.css` `.osk-key`.

#### 2e. Joystick anchor edge-clamp

The virtual joystick anchor must be inset by at least `STICK_R + margin` from each bezel edge. A thumb planted flush with the edge would put half the stick radius off-glass, creating a one-sided dead zone.

```js
// survivors/game.js
const STICK_R = 52;
const m = STICK_R + 18;
const ax = clamp(t.clientX, m, (container.clientWidth || innerWidth) - m);
const ay = clamp(t.clientY, m, (container.clientHeight || innerHeight) - m);
```

Source: `survivors/game.js` line 570-572 (2026-06-12 session log confirms "anchor at bezel = half the stick off-glass").

#### 2f. Double-tap proximity guard

Documented in the session log as the "squadron double-tap-roll 48px proximity guard": lift-and-re-grab was triggering the roll when the second touch landed close to the first. Guard implemented by rejecting a new tap if it lands within 48px of the previous release point within a short window.

Source: `joeOS/Daily Notes/2026-06-12.md` (session note only; not verified in squadron source in this run — see UNVERIFIED).

#### 2g. Touch onboarding hint (one-time localStorage gate)

```js
// survivors/game.js
if (isTouch) {
  try {
    if (!localStorage.getItem("emojisurv_touchhint")) {
      localStorage.setItem("emojisurv_touchhint", "1");
      game._setToast("👆 DRAG ANYWHERE TO MOVE", 3.2);
    }
  } catch (e) {}
}
```

Pattern: first-run only, surfaced on the toast channel, never shown again. localStorage access wrapped in try/catch (private mode safety). Source: `survivors/game.js` lines 629-635.

#### 2h. Touch-specific copy in overlays

```html
<!-- emoji-slopes/index.html -->
<div class="keys" id="keys-touch" style="display:none">
  <kbd>drag</kbd> steer &nbsp; <kbd>second finger</kbd> tuck
</div>
```

Desktop key hints and touch hints are separate DOM nodes; JS toggles which is shown based on pointer type. Do not merge them into a single hybrid string. Source: `emoji-slopes/index.html` lines 140-143.

---

### 3. Visibility & Focus Autopause

Both `blur` and `visibilitychange` must be bound — `blur` is flaky on iOS Safari during Home-swipe/tab-switch:

```js
// shell/shell.js
addEventListener("blur", () => { if (current && !paused) showPause(); });
document.addEventListener("visibilitychange", () => {
  if (document.hidden && current && !paused) showPause();
});
```

Games also bind these on `window` as a fallback (`autoPause` in survivors), but the shell is the canonical owner. Source: `shell/shell.js` lines 173-178, `survivors/game.js` line 556-557.

---

### 4. Responsive Cabinet/Menu Layout

**Desktop:** Centered flex row of fixed-width cabinet cards (`width: min(280px, 82vw)`), hover lifts `translateY(-7px) scale(1.025)`, glow via `color-mix`.

**Phone (`max-height:760px` OR `max-width:480px`):**

```css
/* index.html */
#arcade { justify-content: flex-start; overflow-y: auto;
  -webkit-overflow-scrolling: touch; overscroll-behavior: contain; gap: 18px;
  padding: calc(env(safe-area-inset-top,0px) + 22px) 16px
           calc(env(safe-area-inset-bottom,0px) + 46px); }
.cab { width: min(360px,92vw); display: grid; align-items: center; text-align: left;
  grid-template: "icon title coin" auto "icon tag coin" auto "icon hi coin" auto / 60px 1fr auto;
  column-gap: 14px; padding: 12px 14px; }
```

The phone layout converts card "icons + title/tag/hi + coin button" from vertical stack to a three-column CSS grid (icon | text | CTA). This fits 3+ games vertically without scroll needing discovery. Source: `index.html` lines 62-78.

**Cabinets as `<button>` elements:** Keyboard focusable, a11y-native, no JS needed for Enter-key launch. Source: `shell/shell.js` line 51 (`const el = document.createElement("button")`).

---

### 5. HUD Design Conventions

#### 5a. Channel separation (slopes pattern)

The slopes standalone uses four distinct text channels that never stomp each other:

| Channel | Element | Position | Purpose |
|---|---|---|---|
| Banner | `#banner` | top 20% | Named section announcements (2.5s auto-fade) |
| Trick score | `#trick` | top 33% | Airtime trick text (1s) |
| Combo meter | `#combo` | top 9% | Live multiplier with pips |
| Hint | `#hint` | center 46% | Tutorial copy (quieter, pill style) |

The trick score sits below the banner: both can be visible simultaneously without overlap. Source: `emoji-slopes/index.html` lines 37-68.

#### 5b. Survivors toast + banner (arcade variant)

```css
/* survivors/game.js CSS */
.game-survivors .toast { top: 54%; /* secondary channel, under the banner */ }
.game-survivors .banner { top: 34%; /* primary channel */ }
```

Fade math: `opacity = Math.min(clamp((dur - t) / fadeOut, 0, 1), clamp(t / fadeIn, 0, 1))` — smooth in AND out in a single expression. Source: `survivors/game.js` lines 704-733.

#### 5c. XP bar pre-level glow signal

```css
.game-survivors .xpBar.hot .xpFill {
  background: linear-gradient(90deg, #ffd24a, #fff0a8);
  box-shadow: 0 0 18px rgba(255,210,70,.95);
}
```

Applied when `game.xp / game.xpReq > 0.9`. The class swap replaces the fill color, creating a "charging" visual. Source: `survivors/game.js` line 710.

#### 5d. Low-HP pulse (background shader)

Instead of a DOM overlay, the red "danger" pulse is embedded in the background pass uniform:

```glsl
// In WGSL bg shader — zero extra draw call
col = mix(col, vec3f(0.55,0.07,0.06),
  clamp(u.tint.w, 0., 1.) * 0.4);
```

The CPU side: `redAmt = Math.max(game.redFlash, lowHp ? 0.4 + 0.18 * Math.sin(game.time * 8) : 0)`. Source: `survivors/game.js` lines 762-763. See graphics-api-expert for the uniform layout.

#### 5e. HUD stat hierarchy (slopes)

```css
#hud .stat b     { font-size: 22px; }            /* most stats */
#hud .stat.star b { font-size: 30px; }           /* headline: meters */
#hud .stat.dim b  { font-size: 15px; opacity:.7; } /* ambient: speed, best */
```

One headline stat at +8px and reduced opacity for ambient. Source: `emoji-slopes/index.html` lines 23-26.

---

### 6. Damage Numbers via DOM Pool + WAAPI

```js
// survivors/game.js — 28 pre-allocated <span> elements
const DMG_POOL = 28;
for (let i = 0; i < DMG_POOL; i++) {
  const s = document.createElement("span");
  s.className = "dmg";
  elDmgLayer.appendChild(s);
  dmgEls.push(s);
}
let dmgIdx = 0;

function spawnDmg(wx, wy, amt) {
  const s = dmgEls[dmgIdx]; dmgIdx = (dmgIdx + 1) % DMG_POOL;
  // viewport-cull: skip if off-screen
  if (sx < -20 || sx > container.clientWidth + 20 || ...) return;
  s.textContent = Math.round(amt);
  s.style.left = sx + "px"; s.style.top = sy + "px";
  s.animate(
    [{ transform: "translate(-50%,-50%) scale(1.1)", opacity: 1 },
     { transform: "translate(-50%, -180%) scale(0.85)", opacity: 0 }],
    { duration: 480, easing: "cubic-bezier(.2,.7,.4,1)" });
}
```

Pattern: ring buffer of pre-allocated DOM nodes; WAAPI `.animate()` so no per-hit allocation; off-screen cull before setting content. Source: `survivors/game.js` lines 479-500.

---

### 7. Game-Feel / Juice Presentation

#### 7a. Hi-score odometer

```css
/* Each digit is a <b> in its own box — the "arcade counter" look */
.cab .hi b {
  display: inline-block; width: 1.3ch; text-align: center;
  background: rgba(0,0,0,.45); border: 1px solid rgba(255,210,74,.22);
  border-radius: 3px; font-family: ui-monospace, Menlo, monospace;
  font-variant-numeric: tabular-nums; color: #ffd24a;
  text-shadow: 0 0 8px rgba(255,210,74,.45);
}
```

Six-digit, leading-zero padded: `String(Math.floor(n)).padStart(6, "0").split("").map(d => \`<b>${d}</b>\`).join("")`. Source: `index.html` lines 45-49, `shell.js` line 32.

#### 7b. CRT power-on transition

```css
#tv.on { animation: crt-on .36s ease-out forwards; }
@keyframes crt-on {
  0%   { opacity: .85; transform: scaleY(.004); }         /* thin bright scan line */
  45%  { opacity: .85; transform: scaleY(.004) scaleX(1.04); }
  70%  { opacity: .38; transform: scaleY(1); }
  100% { opacity: 0;   transform: scaleY(1); }
}
@media (prefers-reduced-motion: reduce) {
  #tv.on { animation: crt-fade .22s ease-out forwards; }
  @keyframes crt-fade { 0%{opacity:.35;} 100%{opacity:0;} }
}
```

Used on every launch AND on quit-to-arcade (`crt()` called both times). The `void tv.offsetWidth` reflow trick re-triggers the animation when the class is removed and re-added. Source: `index.html` lines 93-104, `shell.js` line 73.

#### 7c. "INSERT COIN" pulse on cabinets

```css
.cab .coin { animation: coin 1.8s ease-in-out infinite; }
@keyframes coin { 0%,100%{ transform:scale(1); } 50%{ transform:scale(1.05); } }
@media (prefers-reduced-motion: reduce) { .cab .coin { animation: none; } }
```

Source: `index.html` lines 52-54.

#### 7d. Level-up card entrance stagger

```css
.game-survivors .screen.on > * {
  animation: gsv-rise .32s cubic-bezier(.2,.9,.3,1.2) backwards;
}
.game-survivors .screen.on > *:nth-child(2) { animation-delay: .05s; }
.game-survivors .screen.on > *:nth-child(3) { animation-delay: .1s; }
@keyframes gsv-rise { from { opacity:0; transform:translateY(14px) scale(.96); } }
```

Cards also stagger independently: `nth-child(2)` at 0.06s, `nth-child(3)` at 0.12s. `backwards` fill mode so they start invisible before their delay fires. Source: `survivors/game.js` CSS lines 323-328.

#### 7e. Combo shatter animation (slopes)

```css
#combo.shatter {
  animation: comboShatter .5s ease-in forwards;
}
@keyframes comboShatter {
  0%   { transform: translateX(-50%) scale(1); color: #a22; }
  25%  { transform: translateX(-50%) scale(1.35) rotate(-4deg); }
  100% { transform: translateX(-50%) scale(.6) rotate(14deg) translateY(48px); opacity:0; }
}
```

Source: `emoji-slopes/index.html` lines 47-50.

#### 7f. Star Speller cheer pop

```css
.cheer-pop.show { animation: cheer 0.9s cubic-bezier(0.16,1,0.3,1); }
@keyframes cheer {
  0%  { opacity:0; transform:translate(-50%,-50%) scale(0.5); }
  25% { opacity:1; transform:translate(-50%,-50%) scale(1.1); }
  70% { opacity:1; transform:translate(-50%,-55%) scale(1); }
  100%{ opacity:0; transform:translate(-50%,-70%) scale(0.95); }
}
```

Element is created per-cheer and `setTimeout(() => pop.remove(), 950)` cleans it up. Source: `star-speller/src/style.css` lines 256-263, `main.ts` line 441.

---

### 8. Screen Overlay Architecture

**Visibility via `opacity + pointer-events + visibility`** — not just `display:none`:

```css
/* emoji-slopes/index.html */
.overlay.hidden { opacity:0; pointer-events:none; visibility:hidden; }
```

Comment in slopes source explains why `visibility` is needed: a child button with `pointer-events:auto` punches through a parent's `pointer-events:none`, so a hidden overlay's button can silently eat clicks meant for layers below. Source: `emoji-slopes/index.html` line 77.

**`justify-content: safe center`** (star-speller level select):

```css
.screen { justify-content: safe center; overflow-y: auto; }
```

Centers content when it fits, top-aligns when taller than viewport so the top isn't clipped above the scroll origin. Source: `star-speller/src/style.css` lines 44-45 (comment explains the behavior).

---

### 9. Reduced-Motion Support

Every ambient/decorative animation has a `prefers-reduced-motion` counterpart:

| Element | Default | Reduced |
|---|---|---|
| CRT transition | `crt-on` 0.36s (scaleY scan line) | `crt-fade` 0.22s (plain fade) |
| "INSERT COIN" pulse | `coin` infinite scale | `animation:none` |
| Yeti warning / combo pulse | `pulse` infinite alternate | `animation:none` |
| Screen entrance stagger | `gsv-rise` 0.32s | `animation:none` |
| Gobutton pulse | `gsv-pulse` 1.6s | `animation:none` |
| Spark count (star-speller) | 38 sparks on complete | 30% of that: `if (reducedMotion()) n = Math.ceil(n * 0.3)` |

The screen-shake path in survivors is guarded by: `const noShake = matchMedia("(prefers-reduced-motion:reduce)").matches`. Source: various files, confirmed per source above.

---

### 10. Kid UX Patterns (Star Speller)

#### 10a. Mode bifurcation by reading stage

| Mode | Grades | Keyboard | Pacing | Metric |
|---|---|---|---|---|
| `"find"` | K–2 (emerging) | On-screen shown; next key highlighted | Slow: 16px/s fall, 4.5s spawn, 1 word on screen, 4 lives | Accuracy % only |
| `"touch"` | 3–5 (fluent) | Hidden by default | Faster: 30px/s fall, 2.8s spawn, 3 words on screen, 3 lives | WPM + accuracy |

Source: `curriculum.ts`, `game.ts` `PACING` constant.

#### 10b. Typo forgiveness — no reset

```js
// game.ts handleKey
} else {
  // Very gentle on typos: keep all progress so far — the kid just tries the
  // next letter again. No reset, no penalty.
  this.keyStreak = 0;
  f.typo = true;
  recordMiss(f.word);
  audio.miss();
}
```

Wrong key flashes red on the keyboard for visual feedback; the word stays in place. Source: `game.ts` lines 187-196.

#### 10c. Adaptive mastery weighting

Words a kid struggles with spawn more often. Algorithm: miss → +2 to need score (cap 6); clean complete → −1; slow complete → +1. Spawn weight = 1 + needScore. Persisted via localStorage. Source: `mastery.ts`.

#### 10d. Auto-sound-out for K–1

```js
// game.ts constructor
this.autoSoundOut = level.grade === "K" || level.grade === "1";
```

Kindergarten and Grade 1 levels automatically speak the phoneme segments on drop appearance (not just on button press). Older grades hear the whole word only. Source: `game.ts` line 115.

#### 10e. Finger-zone keyboard coloring

Left hand = warm colors (pink → orange → yellow → green); right hand = cool colors (cyan → blue → violet → purple). Color is set as a CSS custom property `--finger` on each key button, consumed by `color-mix(in srgb, var(--finger) 70%, white)` for the key background. Source: `keyboard.ts`.

#### 10f. Bottom-dock layout (never fight the game area)

All in-game UI lives in a bottom dock. The game's catch-line is reserved as `dock.offsetHeight + 16`. Nothing floats over the play area except cheer pops. Source: `main.ts` lines 374-428, `style.css` `#dock`.

#### 10g. Settings surface accessibility options directly

Settings modal exposes: dyslexia font (easy-read), bigger text, colorblind colors, reduced motion, letter sounds vs names, caps/lowercase. Applied via `document.body.classList.toggle("easy-read", ...)` at save time. Source: `settings.ts`, `main.ts` `showSettings()`.

---

### 11. Global HTML/viewport Boilerplate for Games

```html
<meta name="viewport"
  content="width=device-width,initial-scale=1,maximum-scale=1,
           user-scalable=no,viewport-fit=cover">
```

```css
html, body {
  overflow: hidden;
  -webkit-user-select: none; user-select: none;
  overscroll-behavior: none;
  -webkit-tap-highlight-color: transparent;
  touch-action: none; /* on the canvas/game element */
}
```

`viewport-fit=cover` is required for `env(safe-area-inset-*)` to work. `overscroll-behavior:none` prevents pull-to-refresh on Android. Source: both `emoji-slopes/index.html` and `emoji-arcade/index.html`.

---

### 12. Loop Architecture

**Loop generation token** (star-speller): prevents stale rAF callbacks from a superseded loop re-queuing:

```ts
let loopGen = 0;
function stopLoop() { loopGen++; cancelAnimationFrame(rafId); }
const loop = (now: number) => {
  if (gen !== loopGen) return; // superseded — exit cleanly
  // ...
  rafId = requestAnimationFrame(loop);
};
```

Without this, ending a level mid-frame leaves the old game loop running alongside the new backdrop loop (two renders per frame, forever). Source: `main.ts` lines 32-36, 317-333.

**dt clamping:** Both `engine/loop.js` (arcade) and `star-speller/main.ts` clamp dt to 50ms to prevent physics explosions after tab-background throttling. Source: GAME-API.md engine description; `main.ts` line 322 `Math.min(0.05, ...)`.

---

## Reviewer checklist candidates

- [ ] Are HUD elements behind potential notch/Dynamic Island using `env(safe-area-inset-*)`?
- [ ] Does the floating touch pause button use `stopPropagation` so game joystick never sees it?
- [ ] Is the touch pause button shown only via `pointer:coarse` + `:has(#stage.on)` (not always visible)?
- [ ] Are all interactive touch targets ≥ 44px height?
- [ ] Is the joystick anchor clamped inward by at least `STICK_R + margin` on all edges?
- [ ] Are `blur` AND `visibilitychange` both bound for autopause (not just one)?
- [ ] Does the overlay `.hidden` class include `visibility:hidden`, not just `opacity:0 pointer-events:none`?
- [ ] Are all decorative animations guarded with `@media (prefers-reduced-motion: reduce)`?
- [ ] Are particle counts scaled down under `reducedMotion()`?
- [ ] Is `overscroll-behavior:none` set to prevent pull-to-refresh?
- [ ] Is `-webkit-tap-highlight-color:transparent` set for tap flash suppression?
- [ ] Is `viewport-fit=cover` in the viewport meta for safe-area to work?
- [ ] Are ambient/status stats visually demoted (smaller size, reduced opacity) vs headline stats?
- [ ] Does the phone layout have its own scrollable container with `overscroll-behavior:contain`?
- [ ] Is toast/cheer copy distinct from banner/announcement copy (separate DOM channels)?
- [ ] Is the loop guarded against stale rAF callbacks after phase transitions?
- [ ] Are game event listeners removed in `destroy()` (nothing bound to `window`/`document` should outlive the game)?

---

## Suggested decision-tree rows

| Question / task | Go to § |
|---|---|
| "Add a new in-game stat to the HUD" | § 5 (hierarchy, channel separation) |
| "Add floating touch control (joystick, button)" | § 2 (safe-area, 44px, edge clamp, stopPropagation) |
| "Game goes to background / app switch" | § 3 (blur + visibilitychange both required) |
| "Show a popup/screen overlay" | § 8 (visibility + pointer-events + safe center) |
| "Add an ambient animation (pulse, glow, CTA)" | § 7, § 9 (reduced-motion guard required) |
| "Add damage numbers / floating score pops" | § 6 (DOM pool + WAAPI pattern) |
| "Design for phone with notch/Dynamic Island" | § 2a, § 11 (env() + viewport-fit=cover) |
| "Split a game into arcade cabinet" | § 1 (cabinet contract) |
| "Design responsive cabinet/menu layout" | § 4 (grid list card on phone) |
| "Kid/educational app UX" | § 10 (forgiveness, mastery, mode bifurcation, dock layout) |
| "Add a level/phase transition" | § 7d (entrance stagger), § 7b (CRT), § 5b (banner/toast channels) |
| "Handle WebGPU device loss gracefully" | cross-ref graphics-api-expert |
| "Screen-shake effect" | § 9 (reduced-motion check before applying) |
| "Add settings with accessibility options" | § 10g (dyslexia font, big text, colorblind, reduced-motion) |

---

## UNVERIFIED

The following were mentioned in session logs or inferred from partial reads but NOT verified by reading the specific implementation:

1. **Squadron double-tap proximity guard (48px radius):** The 2026-06-12 session log states "squadron double-tap-roll 48px proximity guard (lift-and-re-grab was triggering rolls) + bomb button raised out of the drag zone." The exact implementation was not found in the squadron `game.js` partial read. Treat distance and mechanism as approximate until the full `squadron/game.js` is read.

2. **`{shadow:true}` atlas baking in engine/atlas.js:** Session log mentions "atlas `{shadow:true}` baked glyph drop-shadows (engine)" as part of the polish pass. `buildAtlas` calls in game files pass `{ shadow: true }` but `engine/atlas.js` was not read in this run to verify the shadow implementation.

3. **Squadron bomb button position (raised out of drag zone):** Stated in session log; not confirmed in squadron game.js source.

4. **`emojisurv_touchhint` key surviving across cabinet visits:** Verified the write path; not verified that it survives a destroy/re-mount cycle correctly (localStorage is tab-global so it should, but no explicit test observed).
