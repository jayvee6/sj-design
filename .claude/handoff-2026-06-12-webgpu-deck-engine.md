# Handoff — WebGPU deck engine (the new "presentation" system)
**Date:** 2026-06-12 · **Machine:** [Mac] · **Branch:** `main` @ `5e50767`, pushed · **Directional tag:** [Any]

---

## TL;DR

sj-design's presentation system was rebuilt on a **self-contained WebGPU engine**.
Instead of the old CSS-gobo / GSAP ambient template, decks now render a live
animated GPU atmosphere behind slide content, with an Apple-grade layout kit on
top. The proven engine + showcase is one file: **`showcase/webgpu-lookbook.html`**
(23 demo slides, verified slide-by-slide in real Chrome, console clean). Merged
to `main` via [PR #6](https://github.com/jayvee6/sj-design/pull/6). The
sj-design-expert Builder playbook now documents it as the new default
(`generation-playbook.md` §0). A **web-based builder** (Vercel-hosted, exports a
downloadable self-contained `.html`) is the next big piece — tracked separately.

This was sparked partly by Apple shipping "Dynamic Backgrounds" (animated
backdrops + Speed/Amplitude) and a per-slide layout picker in the newest Keynote.
Ours goes further: real WGSL shaders + a GPU compute particle system.

---

## What shipped (commits on `main`)

| Commit | What |
|---|---|
| `ceb402b` | The WebGPU look-book — 14 GPU scenes + initial layout kit |
| `5b24805` | Round out layout kit: section, statement, big fact, photo 3-up |
| `4cf7954` | Gallery + split: 3D glass frames, 3/4-up, video-ready |
| `d9af132` | Media layout: video/image in a 16:9 glass frame |
| `8b560f7` | Establish WebGPU engine as the new presentation default (skill doc) |
| `c026faa` | Merge PR #6 → main |
| `5e50767` | Soften mouse parallax to a hint |

---

## The engine — how it works

**One file:** `showcase/webgpu-lookbook.html`. Self-contained (only GSAP via CDN).
A single fullscreen WebGPU canvas (z-index 1) sits behind the slide deck (z 9);
HUD at 200. CSS-gradient `#bg` (z 0) is the no-WebGPU fallback. Inlined `SJGpu`
bootstrap (no external lib deps).

### Scene catalog (14)
All scenes are fullscreen-triangle fragment shaders sharing **one uniform
contract** — a 24-float (`96-byte`) buffer:

```
[0] elapsed   [1] reveal   [2] mouseX   [3] mouseY
[4] res.x     [5] res.y    [6] pulse    [7] beat
[8..11] colA  [12..15] colB  [16..19] colC  [20..23] colBg   (all vec4, rgb+1)
```

| Category | Scenes |
|---|---|
| Dynamic | Aurora Veil · Nebula Flow-Field · Ink Diffusion · Caustic Water |
| Minimal | Silk Gradient · Topographic |
| Bold | Hyperspace Warp · Halftone Riso · Scanline CRT |
| Material | Crystalline Refraction · Liquid Chrome · Voronoi Shatter |
| Editorial | Volumetric God-Rays |
| Live (GPU compute particles) | Constellation Field |

Scenes live in the `SCENES` object (`{name, frag}`, frag = WGSL appended to a
shared `PRELUDE` with hash/noise/fbm/aces/dither + the vertex shader). Each
scene gets its own render pipeline built in a loop. **Constellation** is special:
a compute pipeline updates 2,200 particles in a storage buffer; an instanced
additive render pass draws them over a `nebula` background fragment.

### Layout kit (10) — per-slide `data-layout`
`hero` (full-bleed left column) · `glass` (frosted panel) · `center` · `split`
(copy + media frame) · `agenda` (numbered) · `bg` (background-only, bottom
caption) · `section` · `statement` (one big line) · `bigfact` (gradient figure)
· `gallery` (`cols-3`/`cols-4`, 3D glass frames) · `media` (16:9 glass frame).

**Per-layout legibility** (no card/circle — Apple-hero style):
- hero / agenda / split / section → edgeless frosted-blur + directional darken (left)
- glass → frosted vibrancy panel
- center / statement / bigfact / gallery / media → soft full-screen frost

**Media:** gallery frames, split, and media accept `<img>`, `<video>`, or a
YouTube `<iframe>`, all wrapped in 3D glass frames (perspective fan + bevel +
sheen). `<video>` renders `autoplay muted loop playsinline`.

### Controls / behavior
- **Speed slider** (top-right): accumulates `simTime += dt*SPEED`; default `0.2×`.
- **Palette** per slide via `data-pal` (JS `PAL` map → uniform colors); sets `--accent`.
- **Scene crossfade** on nav via a `reveal` state machine (out→swap→in).
- **Parallax**: softened to a hint — DOM `depth*2.2/1.8` (~6px max), shader mouse `×0.45`.
- **Reduced-motion**: freezes time + parallax. **Fallback**: CSS gradient + working nav.

### Adding a scene / layout
- New scene: add `{name, frag}` to `SCENES` (frag uses the shared uniforms), add
  a `PAL` entry, give a slide `data-scene="key" data-pal="key"`. Pipeline builds
  automatically.
- New layout: add CSS under `.slide[data-layout="x"]` (+ legibility treatment),
  set `data-layout="x"` on the slide.

---

## Next steps (priority order)

1. **Web-based builder (the big one).** Browser UI on top of this engine: slide
   list (add/reorder/delete) + layout picker + backdrop picker + speed/palette
   controls + live WebGPU preview + content fields, exporting a self-contained
   `.html`. **Host on Vercel; users build and "download" a finished deck.**
   Reuse the engine's scene/layout code verbatim as the runtime. (Spawned as its
   own task earlier — chip `task_ce666ff0`.)
2. **Light/Dark variant per scene.** Engine is dark-only today; Keynote pairs
   Light/Dark for every Dynamic theme. A "Silk Light" was prototyped (loved it).
   Generalize in the engine: theme-aware text color + inverted (light-frosted)
   glass + lighter scrim, so every scene gets both and the builder + exports
   inherit from one source.
3. **Video-reactive backdrops (ambilight).** Sample average color from a
   same-origin / CORS `<video>` each frame (8×8 canvas → `getImageData` → smooth
   → palette uniforms `colA/B/C`) so the scene tints to the playing video.
   **Not possible for YouTube embeds** (cross-origin pixel lock) — needs a real
   video file. Guard so it no-ops on tainted/cross-origin sources.
4. **WebXR / OpenXR immersive mode.** Scene → 360 environment (you're *inside*
   the aurora/nebula), glass panels → world-space quads, head-tracked parallax,
   **controller haptics on slide transitions** (WebXR gamepad actuators). Ties to
   the FrameCast project (Mac → Steam Frame). WebGPU↔WebXR binding is still
   experimental (early 2026) — re-target the engine into an XR layer when it lands.
5. **Aspect-ratio selector** (16:9 / 4:3) for export.
6. **Category taxonomy** for the builder's theme picker (Dynamic/Minimal/Bold/
   Material/Editorial/Live) — already mapped above.
7. **JSON pipeline:** decide whether to bake scenes + `data-layout` into
   `scripts/build_presentation.py` (deck-level `"backdrop"` field) or let the web
   builder supersede it.

---

## Honest tuning notes / known issues

- **Nebula Flow-Field** is the softest scene — reads close to Aurora/Silk. Push
  the streak contrast / brighten stars, or cut it.
- **Eyebrow/sub text** can go slightly faint on the very brightest scenes
  (Caustic Water, Halftone). Nudge the darken or lift their color.
- **YouTube embeds throw Error 153 on `file://`** (null origin) — serve over
  http(s) (localhost or Vercel) and they play. Confirmed working over localhost.
- A throwaway `python3 -m http.server 8791` is/was running in `showcase/` for
  video/YouTube testing — kill it when done.

## Gotchas for whoever continues

- **Verify WebGPU in a VISIBLE browser** (chrome-devtools MCP), not a hidden one
  — WebGPU may not render headless. `file://` is fine for scenes; use http for
  YouTube/`<video>`.
- **chrome-devtools MCP can wedge** ("browser already running for
  …/chrome-devtools-mcp/chrome-profile"). Recover: `pkill -f
  'chrome-devtools-mcp/chrome-profile'`, then re-open a page.
- **Nav transition guard** ignores input mid-crossfade; the *first* keypress at
  load can be dropped during the initial reveal. When scripting nav, wait
  ~1.3 s between presses and poll `.slide.active`.
- WGSL uniform struct alignment is load-bearing — keep the 96-byte layout above
  if you touch it; vec4s aligned to 16.

---

## How to continue

- **See it:** serve and open — `cd showcase && python3 -m http.server 8791`,
  then `http://localhost:8791/webgpu-lookbook.html` (http needed for YouTube/video;
  `file://` works for scenes).
- **Build decks today:** edit the look-book directly, or invoke `sj-design-expert`
  (Builder) — `references/generation-playbook.md` §0 documents the engine.
- **Builder prototype:** start from chip `task_ce666ff0` (self-contained brief).
- **Sibling routing:** WGSL/GPU internals → `graphics-api-expert`; Mac→XR
  streaming → FrameCast project.

## Paper trail
- Engine + skill doc: this repo, `main` (commits above).
- Memory / vault checkpoint: **still pending** — capture engine + builder +
  light-mode + VR/haptics directions in `Projects/sj-design.md` and a Daily Note
  Session Log entry next session.
