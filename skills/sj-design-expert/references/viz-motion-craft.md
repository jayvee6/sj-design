# Visualization & Motion Craft — Reference

> T3 research slice. Read-only pass over five repos.
> GPU pipeline internals deferred to `graphics-api-expert`; one-line cross-refs only where needed.

---

## Sources read

| Repo | Files read |
|---|---|
| `musicplayer-viz` | `viz-registry.js`, `viz/lib/perf-budget.js`, `viz/lib/beat-switcher.js`, `viz/lib/dual-mode-blend.js`, `viz/lib/temporal-taa.js`, `viz/lib/shader-utils.wgsl.js`, `docs/animation-speed-audit.md`, `CLAUDE.md`, `audit/PIXAR-UPLIFT-HITLIST.md`, `audit/MANDALA-REDESIGN.md`, `styles.css` (seekbar/player section), `app.js` (idle synth, hue accumulator, album art, seekbar handlers), `viz/bars.js`, `viz/constellation-wgpu.js`, `viz/aurora-veils-wgpu.js`, `viz/cosmic-wave-wgpu.js`, `viz/kaleidoscope-wgpu.js`, `viz/mandala-relief-wgpu.js`, `viz/lunar-wgpu.js` |
| `three-particle-lab` | `src/main.js`, `src/Particles.js` |
| `tree-shatter-sandbox` | `src/main.js` |
| `ripple-zen-garden` | `CLAUDE.md`, `LEDGER.md`, `ORCHESTRATOR.md` |
| `ripple` | `index.html` (full — CSS, WGSL, JS) |

---

## Distilled patterns

### 1. Post-processing stack (universal across webgpu viz)

Every WebGPU viz in `musicplayer-viz` follows the same composite pass order (source: `viz/lib/shader-utils.wgsl.js`, `viz/lib/temporal-taa.js`):

```
scene (rgba16float HDR) → TAA resolve (optional) → ACES tonemap → IGN dither → swapchain
```

| Step | Purpose | Source |
|---|---|---|
| ACES (Hill 2015) | Compress HDR → [0,1] with film shoulder; prevents audio-reactive brightness spikes from clipping to flat white | `viz/lib/shader-utils.wgsl.js:71` |
| `sjDither` (IGN) | Interleaved-gradient-noise dither breaks 8-bit banding on linear→sRGB conversion | `viz/lib/shader-utils.wgsl.js:75` |
| TAA resolve | Reprojection-free; 3×3 neighbourhood clamp + luma flash-reject; keeps volumetric viz coherent | `viz/lib/temporal-taa.js:57` |
| Film grain | Applied in the TAA present pass — ACES + fine grain together | `viz/lib/temporal-taa.js:21` |

**Rule:** never put ACES in the scene shader; only in the present/composite pass. Applying it to already-display-referred color double-corrects and desaturates (confirmed failure on `ripple-zen-garden` iter 1; LEDGER.md:53).

**Vignette:** used selectively, not universally. Appears in `cosmic-wave-wgpu.js:118` ("gentle global pulse + vignette"), `kaleidoscope-wgpu.js:161`, `mandala-relief-wgpu.js:360`, `newton-basins-wgpu.js:165`, `liquid-chrome-wgpu.js:243`. Pattern: `smoothstep(innerR, outerR, dist_from_center)` multiplied against color. Keeps the viewer's eye on the focal subject.

### 2. Audio-reactive choreography as design language

**Audio frame fields consumed by viz** (sourced via `viz-registry.js` render path):

| Field | Meaning | Typical use |
|---|---|---|
| `bass` / `bassAtt` | Low-frequency energy / attack | Scale, expand, throb; drive slow rotation |
| `mid` / `midAtt` | Mid energy | Color shifts, petal open/close |
| `treble` / `trebAtt` | High-frequency energy | Shimmer, fine-detail ripple |
| `beatPulse` | Onset energy (0→1 pulse) | Flashes, impulses, mode switches |
| `isBeatNow` | Boolean rising edge | One-shot triggers |
| `energy` | Broadband scalar | Global brightness/speed multiplier |
| `valence` | Track mood 0–1 | Master hue offset (maps → OKLCh hue angle) |
| `magnitudesSmooth` | 32-bin smoothed FFT | Per-bar height, per-band SDF pulse |

**Attack/release design rule:** always use the smoothed `*Att` / `*Rel` / `magnitudesSmooth` variants in the shader, NOT raw FFT bins. Raw FFT produces a "mechanical twitch" look (cited in `audit/MANDALA-REDESIGN.md:47`). The `*Rel` (release) forms sustain energy so the viz breathes rather than stutters.

**Beat response design:** limit audio-reactive gain to a clamped range. The unclamped pattern `baseline + bass * N + beat * M` with N,M ≥ 2 has caused both photosensitivity risks and ACES pipeline surprises. Recommended pattern from `docs/animation-speed-audit.md:154`:
```js
Math.min(maxGain, baseline + bassSmooth * perBassCoef + beatEnv * perBeatCoef)
// maxGain ≈ 6.0 for most viz; 3.0 for full-screen flash effects
```

**Audio-reactive hue accumulator:** `viz-registry.js` advances a `musicHueAccumulator` (radians) at `0.04 + treble * 0.5 + beatPulse * 0.8` rad/s. This keeps colors shifting even on a static track. Valence maps → master hue via `2.9 + (valence - 0.5) * 1.7` rad. Every viz sharing this system gets automatic track-color response for free.

**Idle state (no music playing):** when `bass < 0.08 && mid < 0.08`, the registry injects a synthetic "breathing" signal (`viz-registry.js:590–622`):
```js
idleBass   = 0.22 + 0.18 * Math.sin(t * 0.22 * 1.9)   // ~0.066 Hz
idleMid    = 0.18 + 0.14 * Math.sin(t * 0.22 * 2.8)
idleTreble = 0.12 + 0.10 * Math.sin(t * 0.22 * 4.3)
```
Result: every viz has an organic ambient idle state without per-viz coding. The slow oscillation frequencies (0.066–0.15 Hz) are below any perceptible flicker threshold.

### 3. Color palette strategy

**Track-driven vs debug modes** (`viz-registry.js:654–681`):

| colorMode | Behavior |
|---|---|
| `'track'` (default) | Valence from Spotify/MusicKit metadata drives hue; beat-reactive accumulator shifts it over time |
| `'cycle'` | 50s hue rotation regardless of track |
| `'static'` | Fixed hue from `VizDebug.staticHue` (0–360°) |

**OKLCh vs hand-picked RGB palettes:** a hard-won lesson from the Pixar uplift campaign (`audit/PIXAR-UPLIFT-HITLIST.md:119`): "OKLCH hue wheels at fixed C collapse into ~2 perceptual families — use hand-picked RGB tables." Automated hue-wheel palettes produce viz that look monochromatic in practice because the Oklab C distance doesn't capture perceptual saturation uniformly.

**Dark palette + dark backgrounds:** the entire repo runs on a near-black canvas (page `background: #050912` in ripple; `scene.background = 0x0d1117` in `tree-shatter-sandbox`; `renderer.setClearColor(0x0b0e13)` in `three-particle-lab`). Light subjects on a dark field is the studio standard.

**Album art integration:** album art is displayed in a separate `#album-art` / `#ipodArt` element in `app.js` (not composited into the viz canvas). The viz color system responds to track valence (mood) but not to the literal album artwork colors. This is an open design opportunity noted in `audit/MANDALA-REDESIGN.md`.

### 4. Performance as a design constraint

**Resolution scale is the dominant lever.** `viz/lib/perf-budget.js` describes this explicitly: "resolution is the biggest lever (≈4× faster per halving)." All WebGPU viz are fragment-bound full-screen shaders; the 2D canvas stays at DPR cap.

| Parameter | Value | Source |
|---|---|---|
| Ratchet threshold | >28 ms (≈36 fps) sustained 2.5s | `perf-budget.js:32` |
| Minimum scale | 0.5 (half-res) | `perf-budget.js:19` |
| Step size | 0.1 per ratchet | `perf-budget.js:20` |
| Cooldown between steps | 6s | `perf-budget.js:34` |
| Recovery | Never automatic (no oscillation) | `perf-budget.js:26` |

**Ratchet-down only:** the earlier two-way adaptive governor caused visible black flashes when the WebGPU context was reconfigured. The current design only steps down on sustained distress; no upward recovery during a session.

**DPR cap patterns:**
- `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))` — both `three-particle-lab` and `tree-shatter-sandbox`
- ripple render: `0.8 × DPR` (capped at 2), sim: `0.6 × DPR` — render and sim resolutions intentionally decoupled for the water shader

**Ripple sim: fixed-timestep loop** (`ripple/index.html:1444–1493`): 60 Hz sim tick regardless of display refresh; max 4 steps per frame; quiesces to a paused loop when the pool settles (30s inactivity). This is the correct pattern for physics-sim viz: decouple from rAF to avoid 2× speed on 120 Hz ProMotion.

**Frame-rate independence:** 17 viz files in `musicplayer-viz` have hardcoded per-frame `+=` state (refresh-rate-coupled); each needs a `const dt = Math.min(0.05, t - lastT)` fix (`docs/animation-speed-audit.md` Addendum A1).

### 5. Live tuning controls workflow

Documented preference (user memory): **build live sliders/toggles to tune params, bake defaults after.** Observed across all five repos:

- `three-particle-lab`: `lil-gui` panel with `curl size`, `speed`, `die speed`, `point size`, `shadow blur`, `shadow color`, `pointer radius`, `pointer force ±`, `auto-rotate` (`src/main.js:109–120`)
- `tree-shatter-sandbox`: `lil-gui` with two folders (`ez-tree`, `three-pinata`) (`src/main.js:259`)
- `musicplayer-viz` registry: per-viz `controls: []` array in the registration definition supports `slider`, `number`, `text`, `button`, `toggle` types; controls appear in a DOM row below the viz buttons (`viz-registry.js:157–200`)
- `musicplayer-viz` debug: global `VizDebug` object exposes `speed`, `reactivity`, `colorMode`, `staticHue`, `energyMode` — all live-writable from the console

**Pattern for new viz:** declare all tunable params as `controls` in the registry definition; prototype with sliders, then bake the winning values as the `default` field once the aesthetic is locked.

### 6. Naming and cataloging 150+ visual modes

**Registry contract** (`viz-registry.js:1–15`):
```js
window.Viz.register({
  id:        'unique-stable-id',   // kebab-case; never changes post-ship
  label:     'Button Text',        // shown in UI
  kind:      '2d' | 'webgpu',
  initFn?,   renderFn,  teardownFn?,
  controls?: [],  layout?: 'vertical'
})
```

**Naming convention observed across 153 files:**
- Descriptive physics/nature names: `aurora-veils`, `ferrofluid`, `physarum`, `ripple-pool`
- Artist/art-movement references: `kleinian-veil`, `newton-basins`, `chladni`, `mandelbrot-abyss`
- `-wgpu` suffix on all WebGPU shaders (vs legacy `.js` 2D); suffix is machine-readable for blend/switch logic
- Prototype/POC suffix convention not shown in filenames — tracked via audit notes

**Beat-driven auto-switcher** (`viz/lib/beat-switcher.js`): switches mode on bar boundaries (default: every 4 bars = 16 beats) with a hard `minIntervalSec: 6` anti-strobe floor. Modes: `'bars'` (bar-aligned), `'beats'` (N detected beats), `'time'` (interval, fires on the next beat for musical alignment). `pick: 'random'` with `avoidRepeat: true` by default.

**Dual-mode blend** (`viz/lib/dual-mode-blend.js`): runs two WebGPU viz simultaneously by monkey-patching `getCurrentTexture()` to redirect each to an offscreen target, then compositing with `mix(A, B, t)`. Auto-sweep (`sin(t * 0.4)`) or manual mix control.

### 7. Calm/wellness motion design (ripple)

**Breathing pacing:** defined as phase objects with `duration` in seconds; each phase has a `type` key that governs animation:

| Phase type | Duration (4-7-8) | Stone animation | Halo | Bowl |
|---|---|---|---|---|
| `inhale` | 4s | 1.0 → 1.04 (`power2.inOut`) | opacity 0 → 0.85 | A3 (220 Hz, 6s decay) |
| `hold-full` | 7s | organic jitter at 1.04 (4 keyframes, `sine.inOut`) | steady 0.85 | D4 (294 Hz, 5s) |
| `exhale` | 8s | 1.04 → 1.0 (`power2.inOut`) | 0.85 → 0 | G3 (196 Hz, 7s, grounding) |
| `hold-empty` | (box only) | snap to 1.0 | → 0 | exhale bowl, 0.6× strength |

**Easing choices for wellness:** `power2.inOut` for primary breath expand/contract (feels lung-like); `sine.inOut` for micro-jitter during hold (organic, never mechanical); `elastic.out(1, 0.45)` for the stone bounce-back after a strike.

**Bowl audio design** (`ripple/index.html:820–854`): 4-partial Tibetan bowl synthesis. Partial ratios `[1.0, 2.76, 5.40, 8.93]` — these are the inharmonic ratios of a real Tibetan bowl. Higher overtones decay faster (`decayScale: [1.0, 0.55, 0.28, 0.16]`) so "shimmer fades, hum sustains." Three bowls tuned to distinct pitches: inhale (A3, lighter), hold (D4, brighter), exhale (G3, lowest, longest decay = grounding).

**Water physics:** damped leapfrog + frequency-dependent viscosity (`capillary detail dies fast, long swell persists`) + quadratic sponge edge. r32float kept over r16 because "r16 quantises the slow decay tail into a permanent shimmer — the calm settle IS the product" (`ripple/index.html:908`). Resolution: sim at 0.6×DPR, render at 0.8×DPR; sim fixed-step 60 Hz.

**Film grain as texture:** `ripple` uses an SVG `feTurbulence` as a CSS background image at `opacity: 0.04`, `mix-blend-mode: overlay` — a cheap CSS-only film grain overlay applied at z-index 6. Source: `ripple/index.html:41–44`.

**Glass selector surface:** the breathing-mode picker is a frosted glass plane (`backdrop-filter: blur(32px) saturate(1.5)`). Three sub-layers: (1) radial-gradient overlay for overhead-light glow, (2) hairline 1px top edge highlight (the "meniscus"), (3) card buttons raised above the plane.

### 8. Zen garden material iteration workflow

From `ripple-zen-garden/LEDGER.md` + `ORCHESTRATOR.md`:

**Scope control as a design discipline:** render shader (WGSL) and tuning parameters are the only allowed edit surface. The compute shader, rake geometry, garden logic, and animation constants are frozen. This prevents accidental regression of core geometry while iterating on material look.

**Grading rubric (photoreal sand/stone, verified):**

| Criterion | Weight |
|---|---|
| Sand multi-scale micro-relief | 20 |
| Sand believable albedo + subtle color variance | 15 |
| Sand groove self-shadow/AO depth | 15 |
| Grazing sheen restraint (not plastic) | 10 |
| Stone surface bump/roughness | 12 |
| Stone contact shadow/AO | 8 |
| Stone mineral color variance | 5 |
| Tonemap/gamma (no clip, no banding) | 10 |
| Resemblance to real reference | 5 |

**Key finding:** naïve ACES on an already-LDR color is wrong; the color is display-referred, so ACES desaturates and lifts. Only apply ACES to scene-linear HDR. (iter 1 failure, `LEDGER.md:57`.)

**Material wins:** multi-octave FBM micro-normal on sand (iter 2), Blinn-Phong matte spec on stone (iter 3), contact shadow ellipse (iter 4), low-freq tone shift per stone (mineral variance, iter 5). Cumulative — each builds on the previous.

### 9. Seekbar / player UI patterns

From `musicplayer-viz/styles.css` and `app.js`:

- Two parallel seekbar implementations: a legacy `#progress-wrap` (top-of-page) and a `#dock-scrubber` (in the floating dock). Both drive the same seek logic.
- Scrub head (thumb) is `opacity: 0` at rest, fades in on `mouseenter`, tracks mouse on `mousemove`; this keeps the bar uncluttered during playback.
- `aria-valuenow` on the dock scrubber for accessibility.
- Player dock fades to an `idle` class after 3s of no interaction (`sleepChrome`); the dock and viz-name badge both receive the `idle` class for CSS-driven fade-out.
- One-time discoverability hint fires on first idle — "the dock fades fully out after 3s idle" — shown once and stored in `localStorage`.

---

## Reviewer checklist candidates

- [ ] Post-processing order is: scene → (optional TAA) → ACES → dither → swapchain. ACES applied in the scene shader is a bug.
- [ ] All audio-reactive brightness gains are clamped (`Math.min(maxGain, ...)` or `clamp()` in WGSL). Unclamped `bass * N + beat * M` with N,M ≥ 2 is a photosensitivity and tonemap risk.
- [ ] Beat-triggered full-screen flashes rate-limited to ≤ 4 Hz (250ms minimum between triggers). See `docs/animation-speed-audit.md` High severity item.
- [ ] Viz using per-frame `state += value` (not `+= value * dt`) are refresh-rate-coupled; must use `Math.min(0.05, t - lastT)` dt.
- [ ] No `requestAnimationFrame` calls inside viz files (all driven by host loop in `app.js`). Zero exceptions in the 153-file catalog.
- [ ] OKLCh hue wheels at fixed C are perceptually flat — use hand-picked RGB tables for deliberate palette design.
- [ ] Idle state (no audio) is handled by the registry's synthetic breathing signal, not per-viz. New viz should not add their own idle fallback unless it is intentionally different.
- [ ] VizPerf scale governor: resolution only ratchets down; never auto-recovers. A new viz must read `gp.canvas.width` every frame (not cache it) so it follows backing-store changes automatically.
- [ ] Wellness / breathing motion: `power2.inOut` for primary scale transitions; `sine.inOut` for holds; `elastic.out` for physical bounce. Avoid `linear` or `bounce` (mechanical / jarring).
- [ ] Film grain applied as a global overlay (`mix-blend-mode: overlay`, opacity ≤ 0.05) rather than computed per-viz.
- [ ] Tonemap/dither for LDR pipelines: if the authored color is already display-referred (hard-clamped to [0,1]), skip ACES; use dither only.
- [ ] `backtick` must not appear inside a WGSL template literal — silently breaks the JS template literal and produces a blank frame with no console error.
- [ ] WGSL has no ternary (`a ? b : c`). Agents writing WGSL must be explicitly told.

---

## Suggested decision-tree rows

| Question / task | Go to § |
|---|---|
| "What post-processing should this WebGPU viz use?" | § 1 (Post-processing stack) |
| "How should the viz respond to music?" | § 2 (Audio-reactive choreography) |
| "What fields does the audio frame expose?" | § 2 (table: Audio frame fields) |
| "The viz looks grey/monochromatic even with a palette" | § 3 (OKLCh collapse lesson) |
| "How should the viz look when no music is playing?" | § 2 (Idle state) |
| "The viz runs fine at 60 Hz but looks wrong at 120 Hz" | § 4 (Frame-rate independence) |
| "How do I add tuning controls to a new viz?" | § 5 (Live tuning workflow) |
| "How do I name / register a new viz?" | § 6 (Naming & catalog) |
| "Design a calm / breathing animation" | § 7 (Wellness motion) |
| "What easing should a breathing expand use?" | § 7 (Easing choices table) |
| "The san/stone material looks plastic/glassy" | § 8 (Zen garden material iteration) |
| "ACES is desaturating my colors" | § 1 and § 8 (LDR pipeline rule) |
| "Seekbar UX pattern" | § 9 (Seekbar / player UI) |
| "New viz causes flicker / photosensitivity concern" | Reviewer checklist, § 2 (beat rate-limit) |
| "Two viz crossfade / blend" | § 6 (dual-mode blend) |
| "Beat-aligned mode switch" | § 6 (beat-switcher) |

---

## UNVERIFIED

- Album art color extraction and direct palette seeding into viz shaders: not implemented as of this read. The code shows album art URLs loaded into `<img>` elements; the viz color system uses Spotify valence, not extracted image colors. Whether a canvas-based color extraction exists elsewhere in the codebase was not verified.
- The `siri-waveform.js` and `siri-waveform-canvas.js` entries use `<canvas 2d>` not WebGPU — their specific post-processing (if any) was not read.
- Whether `VizPerf.setEnabled(false)` is exposed in any UI toggle was not verified; the code has the API but the settings UI was not read.
- The `ambient-mode.js` file exists at repo root; its role in the idle synth path was not fully traced.
- `liquidglass.js` in the ripple repo: not read. Possibly a newer visual layer added after the main work.
- The `ripple` iOS native app may have a different easing parameter set (mentioned as "web→iOS parity done" in user memory); this doc covers the web version only.
- `tree-shatter-sandbox`: the lil-gui folders for ez-tree and three-pinata were listed but the specific param names were not read; tuning ranges were not verified.
