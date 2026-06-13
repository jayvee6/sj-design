# Generation playbook — decks, motion primitives, emoji viz, WebGPU scenes

The Builder mode of sj-design-expert. Absorbed from the former `presentation`
skill (2026-06-12) and upgraded with the distilled first-party references.
Output is always a **self-contained `.html` file** — no dependencies to
install, portable per `studio-design-system.md` §11.

**Paths:** all shared assets live at the **sj-design repo root**
(`~/Documents/Development/sj-design/`): `showcase/`, `lib/`, `scripts/`,
`assets/template.html`, `fonts/`, root `references/`.

---

## 1. Motion primitives catalog

Standalone, copy-pasteable demos in `showcase/`. Each runs zero-dependency on
a synthetic time pulse (`lib/synthetic-pulse.js`, SJPulse) and has a one-line
hook to wire back to audio.

| Family | Demos | Detail reference |
|---|---|---|
| Emoji visualizations | `showcase/emoji-waves.html` (concentric delayed-bass rings) · `emoji-vortex.html` (golden-angle phyllotaxis tunnel) · `emoji-fireworks.html` (peony/ring/star/heart/smiley parabolic bursts) | root `references/emoji-visualizations.md` |
| Dancing formations | `showcase/emoji-formations/`: triangle-orbit · hex-swarm · heart-pulse · infinity-loop · star-formation · shape-morph | — |
| WebGPU scenes | `showcase/scenes/`: wire-terrain (raymarched FBM) · disco-chrome (mirror ball) · neon-oscilloscope (ribbon waves). One fullscreen-triangle fragment shader each, inline WGSL, single pass. Perf knobs in `lib/webgpu-bootstrap.js` (SJGpu, `{maxDPR, renderScale}`) | `viz-motion-craft.md` §1, §4 for post/perf rules; graphics-api-expert for WGSL internals |
| Image FX | 3D object/logo explosion (pre-fractured GLB shards, one `progress` uniform) · fake-3D depth-map parallax · hover distortion/reveal. Recipes only, no bundled demo | root `references/image-fx.md` — **akella attribution mandatory** (visible credit + repo link in any output; `studio-design-system.md` §14) |
| Atmospheric FX | `showcase/atmosphere.html` (combined) + split `atmosphere-{gobo,starfield,bokeh,fog,grain}.html` | `studio-design-system.md` §6 |

Shared lib (`lib/`): `canvas-size.js` (SJCanvas, DPR sizing) ·
`synthetic-pulse.js` (SJPulse) · `envelopes.js` (VizEnv attack/release) ·
`webgpu-bootstrap.js` (SJGpu). Demos load these with an inline fallback so
each file stays single-file portable.

**Builder boosts (new — apply to every primitive build):**
- Audio-reactive wiring: smoothed envelopes, clamped gains, idle breathing
  state → `viz-motion-craft.md` §2. Never drive opacity/scale off raw FFT.
- Tunable params get live sliders first, baked defaults after
  (`viz-motion-craft.md` §5 — user's documented workflow preference).
- Ambient/looping motion needs a `prefers-reduced-motion` counterpart and a
  strobe sanity check (`motion-game-ux.md` §9, `viz-motion-craft.md`
  photosensitivity rules).
- WebGPU scenes degrade to a message in non-WebGPU browsers; resolution scale
  is the perf lever (`viz-motion-craft.md` §4).

---

## 2. Deck generation workflow

### Step 1 — Understand the request
Identify: topic · audience (executive, technical, general, investors) · tone ·
required slides/sections · theme preference (default `dark` / Blue Hour).

### Step 2 — Plan the structure
Narrative arc: **opening** (title, names the thing) → **problem/context** →
**body** (3–6 slides: two-column for comparisons, stats for numbers, quote for
social proof, media/gallery for visuals) → **closing** (CTA or memorable
finish). Rule: **6–12 slides**.

### Step 3 — Write content
Apple Style Guide rules — full set in `studio-design-system.md` §16. Core:
sentence case, ≤8-word headings, one-idea bullets, active voice, numbers 0–9
spelled out, serial comma, no filler ("leverage", "utilize", "synergy"),
specific over vague ("40% faster"), no unprovable superlatives.

### Step 4 — Build the JSON spec

```json
{
  "title": "Presentation Title",
  "theme": "dark",
  "slides": [
    { "type": "title", "eyebrow": "Optional label", "heading": "Main headline",
      "subheading": "Optional subtitle or speaker", "icon": "🚀" },
    { "type": "content", "eyebrow": "Section label", "heading": "Slide headline",
      "bullets": ["First point", "Second point", "Third point"],
      "note": "Optional footnote or source" },
    { "type": "stats", "eyebrow": "The numbers", "heading": "Optional headline",
      "stats": [
        { "label": "Annual revenue", "value": "$4.2M", "sublabel": "Up 38% YoY" },
        { "label": "Retention", "value": "94%", "sublabel": "Best-in-class", "featured": true }
      ] },
    { "type": "quote", "eyebrow": "Context label", "icon": "💬",
      "quote": "The actual quote text.", "attribution": "Person, Title",
      "credit": "Optional secondary credit" },
    { "type": "two-column", "eyebrow": "Comparison label", "heading": "Headline",
      "left":  { "title": "Left heading",  "items": ["One", "Two", "Three"] },
      "right": { "title": "Right heading", "items": ["One", "Two", "Three"] } },
    { "type": "gallery", "eyebrow": "Optional", "heading": "Optional",
      "srcs": ["https://example.com/photo1.jpg", "/local/path/image.webp"],
      "caption": "Optional caption" },
    { "type": "media", "heading": "Optional",
      "src": "YouTube / image / video URL", "caption": "Optional",
      "media_type": "auto" },
    { "type": "closing", "heading": "Strong final statement",
      "cta": "Call to action", "contact": "email@example.com or @handle" }
  ]
}
```

Field notes:
- **stats**: `value` drives animated count-up (`$`, `%`, `+`, commas OK);
  `featured: true` (or `span: 2`) = full-width card for the most important
  number; card widths lock before count-up (no reflow).
- **media**: `media_type` `"auto"` detects YouTube (watch/youtu.be → embed),
  `.mp4/.webm/.ogg` video, image extensions. Local paths → base64 data URIs.
- **gallery**: Ken Burns slideshow, 3.8 s GSAP crossfades, dot indicators,
  local files → base64.

### Step 5 — Run the build script

```bash
python3 ~/Documents/Development/sj-design/scripts/build_presentation.py /tmp/spec.json
# or stdin:  echo '<json>' | python3 .../build_presentation.py
# output path:  ... spec.json -o ~/Desktop/my-deck.html
```

Prints `✓ Generated: <path>` on success.
(UNVERIFIED carry-over: the script's own validation/escaping rules have not
been re-read — if a spec fails, read the script, don't guess fields.)

### Step 6 — VERIFY before reporting (new — mandatory)
Per `review-verification-playbook.md` §1: open the generated file in **real
Chrome via chrome-devtools MCP** (`new_page` → `file:///…`), then check
console for errors, take a screenshot of slide 1, and advance one slide to
confirm navigation + animations fire. The old skill said "open and tell the
user" — the expert *verifies, then shows proof*. A deck no one rendered is
not done.

### Step 7 — Report
Output path · navigation (arrows / click right half forward, left half back,
`f` fullscreen) · screenshot proof · offer theme/content changes.

---

## 3. Themes (17)

| Theme | Value | Atmosphere | Best for |
|---|---|---|---|
| Blue Hour | `"dark"` | Starfield · bokeh · Perlin gobos · SF fog | Pitch decks, evening keynotes, default |
| Crissy Field | `"light"` | Warm bokeh · blue gradient · gobos | Investor decks, bright rooms |
| Obsidian | `"obsidian"` | Dust particles · green gobos | Tech, dev tools, terminal aesthetic |
| Deep Space | `"deep-space"` | 200-star field · cyan/violet nebula | Sci-fi, data viz, aerospace |
| Noir | `"noir"` | Grain · venetian bars · rain · crimson bloom | Editorial, fashion, cinema |
| Golden Hour | `"golden-hour"` | Amber bokeh · amber-cream gradient | Hospitality, food, warm brands |
| Twin Peaks | `"twin-peaks"` | City glow · teal fog · night gobos | Nightlife, urban, moody Bay Area |
| Embarcadero | `"embarcadero"` | Steel-blue fog · grey-blue bokeh | Corporate, finance, maritime |
| Muir Woods | `"muir-woods"` | Fireflies · forest green gobos | Nature, wellness, sustainability |
| The Mission | `"the-mission"` | Orange/pink gradients · saturated gobos | Art, culture, creative agencies |
| Santa Cruz | `"santa-cruz"` | Aqua/seafoam bokeh · ocean gobos | Surf, beach, Pacific coast |
| Sausalito | `"sausalito"` | Teal/silver bokeh · harbour mist | Architecture, coastal real estate |
| Half Moon Bay | `"half-moon-bay"` | Coastal fog · storm grey gobos | Wine, coastal tourism, moody editorial |
| Redwood | `"redwood"` | Amber fireflies · burgundy gobos | Luxury, heritage brands |
| The Richmond | `"the-richmond"` | SF fog · lavender/grey gobos | Residential, neighbourhood stories |
| Nob Hill | `"nob-hill"` | Champagne bokeh · gold/ivory gobos | Luxury real estate, galas |
| Haight | `"haight"` | Floating emoji · mandala · confetti · nav explosions | Parties, joyful decks |

Selection guidance: dark themes for dramatic impact; light/mid for bright
rooms; forest/coastal for nature & community; Haight when the deck is the
party. Consultant-mode cross-ref: `studio-design-system.md` §2 (per-theme
token values + the THEME_GOBOS/THEME_BOKEH JS pairing gotcha when adding a
new theme). Haight's confetti/explosions: run the photosensitivity sanity
check before shipping to a general audience.

---

## 4. Slide types & animation

| Type | Best for | Key fields |
|---|---|---|
| `title` | Opening, section breaks | `heading`, `subheading`, `eyebrow`, `icon` |
| `content` | Facts, lists, features | `heading`, `bullets`, `note` |
| `stats` | Metrics, financials | `stats[]`: `label`, `value`, `sublabel`, `featured` |
| `quote` | Social proof, emphasis | `quote`, `attribution`, `icon`, `credit` |
| `two-column` | Comparisons, before/after | `left`, `right` (each `title` + `items`) |
| `gallery` | Photo showcases | `srcs[]`, `caption` |
| `media` | Demos, YouTube, screenshots | `src`, `caption`, `media_type` |
| `closing` | CTA, thank you | `heading`, `cta`, `contact` |

Per-slide-type GSAP entrance choreography is automatic — table in root
`references/slide-animations.md`. House easing: `cubic-bezier(0.16, 1, 0.3, 1)`
(expo out); springs `back.out(1.5)` (`studio-design-system.md` §7).

Ambient layer (every deck): Perlin gobo blobs · starfield (hidden in light
theme) · bokeh discs · three-layer SF fog. Emoji-viz techniques can back hero/
loading/closing slides — root `references/emoji-visualizations.md`.

HUD (every deck): `⏮ ⏭` jump · `😅` emoji-rain toggle (closing slide) ·
`1 / 12` counter · `A− A A+ A++` text-size presets (localStorage) · bottom
progress bar.

Custom slides beyond the 8 types (e.g. photo-tiles scatter, family-card glass
portrait, mouse parallax): recipes in the vault project note patterns +
`studio-design-system.md` §3/§5 — build on the 13-token contract and the
5-layer glass recipe, never freelance new conventions.

---

## 5. Builder QA gate (run before declaring any artifact done)

1. Console clean in real Chrome (chrome-devtools MCP) — zero errors.
2. Self-contained: no network fetches except declared CDNs (GSAP); local
   media embedded base64 (`studio-design-system.md` §11).
3. Copy passes the Apple Style Guide spot-check (§16).
4. Image-FX techniques → visible akella credit present (§14).
5. Ambient/looping motion has `prefers-reduced-motion` handling; no
   unbounded strobe (`motion-game-ux.md` §9).
6. If viewed on phones: tap targets ≥44px, safe-area respected
   (`motion-game-ux.md` §2) — decks are click/keyboard-first, but HUD
   buttons count.
7. WebGPU content: degradation message verified in a non-WebGPU context, or
   explicitly noted as WebGPU-only.
8. Screenshot proof captured and shown to the user.

---

## 6. Example prompts (trigger surface)

Presentations: investor pitch ("stats on rental income, gallery, contact
closing, light theme") · product launch ("10 slides, B2B SaaS, YouTube demo,
beta quote") · QBR ("revenue stats, Q3 vs Q4 two-column, wins, strong close")
· lecture slides · real-estate overview.

Motion & graphics: landing hero ("heart-pulse formation behind headline") ·
loading state ("Concentric Waves in a 200×200 box, slowed") · celebration
("emoji fireworks star burst once on load, then idle") · empty state ("Wire
Terrain dim behind 'No results yet'") · kiosk attract loop ("Tunnel Vortex
fullscreen, muted").
