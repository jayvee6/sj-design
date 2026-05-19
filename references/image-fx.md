# Image FX — 3D explosion · fake-3D depth parallax · hover distortion

Three WebGL/Three.js techniques for turning a model or a flat image into a
tactile, motion-rich element. They share one idea: drive a vertex/fragment
displacement off a single normalized parameter (a `progress` tween, a mouse
vector, a smoothed hover value) so the effect is GSAP-tweenable and
audio-hookable like the rest of this toolkit.

Decoupled from any framework state — each is a standalone scene with a
one-line hook to wire the driver back to audio, scroll, or a deck step. Use
these for a logo that shatters on a title slide, a "spatial" hero photo that
follows the cursor, or a gallery whose tiles warp on hover.

These are independent reimplementations of techniques popularized by
**akella (Yuri Artyukh)** — see **Credits / Attribution** at the end. Study
his originals for the polished reference; the recipes below are original
synthesis (algorithm, parameters, gotchas), not his source.

---

## 1. 3D Object Explosion

**What it is.** A mesh appears whole, then bursts into hundreds of shards
that tumble outward and hang in space — or runs in reverse to *re-form* from
a cloud. One `progress` uniform in `[0,1]` drives the entire thing, so a GSAP
tween (or a deck step, or a beat) controls explode/implode with easing.

**Core algorithm**
- **Pre-fracture offline.** Don't try to split geometry at runtime. Author a
  fractured model (Blender Cell Fracture → export GLB) so each shard is its
  own set of triangles. Merge all shards into one or two `BufferGeometry`
  objects for a single draw call; identity is carried in per-vertex
  attributes, not separate meshes.
- **Per-shard attributes** (same value for every vertex of a shard):
  - `aCentroid` (vec3) — the shard's local center of mass.
  - `aAxis` (vec3) — a stable random unit axis for tumble.
  - `aDelay` (float) — `0..1` stagger so shards don't all leave at once.
- **Vertex shader** maps `progress` through a per-shard local time
  `p = clamp((progress - aDelay) / (1.0 - aDelay), 0.0, 1.0)`, then:
  1. translate the vertex into shard-local space (`pos - aCentroid`),
  2. rotate it about `aAxis` by `p * spinAmount` (Rodrigues),
  3. push the whole shard out along `normalize(aCentroid)` (radial) plus a
     low-freq curl/value-noise offset so the cloud isn't a perfect sphere,
  4. translate back and add the dispersal: `aCentroid + dir * p * spread`.
- **Easing belongs in the tween, not the shader** — keep the shader linear in
  `p`; let GSAP own the personality (`expo.out` for a snap, `power2.inOut`
  for a breathing loop).

Minimal shard displacement (illustrative — write your own noise/rotate):
```glsl
uniform float progress;
attribute vec3 aCentroid; attribute vec3 aAxis; attribute float aDelay;
// p: per-shard normalized time
float p = clamp((progress - aDelay) / max(1.0 - aDelay, 1e-3), 0.0, 1.0);
vec3 local = position - aCentroid;
local = rotateAxis(local, aAxis, p * 6.2831 * spin);   // your Rodrigues
vec3 dir = normalize(aCentroid + 0.001);
vec3 world = aCentroid + dir * p * spread + curl(aCentroid, p) * p;
gl_Position = projectionMatrix * modelViewMatrix * vec4(world + local, 1.0);
```

**Driving.** `gsap.to(uniforms.progress, { value: 1, duration: 1.6, ease: 'expo.out' })`.
Reverse the tween to re-form. Hook to audio: set `progress` from a smoothed
beat envelope (see `lib/envelopes.js`) for an explode-on-drop.

**Params that matter.** `spread` (world units a shard travels), `spin`
(turns over the tween), `aDelay` distribution (uniform = even bloom;
front-to-back = a "peel"), curl frequency (low = blobby, high = spiky).

**Gotchas.** Lighting on flat shards needs real per-face normals — recompute
after fracture or the cloud reads as flat. Use an env map / IBL: chips with
no specular look like cardboard. Frame the camera to the *exploded* bounds
(≈70° FOV pulled back) or shards clip on burst. Single merged geometry is
mandatory for perf — hundreds of separate meshes tank the draw call count.

**When to use.** Logo/product reveal on a title slide, a "deconstruction"
section, a beat-synced shatter in a music context.

---

## 2. fake3d — Depth-Map Parallax

**What it is.** A single photo gains convincing 3D parallax that tracks the
cursor (or device tilt), as if the camera moves slightly inside the scene.
No model, no point cloud — one image plus a grayscale depth map.

**Core algorithm**
- Two textures on a single full-cover quad: `uImage` (the photo) and
  `uDepth` (grayscale: white = near, black = far; midpoint = the focal
  plane).
- In the fragment shader, offset the lookup UV by the pointer, scaled by
  per-pixel depth so near things shift more than far things:
```glsl
float depth = texture2D(uDepth, vUv).r;
vec2 off = uMouse * (depth - 0.5) / uThreshold;   // uMouse in [-1,1]
vec3 col = texture2D(uImage, vUv + off).rgb;
```
- **Inertia.** Never feed the raw pointer. Lerp toward it every frame
  (`mouse += (target - mouse) * k`, `k ≈ 0.05`) — the lag is what sells the
  weight; raw tracking feels cheap and jittery.
- **Mobile substitute.** Swap pointer for `deviceorientation` beta/gamma,
  clamped to ≈±15° and normalized to the same `[-1,1]` range.
- Cover-fit the quad (object-fit: cover math in the shader) so the image
  never letterboxes as the container resizes.

**Driving.** Pointer → `uMouse` with the lerp above. For a hands-off hero,
drive `uMouse` with a slow Lissajous (`sin`/`cos` of time) so it drifts.
Audio hook: nudge `uThreshold` (parallax depth) with a bass envelope.

**Params that matter.** `uThreshold` (smaller = more dramatic parallax;
too small smears), depth-map midpoint (where the "screen plane" sits), lerp
`k` (weight/inertia).

**Gotchas.** This is a 2.5D fake — large offsets reveal disocclusion
smearing at depth discontinuities (hair, edges). Keep `uThreshold` modest
and motion subtle. The whole effect lives or dies on the depth map: paint
one by hand for hero shots, or generate with a monocular depth model
(e.g. MiDaS / Depth-Anything) and blur the seams.

**When to use.** A hero/cover photo that should feel alive, a portrait
section, a "spatial photo" moment in a deck.

---

## 3. Hover Distortion / Reveal

**What it is.** Image tiles in a grid that warp, RGB-split, and/or cross-fade
to a second image on hover — the interaction vocabulary of award-site
galleries. Each tile is its own WebGL plane synced to a DOM rect.

**Core algorithm**
- One textured plane per image, positioned/sized to mirror its DOM element
  (read `getBoundingClientRect`, convert to clip space). The DOM stays the
  layout source of truth; WebGL is a visual layer on top.
- A single smoothed `uHover` per tile in `[0,1]`: on enter target = 1, on
  leave = 0, lerp each frame (`k ≈ 0.1`). Every effect is a function of it:
  - **Displacement**: push UVs by a displacement-map texture × `uHover`.
  - **RGB split**: sample R/G/B at slightly offset UVs, offset ∝ `uHover`
    (and optionally ∝ pointer velocity for a "drag" smear).
  - **Reveal**: `mix(texA, texB, smoothstep(0.0, 1.0, uHover))` to fade to a
    second image or a duotone of the first.
```glsl
float h = uHover;                       // already smoothed on the CPU
vec2 d = texture2D(uDisp, vUv).rg * h * 0.1;
vec3 c = vec3(
  texture2D(uTex, vUv + d + vec2(0.02*h, 0.0)).r,
  texture2D(uTex, vUv + d).g,
  texture2D(uTex, vUv + d - vec2(0.02*h, 0.0)).b);
```

**Driving.** Pointer enter/leave set the per-tile target; the lerp does the
rest. Pointer position within the tile can drive a directional bend. For a
deck, drive `uHover` from the active-slide index instead of the mouse.

**Params that matter.** Smoothing `k` (snappy vs. liquid), displacement
strength, RGB-split magnitude, whether split also tracks pointer velocity.

**Gotchas.** Keep the WebGL planes pixel-locked to their DOM rects on scroll
and resize or the overlay drifts. Throttle to tiles actually near the
viewport. Pre-decode textures (`createImageBitmap`) so the first hover
doesn't hitch.

**When to use.** A portfolio/gallery section, a "selected work" grid, any
interactive image wall in a presentation or microsite.

---

## Patterns worth carrying

- **One normalized driver.** Explosion `progress`, fake3d `uMouse`, hover
  `uHover` — all `[0,1]`-ish scalars/vectors. That uniformity is what makes
  every effect GSAP-tweenable, audio-hookable, and deck-step-drivable with
  the same plumbing as the rest of this toolkit.
- **Smooth on the CPU, render linear on the GPU.** Inertia/lerp and easing
  live in JS; the shader stays a clean function of the driver. Easier to
  reason about, retune, and reuse.
- **DOM is the layout truth; WebGL is the skin.** For anything that coexists
  with page content (hover grids, fake3d heroes), mirror DOM rects rather
  than rebuilding layout in GL.

---

## Credits / Attribution

These techniques are independent reimplementations of work by
**akella — Yuri Artyukh** (<https://github.com/akella>), a prolific creative
developer (he also teaches them on his YouTube channel). Study the originals
as the reference implementations:

- **3D Object Explosion** — <https://github.com/akella/ExplodingObjects>
  No `LICENSE` file in the repo; the README states the **Codrops license**:
  free to use in personal and commercial projects, but you may not resell or
  redistribute it as-is, and a free plugin built from it must carry a visible
  mention and link back to the original.
- **fake3d** — <https://github.com/akella/fake3d>
  No `LICENSE` file; README marked **© Codrops 2018**, same **Codrops
  license** terms as above.
- **webgl-mouseover-effects** — <https://github.com/akella/webgl-mouseover-effects>
  **MIT License** (`LICENSE` present; Copyright © 2009–2020 Codrops).

Nothing here is copied from those repos — the recipes above are original
descriptions of the technique. **Any artifact this skill produces using these
techniques must keep a visible credit to akella with a link to the relevant
repo** (a small footer/credit line in the generated HTML is sufficient), in
the spirit of the Codrops license and as good practice generally.
