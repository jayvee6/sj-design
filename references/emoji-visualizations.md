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

**What it is.** Themed emoji fireworks that launch with a true parabolic arc (manual physics integration, not a tween), detonate at a randomly chosen apex, and burst into matching debris in a theme-paired **shape** — peony, ring, star, heart, or smiley. Every launch picks a fresh angle, z-depth layer, and rocket/debris/shape theme set. Runs on a timer by default; wires to beat detection with one line.

**Core algorithm — rocket**
- Per-frame integration: `vy += GRAVITY * dt; x += vx * dt; y += vy * dt;` with `GRAVITY = 520` px/s². A `dt` tween would *look* like an arc but the peak timing would be wrong on speed changes — manual Euler keeps it correct.
- Launch angle: `90° ± 20°` from vertical (θ = 70°–110°). Pure vertical reads boring; wider than ±20° starts to look like lateral artillery, not fireworks.
- Detonation: rocket stores `explosionY` picked randomly in a band — `[0.15H, 0.50H]` from the top (so bursts stay in the upper half of the sky, never at the edges). When `r.y <= r.explosionY`, remove the rocket and call `spawnBurst`.

**Core algorithm — burst**
- `count = 50` particles per burst. Each particle gets a *launch-velocity vector* from a shape function (see **Burst shapes** below): `v = shapeVector(shape, i, count)` returns a unit-ish `(x, y)`; then `mag = speed * rand(spread)`, `vx = v.x * mag`, `vy = v.y * mag - rand(lift)`. The `-lift` fights gravity for a split second so the burst *blooms* before falling.
- Particle `life ∈ [1.2, 2.0]` seconds, fade is `(1 - age/life)²` — quadratic fadeout reads cleaner than linear.
- Particle gravity is `0.65 * GRAVITY` — embers hang longer than the rocket would.

**Burst shapes.** This is a *velocity-field* system — every particle starts at the burst center and flies out, so a "shape" is **not** a tween to a position; it's a function `index → unit launch-velocity vector`. Gravity then acts on all of them, so the figure is legible at the bloom and disperses naturally a beat later (same physics aesthetic as the plain peony — don't try to "hold" the shape). Two rules make shapes swappable without retuning the engine:

1. **Normalize to mean radius ≈ 1.** Every shape's vectors are scaled so their average magnitude matches the peony's `|(cosθ, sinθ)| = 1`. Then changing shape never changes burst size — only the speed/`force`/depth terms do. (Heart's raw curve spans ≈ ±16; divide by 15. Star's rose multiplier already averages 1. Smiley is authored directly in unit space.)
2. **Per-shape `spread` + `lift`, not one global pair.** `spread` is the radial magnitude jitter: a wide spread (`0.6–1.3`) fills a *disc* — right for a peony bloom — but smears any figure that encodes position. A figure shape needs a *tight* spread (`~0.9–1.06`) so particles land on the curve, plus a gentler `lift` (a big random per-particle lift distorts the figure vertically). Table actually in use:

   | shape  | spread       | lift     | note |
   |--------|--------------|----------|------|
   | peony  | `0.60–1.30`  | `20–80`  | loose, lofty classic bloom |
   | ring   | `0.94–1.06`  | `16–44`  | same geometry as peony; tight spread = thin shell |
   | star   | `0.86–1.05`  | `14–36`  | rose curve supplies the radial variation |
   | heart  | `0.90–1.06`  | `12–30`  | hold the curve |
   | smiley | `0.95–1.05`  | `10–24`  | hold the face |

The catalog (canvas Y is screen-down, so `−y` is up):

- **Peony** — `t = (i/count)·2π + jitter(±0.12)`; `(cos t, sin t)`. The small angular jitter prevents banding into a visible wheel.
- **Ring** — identical geometry to peony; the thin "shell" read comes entirely from `ring`'s tight `spread`, not the vector.
- **Star** — rose-curve radius fluctuation: `m = 1 + depth·sin(spokes·t)`, `(cos t · m, sin t · m)`. `spokes = 5`, `depth = 0.42` → `m ∈ [0.58, 1.42]`, mean 1. `depth` is "how deep the points cut"; `spokes` is the point count.
- **Heart** — classic parametric heart: `x = 16 sin³t`, `y = -(13 cos t − 5 cos 2t − 2 cos 3t − cos 4t)`, both ÷ 15. The leading `−` on `y` flips the curve so the heart points *up* in screen-down coords.
- **Smiley** — compound. Partition the `count` indices across four features (≈52% outline, ≈11% each eye, remainder smile) and emit a velocity toward each feature's position in unit space (outline radius = 1): outline = peony circle; eyes = small `r≈0.10` clusters at `(±0.36, −0.34)`; smile = the **bottom** arc of a circle (`a ∈ [0.18π, 0.82π]`, `(cos a · 0.64, 0.20 + sin a · 0.52)`) — in screen-down coords a happy mouth is the lower arc, not the upper one. It reads for the bloom beat, then gravity pulls the face apart like any burst.

**Theme coupling.** `shape` is a field on each `THEMES[]` entry, so the burst reinforces the story: 💘 → heart, 🪄/⚡/🎄/🐉 → star, 🎃 → smiley (jack-o'-lantern), 🍾/👽 → ring (champagne pop / UFO halo), everything else → peony. Forcing a shape independent of theme is a one-arg override (`launch(shape)`), used by the demo's `1`–`5` keys.

**Depth layers.** Each launch samples `z ∈ [0, 1]`:
- `scale = 0.72 + z * 0.60` (farther = smaller)
- `alpha = 0.70 + z * 0.28` (farther = dimmer)
- Launch `speed *= jitter * scale` (farther = slower across the sky — parallax)
- `xSpread` shrinks with depth too (farther rockets clustered more tightly, like a distant show)
- Draw list is `rockets.concat(particles).sort((a,b) => a.z - b.z)` — far items render behind near items.

**Themes.** Each launch picks one from `THEMES[]`: `{ rocket: '🚀', debris: ['✨','💥','🌟','🎉'] }` etc. Rocket emoji and debris set are paired so the explosion reads as thematically related. Adding a theme is zero-friction — push to the array. A few that work well: rocket/sparks, heart/hearts, pumpkin/ghosts, champagne/confetti, octopus/sea-life, lightning/stars, dragon/fire.

**Sky trails.** Instead of clearing, fill the canvas with `rgba(4, 6, 16, α)` every frame — the residual of the previous frame is the comet tail. `α` is the trail-length knob: residual after `n` frames ≈ `(1−α)ⁿ`. `α = 0.60` (current) ≈ a tight 2-3-frame tail; `0.40` is a longer smear; `0.85+` is near-instant clear (almost no trail). Too low (`≤0.30`) reads as motion blur, not sparks.

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
