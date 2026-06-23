# wwwtyro — Rye Terrell (procedural / atmospheric reference)

Aesthetic and technique reference for the skill's procedural atmospheric FX
(Perlin blobs, starfields, the `deep-space` theme). Rye Terrell's browser-GPU
work is the same lineage we want: **generative, GPU-driven, dependency-free.**

- Site: https://wwwtyro.net
- Repos: https://github.com/wwwtyro

## Most relevant to this skill

- **space-2d** (https://github.com/wwwtyro/space-2d) /
  **Procedural 2D Space Scenes in WebGL**
  (https://wwwtyro.net/2016/10/22/2d-space-scene-procgen.html) — point stars via
  exponential-distribution sampling, 5-octave Perlin nebulae with
  noise-displaced lookups (anti-tiling), distance-field stars/sun, additive
  compositing. The reference pipeline for richer `deep-space` / starfield
  backgrounds.
- **space-3d** (https://github.com/wwwtyro/space-3d) — the 3D successor;
  **Unlicense (public domain)**. A single still export from
  https://tools.wwwtyro.net/space-3d/index.html works as a baked atmospheric
  backdrop for the `deep-space` theme (no attribution, no runtime dep).
- **perlin.js** (https://github.com/wwwtyro/perlin.js) — clean 1/2/3-D Perlin
  noise reference for the procedural blob / fog FX.
- **glsl-atmosphere** (https://github.com/wwwtyro/glsl-atmosphere) — physical
  sky (Rayleigh + Mie) if a theme ever wants a true atmospheric gradient.

## Note

Techniques only — implementations here stay self-contained and dependency-free
per the skill's constraints. space-3d is public domain; the others are
referenced for approach, not vendored.
