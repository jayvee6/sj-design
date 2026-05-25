# Cosmic Disco → musicplayer-viz — Port Brief

**Audience:** a fresh Claude/engineer session with no prior context. Read this
top to bottom before touching code. Goal: implement the `cosmic-disco` scene
as a registered visualizer in the **musicplayer-viz** web app.

---

## 0. Canonical source (the thing you are porting)

- **`~/Documents/Development/sj-design/showcase/scenes/cosmic-disco.html`**
  — the canonical build, **`cd-015`**. This is a standalone self-contained
  HTML: raw WebGPU, WGSL in an inline JS template literal, a **3-pass
  temporal-denoise pipeline** (scene → resolve → present), an honest perf
  HUD, build-id + `srcHash`. Committed/pushed to `github.com/jayvee6/sj-design`
  (commit `a533edc`). **This is the look + algorithm of record.**
- `cosmic-disco-threejs.html` (same dir) — a **single-pass WebGL/GLSL
  reference, NO TAA**. Useful only to read the scene math in GLSL; it is
  noisier and is *not* the target quality. Not a lockstep twin anymore.

The scene: a dense lat/lon-faceted **mirror disco ball** (per-tile jitter,
colored glints, gold city-lights) inside a **lush volumetric pink/gold
nebula** (domain-warped FBM), with **light shafts that are physically
bounced off the bright mirror tiles from two pin-spots and revealed only by
the fog** (they sweep as the ball spins). Analytic silhouette/grout AA.
ACES tonemap. ~60fps locked on Apple M-series.

---

## 1. THE decision you must resolve first (do not skip)

musicplayer-viz's documented viz contract is **single full-screen
fragment shader, single render pass, NO postprocessing**. cosmic-disco's
*good* build is **3-pass** (scene→HDR, reprojection-free temporal-denoise
resolve, present+ACES). **The single-pass version was rejected by Joe as
too noisy** — the volumetric light shafts only become coherent with the
multi-pass temporal denoise. This is non-negotiable for visual quality.

**Confirmed direction (Joe, 2026-05-16):** musicplayer-viz **will gain
opt-in multi-pass temporal-resolve support** — this is decided, not an
open question. The "single-pass, no-postprocessing" contract becomes
"single-pass by default; a viz may declare it needs multi-pass + a
temporal-resolve stage." MSAA is explicitly **not** the mechanism — these
viz are full-screen fragment shaders with no primitive edges, so MSAA does
nothing for procedural/volumetric noise.

So the port is:

- **Use / build the app's opt-in multi-pass path.** Read the current
  `~/Documents/Development/musicplayer-viz/app.js` + the `studiojoe-viz`
  skill to see if the generic plumbing already exists (registry lets a viz
  request N targets / a resolve pass). If it does, register cosmic-disco as
  a multi-pass viz and supply the 3 passes. **If it does not yet exist,
  building that generic capability is part of this work** (not a blocker to
  negotiate away): an offscreen HDR `rgba16float` scene target at render
  res, two ping-pong history textures, a resolve pass, a present pass —
  exposed generically so the future blackhole sim reuses it, with a
  **single-pass fallback + device gating** (weak GPU / iOS → fall back, or
  MetalFX on native) since multi-pass is opt-in, not global.
- Do **not** ship the single-pass build as the result — Joe rejected it as
  too noisy; the reprojection-free multi-pass temporal denoise is
  non-negotiable for coherent light shafts.

Treat the opt-in multi-pass temporal capability as the primary
deliverable; the scene shader itself is largely a copy of `cd-015`.

---

## 2. Target integration contract (VERIFY against the live app)

From the `studiojoe-viz` skill + memory; **re-verify against the current
`~/Documents/Development/musicplayer-viz/app.js` — it may have changed:**

- Register via `window.Viz.register({ id, label, kind:'webgpu', initFn,
  renderFn, teardownFn, controls })`. `initFn` is lazy (first activation),
  `await window.initWebGPU()` then read `window.vizGPU`.
- `window.vizGPU = { adapter, device, queue, context, format, canvas, dpr }`
  — the shared WebGPU surface. Your offscreen/history textures sit on this
  `device`. Honor `teardownFn` (destroy textures, bind groups).
- Audio: `window.AudioEngine.currentFrame()` →
  `{ time, bass, mid, treble, beatPulse, bpm, isBeatNow, bassHistory,
  magnitudes, valence, energy, danceability, tempoBPM, width, height }`.
- Time/motion: the app drives `renderCurrent(visualClock, frame)` with a
  speed-scaled `visualClock` (see `window.AnimSpeed`, parity-locked with
  iOS). Integrate camera/rotY off the app's clock, NOT your own rAF.
- The app already has its own accurate debug HUD (`_hud`). **Drop the
  standalone HUD/build-id machinery from the port** — but keep the perf
  *discipline* (below).

---

## 3. Signal mapping (cosmic-disco standalone → app)

The standalone uses synthetic `SJPulse`. Replace with the AudioFrame:

| standalone (`signals()`) | musicplayer-viz AudioFrame |
|---|---|
| `bass` (SJPulse.kick) | `frame.bass` |
| `mid` (SJPulse.wave) | `frame.mid` |
| `treble` (SJPulse.flicker) | `frame.treble` |
| `beat` (SJPulse.kick fast) | `frame.beatPulse` (raw, for sharp punches) |
| `amp` (= mean) | `(bass+mid+treble)/3`, or `frame.energy` |

Apply EMA smoothing where the standalone relied on SJPulse's smoothness
(typical taus sec: bass 0.5, mid 0.8, treble 0.3, beat 0.25 — keep raw
`beatPulse` for the sharp beam/halo punches). Camera orbit + `rotY` must
integrate from `visualClock` (clamped dt) for iOS parity.

---

## 4. The 3-pass pipeline you must reproduce (from cd-015)

Read the exact WGSL in `cosmic-disco.html`. Structure:

1. **Scene → HDR target** (render res). Outputs linear pre-tonemap color
   in `.rgb` and a **contribution-weighted mean scatter distance** depth
   proxy in `.a` (NOT a constant — a constant smears the fog). IGN-animated
   march jitter (procedural, no texture asset). NO ACES here.
2. **Resolve → ping-pong history** (same res). **Reprojection-FREE**:
   sample history at the *same* pixel, hard-clamp it to the current 3×3
   neighbourhood (±1.0σ), low feedback (`mix(0.55,0.45,flash)`), luminance
   flash-reject. (Reprojection TAA was tried twice and *intrinsically
   smears* a pure volumetric with no motion vectors — do NOT reintroduce
   camera reprojection. This is the hard-won conclusion.)
3. **Present → screen**: sample resolved history, ACES + fine grain.

cd-015 renders at native res (no upscale) and still holds locked-60 on
M-series. For the app, pick render scale from the app's perf budget /
device; the temporal denoise is what makes the shafts coherent — keep it.

Volumetric march = adaptive empty-space-skip (coarse stride through
empty/sub-threshold, fine steps in cloud, Beer–Lambert with the *actual*
step length, transmittance early-out). Beams accumulate in a **separate
buffer with a soft-knee** (`bAcc/(1+0.45·bAcc)`) so a direct camera hit is
a bounded flare, not a whiteout.

---

## 5. Non-negotiables / hard-won lessons (apply from frame one)

- **Measure GPU throughput, not rAF.** Never EMA-smooth a perf number.
  Use the app's `_hud` (windowed avg + p99 low1% + drops/s). A meter that
  lied (rAF+EMA) cost this project many wasted iterations.
- **Never put a backtick in a shader comment.** The shader is a JS
  template literal; one backtick silently kills the whole module (black
  screen, no HUD). It bit this project twice. After every shader edit:
  `grep -n '\`' <file>` — only the template delimiters may match.
- **Lossless-first optimization.** Exhaust visually-lossless shader wins
  (gating, CSE, noise reuse, alloc hoists, adaptive march) before cutting
  step count / resolution. Look-affecting cuts need Joe's sign-off.
- **Physical models converge; screen-space fakes don't.** The beams went
  fake-starburst → physical mirror-tile bounce; keep them physical.
- **HDR accumulate, tonemap last.** ACES in the present pass; soft-knee
  bright features (beams).
- **iOS parity:** per the parity rule, tuning (sin/cos freqs, reactivity,
  EMA taus, color, speed ceilings) must eventually mirror to the iOS
  Metal side. The reprojection-free temporal denoise maps cleanly to a
  Metal multi-pass / MetalFX path later.
- **Instrument every prototype from frame one** (perf HUD + build id);
  measure-as-you-build. Open every iteration in Chrome (`open -a
  "Google Chrome" <url>`); the editor preview panel is not the target —
  never claim a render correct unseen.

---

## 6. Port checklist

1. Read `app.js` + the `studiojoe-viz` skill; confirm the current registry
   API and whether multi-pass viz are supported. Resolve §1.
2. Create the viz module (match the repo's `viz/*.js` convention). Lazy
   `initFn`: build the 3 pipelines, HDR + 2 history textures on
   `window.vizGPU.device`, sized to the app's render target; bind groups.
3. Port the WGSL from `cosmic-disco.html` (scene + resolve + present).
   Keep the uniform struct; swap synthetic signals for AudioFrame; drive
   time/rotY/camera off `visualClock`.
4. `renderFn(visualClock, frame)`: write uniforms, run the 3 passes,
   ping-pong history. `teardownFn`: destroy all textures/bind groups.
5. `grep` backticks. Verify on the app's HUD: locked target fps, GPU
   throughput, no drops; shafts coherent (not speckly); no whiteout on
   beats; no full-frame smear.
6. Mirror tuning to iOS Metal per the parity rule when that port happens.

---

## 7. Validation (done = all true)

- Light shafts read as clean coherent rays (the whole reason for the
  multi-pass denoise), not per-pixel speckle.
- No blinding whiteout when a shaft points at the camera (soft-knee works).
- No full-frame temporal smear (reprojection-free; do not add reprojection).
- App HUD shows the device's target fps with GPU throughput (not rAF) and
  ~0 drops; teardown releases GPU memory on viz switch.
- Audio-reactive: visibly responds to a staccato kick (beat coupling not
  over-smoothed).

> Source of truth for the algorithm and exact constants:
> `sj-design/showcase/scenes/cosmic-disco.html` @ build `cd-015`
> (repo commit `a533edc`).
