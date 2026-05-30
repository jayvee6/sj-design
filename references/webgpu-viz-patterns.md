# WebGPU Viz Patterns — sj Reference

Implementation-level patterns for WebGPU visualizations in the Studio Joe stack.
Distilled from 153 production viz modules in `musicplayer-viz` (2026).
For the authoritative deep-dive, see the joeOS wiki: **WebGPU Scene Architecture — Best Practices**.

---

## VizShaderUtils — what each piece provides

```js
const SHARED_COLOR   = window.VizShaderUtils.colorUtils;    // oklch_to_linsrgb, oklab variants
const FULLSCREEN_VS  = window.VizShaderUtils.fullscreenVS;  // FSOut struct + vs_fs vertex shader
const COMPOSITE_UTIL = window.VizShaderUtils.compositeUtils; // aces() tone-map + sjDither()
```

**Include rule:** every shader module that calls a function must contain the string that defines it.

| Shader uses | Must include |
|-------------|-------------|
| `oklch_to_linsrgb()` | `SHARED_COLOR` |
| `vs_fs` / `FSOut` struct | `FULLSCREEN_VS` |
| `aces()` / `sjDither()` | `COMPOSITE_UTIL` |

Missing include on Metal = white screen pipeline failure. On D3D12 = may silently work.
**Always test on Mac Metal as the correctness bar.**

---

## Uniform struct — how to pack without bugs

### 1. Trace the layout byte by byte

```wgsl
struct U {
    viewProj: mat4x4<f32>,  // offset 0,   size 64
    camPosX:  f32,          // offset 64,  size 4
    camPosY:  f32,          // offset 68,  size 4
    camPosZ:  f32,          // offset 72,  size 4
    elapsed:  f32,          // offset 76,  size 4
    simGrid:  vec2<f32>,    // offset 80,  size 8  (align 8)
    span:     f32,          // offset 88,  size 4
    ...
}
// JS Float32Array index = byte offset / 4
// uni[16] = camPosX (64/4), uni[20] = elapsed (76/4), uni[22] = span (88/4)
```

### 2. Never use `vec3<f32>` in a uniform struct

`vec3<f32>` has alignment 16, size 12 — the 4-byte gap after it shifts everything downstream.
Replace with 3 separate `f32` fields or a `vec4<f32>`.

```wgsl
// ✗ Hazardous
camPos:  vec3<f32>,  // bytes 64-75, then 4-byte implicit pad
elapsed: f32,        // byte 80 — NOT 76 as you'd expect

// ✓ Safe
camPosX: f32,  // byte 64
camPosY: f32,  // byte 68
camPosZ: f32,  // byte 72
elapsed: f32,  // byte 76
```

### 3. JS index after a struct change

After adding/removing/reordering any field, re-derive **every** index that follows it. One-off errors here (especially on `blurX`/`blurY` at the end of the struct) produce a bloom blur that samples at a zero step size — the pass runs but has no effect.

---

## Multi-pass pipeline checklist

Standard bloom + composite architecture:

```
Scene pass  → rgba16float HDR (full-res, depth)
Bright-pass → rgba16float (half-res)
Blur H      → rgba16float (half-res)
Blur V      → rgba16float (half-res) → final bloom
Composite   → ACES + dither → swapchain format
```

**Gotchas:**
- Every pass needs `loadOp: 'clear'` — omitting it on an HDR texture gives TV-static on frame 0.
- Blur H and Blur V need separate uniform buffers (`blurBufH`, `blurBufV`) — same layout as the main uniform, with only `blurX`/`blurY` set differently.
- The composite shader needs **both** `SHARED_COLOR` (for color math) and `COMPOSITE_UTIL` (for `aces`/`sjDither`).

---

## Simulation textures (ping-pong)

```
SIM textures: texA, texB (rg32float or rgba32float)
Per frame: read texA → write texB, then srcIsA = !srcIsA
```

- `rg32float` / `r32float` are **unfilterable** — BGL must use `sampleType: 'unfilterable-float'` and `sampler: { type: 'non-filtering' }`.
- Use `textureLoad(tex, coord, 0)` in compute shaders (no sampler needed).
- Create two bind groups at init: `bgAtoB` and `bgBtoA`. Never recreate per frame.

---

## Idle visual state (required)

Every viz must show something without audio. The gallery picker shows a static screenshot; pure black or white is indistinguishable from broken.

### Patterns

```js
// Audio-proportional height → add a floor
const height = Math.max(audioLevel, 0.04);

// WGSL emission floor
let emission = max(audioDrivenValue * audioDrivenValue, 0.06);

// Time-driven ambient always on
let hue = masterH + sin(u.elapsed * 0.3) * 0.2;
```

### Camera / animation
- Drive `cam.az` or `rotAccum` continuously with `+= dt * BASE_SPEED`.
- Even a 0.05 rad/s rotation makes a static viz clearly alive.
- Bounce/wrap parameters so the viz never reaches a frozen state.

---

## Time initialization

`t` in `renderFn` is **elapsed seconds from viz start** (starts near 0).
`lastT` must use the same baseline:

```js
// ✓ In initFn
lastT = 0;

// ✗ Wrong — uses wall-clock seconds, making dt huge-negative on first frame
lastT = performance.now() / 1000;
```

A large negative `dt` in an exponential smoothing filter (`exp(-dt / τ)`) produces Infinity → NaN → black frame and potentially corrupted uniforms for the lifetime of the viz.

---

## Texture format quick reference

| Format | Filterable | Storage write | sampleType BGL |
|--------|-----------|--------------|---------------|
| `rgba8unorm` | ✓ | ✓ (with flag) | `float` |
| `rgba16float` | ✓ | ✓ | `float` |
| `rg32float` | ✗ | ✓ | `unfilterable-float` |
| `r32float` | ✗ | ✓ | `unfilterable-float` |
| `depth24plus` | ✗ | ✗ | — (depth attachment only) |

---

## Debugging quick reference

| Symptom | Check first |
|---------|------------|
| White screen (Mac) | Missing `COMPOSITE_UTIL` or `FULLSCREEN_VS` in shader string |
| Black without audio | All output proportional to audio signal — add idle floor |
| TV-static frame 0 | Missing `loadOp: 'clear'` on HDR render attachment |
| NaN / black forever | `lastT` initialized to `performance.now()/1000` instead of 0 |
| Bloom has no spread | `blurX`/`blurY` at wrong JS uniform index — check struct layout |
| Uniform garbage | `vec3<f32>` alignment — scalar after it reads 4 bytes too early |
| Correct on PC, broken on Mac | Metal validation stricter — find the undefined WGSL function |
| Sim frozen | Ping-pong not swapping — `srcIsA` flag not toggled, or wrong bind group |
