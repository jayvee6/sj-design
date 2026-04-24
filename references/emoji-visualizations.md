# Emoji Visualizations

Three canvas-2D techniques that composite emoji glyphs into full-screen animated scenes. Ported from [musicplayer-viz](../../musicplayer-viz) where they were FFT-reactive; here they're decoupled from audio so they run as standalone presentation effects, with a one-line hook to wire them back to sound if the caller has it.

All three rely on emoji as a font glyph, not images. Use `serif` or `-apple-system` — the system falls back to Apple Color Emoji / Noto Color Emoji automatically. No asset pipeline, no texture atlas.

**Live demos** (all self-contained, open directly):
- [`showcase/emoji-waves.html`](../showcase/emoji-waves.html)
- [`showcase/emoji-vortex.html`](../showcase/emoji-vortex.html)
- [`showcase/emoji-fireworks.html`](../showcase/emoji-fireworks.html)

---

## 1. Concentric Waves

**What it is.** Six rings of emojis pulsing outward from screen center, each ring reading an older audio value than the one inside it so a bass hit "ripples" through time. Alternating spin direction per ring keeps the pattern from locking into a static wheel.

**Core algorithm**
- `N` rings centered at `(W/2, H/2)`. Ring 0 is a single emoji; ring `k` holds `k*6` evenly-spaced emojis. Totals: 1, 6, 12, 18, 24, 30.
- Per ring: `baseR = (ring+1) * min(W,H) * 0.09`, `radius = baseR * (1 + delayedBass * 0.45)`.
- **Delayed-bass ripple**: keep a FIFO of the last 16 bass values. Ring `k` reads `history[min(k*2, 15)]`. Ring 0 reads the live value. The time lag is what makes the pulse *travel*.
- **Alternating spin**: `dir = (ring % 2 === 0) ? +1 : -1`; every ring rotates around the shared `waveSpin` accumulator (`+= 0.008` per frame at 60fps).
- Per emoji: `angle = (j/count) * 2π + waveSpin * dir`, pick glyph `EMOJIS[(ring * 4 + j) % EMOJIS.length]`.
- Size: `14 + ring*3 + delayedBass * 18` px — outer rings naturally larger, all rings inflate on pulse.

**Audio hook.** Replace `computePulse(t)` with an FFT reader. Expected shape:
```js
// Return a bass value in [0, 1]; push it onto a 16-slot ring buffer.
function computePulse(t) {
  const bass = /* your bass band average from getByteFrequencyData */;
  bassHistory.unshift(bass);
  bassHistory.pop();
  return bass;
}
```

**Render cadence.** One `fillText` per emoji per frame — with 91 emojis total this is cheap on any modern browser, no off-screen caching needed.

---

## 2. Tunnel Vortex

**What it is.** 280 emojis arranged in a Fibonacci phyllotaxis spiral, rotating together while bass inflates their size in unison. Reads as a tunnel because the outer emojis are larger (farther away in inverted depth) and soft-faded into the canvas edge.

**Core algorithm**
- Phyllotaxis placement: for `i` in `0..279`, `angle = i * GOLDEN_ANGLE + tunnelRot` where `GOLDEN_ANGLE = 2.39996323` radians; `r = phylloSpread * sqrt(i) * scale`. This is the sunflower-seed formula — it naturally produces Fibonacci-arm spirals with no repetition or gaps.
- **Per-emoji size**: `(5 + sqrt(i) * 6.5) * scale * (1 + bass * 0.5)`. Outer emojis larger (the tunnel "wall"), center emojis smallest.
- **Tunnel rotation**: `tunnelRot += 0.003 + mid * 0.012` per frame. Mid-frequency energy drives the spin; bass stays decoupled (so size and rotation react to different things — a kick doesn't spin the tunnel, a synth sweep does).
- **Soft edge fade**: compute `edge = min(W,H) * 0.52`; `alpha = clamp(1 - (r - 0.8*edge) / (0.2*edge), 0, 1)`. Emojis past `edge` are invisible; emojis in the outer 20% band fade in.
- **Outer-first draw order**: iterate `i = PHYLLO_COUNT-1 down to 0` so small center emojis overdraw the large outer ones, preserving the tunnel illusion.

**Performance pattern — glyph cache.** Don't `fillText` 280 times per frame. Rasterize each unique emoji once into an off-screen canvas at some fixed `CACHE_SIZE` (80px works well) at `font = CACHE_SIZE * 0.82`, then composite with `drawImage(cache[e], x-half, y-half, size, size)`. Roughly 10× faster than repeated `fillText` in Chrome/Safari.

```js
const emojiCache = (() => {
  const map = {};
  EMOJIS.forEach(e => {
    const oc = document.createElement('canvas');
    oc.width = oc.height = CACHE_SIZE;
    const octx = oc.getContext('2d');
    octx.font = `${CACHE_SIZE * 0.82}px serif`;
    octx.textAlign = 'center'; octx.textBaseline = 'middle';
    octx.fillText(e, CACHE_SIZE / 2, CACHE_SIZE / 2);
    map[e] = oc;
  });
  return map;
})();
```

**Audio hook.** Needs two bands:
```js
function computePulse(t) {
  return {
    bass: /* low-band FFT average, [0,1] */,
    mid:  /* mid-band FFT average, [0,1] */,
  };
}
```

---

## 3. Fireworks

**What it is.** Themed emoji fireworks that launch with a true parabolic arc (manual physics integration, not a tween), detonate at a randomly chosen apex, and burst into matching debris. Every launch picks a fresh angle, z-depth layer, and rocket/debris theme pair. Runs on a timer by default; wires to beat detection with one line.

**Core algorithm — rocket**
- Per-frame integration: `vy += GRAVITY * dt; x += vx * dt; y += vy * dt;` with `GRAVITY = 520` px/s². A `dt` tween would *look* like an arc but the peak timing would be wrong on speed changes — manual Euler keeps it correct.
- Launch angle: `90° ± 20°` from vertical (θ = 70°–110°). Pure vertical reads boring; wider than ±20° starts to look like lateral artillery, not fireworks.
- Detonation: rocket stores `explosionY` picked randomly in a band — `[0.15H, 0.50H]` from the top (so bursts stay in the upper half of the sky, never at the edges). When `r.y <= r.explosionY`, remove the rocket and call `spawnBurst`.

**Core algorithm — burst**
- `count = 50` particles per burst. For each: `theta = (i/count)*2π + jitter(±0.12)`, `mag = speed * rand(0.6, 1.3)`, `vx = cos(θ)*mag, vy = sin(θ)*mag - rand(20, 80)` (the `-rand(20,80)` lift fights gravity for a split second so the burst *blooms* upward before falling).
- Particle `life ∈ [1.2, 2.0]` seconds, fade is `(1 - age/life)²` — quadratic fadeout reads cleaner than linear.
- Particle gravity is `0.65 * GRAVITY` — embers hang longer than the rocket would.

**Depth layers.** Each launch samples `z ∈ [0, 1]`:
- `scale = 0.72 + z * 0.60` (farther = smaller)
- `alpha = 0.70 + z * 0.28` (farther = dimmer)
- Launch `speed *= jitter * scale` (farther = slower across the sky — parallax)
- `xSpread` shrinks with depth too (farther rockets clustered more tightly, like a distant show)
- Draw list is `rockets.concat(particles).sort((a,b) => a.z - b.z)` — far items render behind near items.

**Themes.** Each launch picks one from `THEMES[]`: `{ rocket: '🚀', debris: ['✨','💥','🌟','🎉'] }` etc. Rocket emoji and debris set are paired so the explosion reads as thematically related. Adding a theme is zero-friction — push to the array. A few that work well: rocket/sparks, heart/hearts, pumpkin/ghosts, champagne/confetti, octopus/sea-life, lightning/stars, dragon/fire.

**Sky trails.** Instead of clearing, fill the canvas with `rgba(4, 6, 16, 0.30)` every frame. The 70% alpha over last frame leaves a 3-4-frame comet tail behind each particle before it fades to black.

**Audio hook.** One-liner:
```js
if (audioFrame && audioFrame.isBeatNow) {
  launch();
  lastAutoFireT = t;  // suppress idle timer on beats
}
```
With no audio, the idle timer (`IDLE_INTERVAL = 1.8s`) keeps the show going.

---

## Patterns worth carrying across all three

- **Logical pixels via DPR.** Set `canvas.width = innerWidth * dpr`, then `ctx.setTransform(dpr, 0, 0, dpr, 0, 0)` so all your coordinates are in CSS pixels. Without this, emoji render at 50% size on retina and at blurry integer positions on fractional DPR.
- **`textAlign = 'center'; textBaseline = 'middle'`** — always. Emoji glyphs have different baselines than Latin text; without these two lines every positioning calculation will be off-center by 8–15px.
- **`serif` or `-apple-system`** for emoji fonts — NOT a specific face. System emoji fallback is the right abstraction; pinning a font breaks cross-platform rendering.
- **Synthetic pulse as default.** Write `computePulse(t)` as the extension point. Ships runnable with zero dependencies; audio reactivity is additive, not required.
