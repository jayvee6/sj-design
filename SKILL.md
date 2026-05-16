---
name: presentation
description: >
  A motion, graphics, and emoji-visualization toolkit for the web. Use for motion
  primitives — animated hero backgrounds, loading states, celebration moments,
  atmospheric FX, emoji visualizations, dancing emoji formations, WebGPU 3D scenes —
  AND for generating complete Apple-style slide decks built on the same primitives.
  Trigger on "make me a presentation / slide deck / pitch deck", "turn this into a
  slideshow", "build a hero background", "loading animation", "emoji visualization",
  "celebration effect", or any request to present information as slides. Output is
  self-contained HTML — cinematic GSAP / Canvas / WebGPU, no dependencies.
---

# sj-design

A motion, graphics, and emoji-visualization toolkit for the web. Ships primitives for hero backgrounds, loading states, celebration moments, atmospheric FX, emoji visualizations, and WebGPU 3D scenes — plus a complete slide-deck generator built on top of the same primitives. Everything is a self-contained `.html` file: no dependencies to install.

---

## Motion primitives

Standalone, copy-pasteable demos in `showcase/`. Each runs zero-dependency on a synthetic time pulse and has a one-line hook to wire back to audio.

**Emoji visualizations** — see [`references/emoji-visualizations.md`](references/emoji-visualizations.md)
- `showcase/emoji-waves.html` — concentric delayed-bass rings
- `showcase/emoji-vortex.html` — golden-angle phyllotaxis tunnel
- `showcase/emoji-fireworks.html` — themed parabolic bursts (peony / ring / star / heart / smiley)

**Dancing formations** — `showcase/emoji-formations/`
- `triangle-orbit` · `hex-swarm` · `heart-pulse` · `infinity-loop` · `star-formation` · `shape-morph`

**WebGPU scenes** — `showcase/scenes/` (raw WebGPU; needs a WebGPU browser, degrades to a message otherwise)
- `wire-terrain` (raymarched FBM terrain) · `disco-chrome` (ray-sphere mirror ball) · `neon-oscilloscope` (four ribbon waves)
- Each is one self-contained full-screen-triangle fragment shader (inline WGSL), single render pass, no postprocessing. Pattern + perf knobs in `lib/webgpu-bootstrap.js` (`SJGpu`; `{ maxDPR, renderScale }` — resolution is the dominant lever for these fragment-bound scenes).
- Reference: **WebGPU Fundamentals** — source/examples repo <https://github.com/webgpu/webgpufundamentals>, rendered site <https://webgpufundamentals.org/>. The canonical WebGPU/WGSL learning resource; use it for host-API setup, WGSL syntax, points/particles, and `wgpu-matrix` (view/projection — the scenes currently hand-roll camera math in the shader).

**Atmospheric FX** — `showcase/atmosphere.html` (combined, interactive) plus split single-effect files `atmosphere-{gobo,starfield,bokeh,fog,grain}.html`

**Shared lib** — `lib/`: `canvas-size.js` (SJCanvas, DPR sizing) · `synthetic-pulse.js` (SJPulse) · `envelopes.js` (VizEnv attack/release) · `webgpu-bootstrap.js` (SJGpu). Demos load these with an inline fallback so each file stays single-file portable.

---

## Building presentations

A complete Apple-style slide-deck generator, built on the primitives above — one use case of the toolkit. The workflow below produces a self-contained HTML deck with cinematic GSAP animations, navigable by keyboard or click.

### Step 1 — Understand the request
Read the user's prompt carefully. Identify:
- Topic / subject matter
- Audience (executive, technical, general, investors)
- Tone (professional, educational, inspirational, persuasive)
- Any specific slides, sections, or content to include
- Preferred theme: `dark` (default — Blue Hour) or `light` (Crissy Field)

### Step 2 — Plan the structure
Design a narrative arc. A good deck has:
- **Opening**: title slide that names the thing and creates interest
- **Problem / context**: why this matters
- **Body**: 3–6 slides covering the core content (use two-column for comparisons, stats for numbers, quote for social proof, media/gallery for visuals)
- **Closing**: clear call to action or memorable finish

Rule: **6–12 slides** is optimal. Fewer feels thin; more loses the audience.

### Step 3 — Write content (Apple Style Guide)
Follow these rules when writing every word:

**Headings**
- Sentence case only — "The future of work", not "The Future of Work"
- Max 8 words. Cut ruthlessly.

**Body text**
- Bullets, not paragraphs — each bullet is one idea, one line
- Active voice — "We built X", not "X was built"
- Plain language — no jargon without definition
- Numbers 0–9 spelled out ("three reasons"), 10+ as numerals
- Serial comma — "speed, quality, and cost"
- No filler — cut "leverage", "utilize", "synergy", "solution"

**Tone**
- Direct and confident
- Specific over vague — "40% faster" not "much faster"
- No superlatives without evidence — "world-class" only if provable

### Step 4 — Build the JSON spec

Construct a JSON object matching this schema:

```json
{
  "title": "Presentation Title",
  "theme": "dark",
  "slides": [
    {
      "type": "title",
      "eyebrow": "Optional label above headline",
      "heading": "Main headline",
      "subheading": "Optional subtitle or speaker name",
      "icon": "🚀"
    },
    {
      "type": "content",
      "eyebrow": "Section label",
      "heading": "Slide headline",
      "bullets": [
        "First key point",
        "Second key point",
        "Third key point"
      ],
      "note": "Optional footnote or source"
    },
    {
      "type": "stats",
      "eyebrow": "The numbers",
      "heading": "Optional headline above the grid",
      "stats": [
        { "label": "Annual revenue", "value": "$4.2M", "sublabel": "Up 38% YoY" },
        { "label": "Customers", "value": "1,200" },
        { "label": "NPS score", "value": "72", "sublabel": "Industry avg: 31" },
        { "label": "Retention", "value": "94%", "sublabel": "Best-in-class", "featured": true }
      ]
    },
    {
      "type": "quote",
      "eyebrow": "Context label (e.g. 'Industry consensus')",
      "icon": "💬",
      "quote": "The actual quote text goes here.",
      "attribution": "Person Name, Title",
      "credit": "Optional secondary credit line"
    },
    {
      "type": "two-column",
      "eyebrow": "Comparison label",
      "heading": "Slide headline",
      "left": {
        "title": "Left column heading",
        "items": ["Point one", "Point two", "Point three"]
      },
      "right": {
        "title": "Right column heading",
        "items": ["Point one", "Point two", "Point three"]
      }
    },
    {
      "type": "gallery",
      "eyebrow": "Optional label",
      "heading": "Optional heading",
      "srcs": [
        "https://example.com/photo1.jpg",
        "https://example.com/photo2.jpg",
        "/local/path/to/image.webp"
      ],
      "caption": "Optional caption beneath gallery"
    },
    {
      "type": "media",
      "heading": "Optional slide heading",
      "src": "https://youtube.com/watch?v=... or image URL or video URL",
      "caption": "Optional caption beneath media",
      "media_type": "auto"
    },
    {
      "type": "closing",
      "heading": "Thank you — or strong final statement",
      "cta": "Call to action text",
      "contact": "email@example.com or @handle"
    }
  ]
}
```

**Stats slide notes:**
- `value` drives the animated count-up — supports `$`, `%`, `+`, commas (e.g. `"$1,662,761"`, `"94%"`, `"+38%"`)
- `featured: true` (or `span: 2`) makes a card span the full width — use for the most important number
- `sublabel` adds a small context line beneath the value
- Cards animate in with spring easing; values count up from zero
- Card widths are locked before count-up starts to prevent layout reflow

**Media slide notes:**
- `media_type` can be `"auto"` (detected from URL), `"youtube"`, `"video"`, or `"image"`
- YouTube URLs (youtube.com/watch or youtu.be) are auto-converted to embeds
- Video files: `.mp4`, `.webm`, `.ogg`
- Images: any URL ending in `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, or `.svg`
- Local file paths are auto-embedded as base64 data URIs (self-contained)

**Gallery slide notes:**
- Displays a Ken Burns photo slideshow — photos pan and zoom continuously
- Each image crossfades every 3.8 seconds via GSAP
- Local file paths are auto-embedded as base64
- Dot indicators show which photo is active

### Step 5 — Run the build script

Save the JSON to a temp file and run:

```bash
python3 /path/to/skills/presentation/scripts/build_presentation.py /tmp/spec.json
```

Or pipe via stdin:

```bash
echo '<json>' | python3 /path/to/skills/presentation/scripts/build_presentation.py
```

To specify output path:
```bash
python3 build_presentation.py spec.json -o ~/Desktop/my-deck.html
```

The script prints the output path on success: `✓ Generated: /tmp/my-deck.html`

### Step 6 — Open and report

Open the file:
```bash
open /tmp/my-deck.html
```

Tell the user:
- Where the file is saved
- How to navigate: arrow keys / click right half to advance, left half to go back, `f` for fullscreen
- Offer to change theme, add slides, or adjust content

---

## Themes

| Theme | Value | Atmosphere | Best for |
|-------|-------|------------|----------|
| Blue Hour | `"dark"` | Starfield · bokeh · Perlin gobo blobs · SF fog | Pitch decks, evening keynotes, most dark content |
| Crissy Field | `"light"` | Warm bokeh · blue gradient · Perlin gobo blobs | Investor decks, daytime presentations |
| Obsidian | `"obsidian"` | Floating dust particles · green-tinted gobo blobs | Tech, finance, developer tools, terminal aesthetic |
| Deep Space | `"deep-space"` | Dense 200-star field · cyan/violet/pink nebula gobos | Sci-fi, data viz, space/aerospace, futurism |
| Noir | `"noir"` | Film grain · venetian blind bars · rain streaks · crimson bloom | Editorial, fashion, cinema, Sin City storytelling |
| Golden Hour | `"golden-hour"` | Warm amber bokeh · amber-to-cream gradient | Hospitality, lifestyle, food, warm brand storytelling |
| Twin Peaks | `"twin-peaks"` | City glow at bottom · teal fog · night purple/teal gobos | Night life, urban, moody Bay Area content |
| Embarcadero | `"embarcadero"` | Steel-blue fog · grey-blue bokeh · cool gobos | Corporate, finance, waterfront, maritime |
| Muir Woods | `"muir-woods"` | Blinking fireflies · deep forest green gobos | Nature, wellness, sustainability, outdoors |
| The Mission | `"the-mission"` | Warm orange/pink gradients · vivid saturated gobos | Art, culture, food, creative agencies, Latin brand |
| Santa Cruz | `"santa-cruz"` | Aqua/seafoam bokeh · ocean blue gobos | Surf, beach, outdoor rec, Pacific coast brands |
| Sausalito | `"sausalito"` | Soft teal/silver bokeh · harbour mist gobos | Architecture, lifestyle, coastal real estate |
| Half Moon Bay | `"half-moon-bay"` | Coastal fog · storm grey/slate gobos | Agriculture, wine, coastal tourism, moody editorial |
| Redwood | `"redwood"` | Amber blinking fireflies · deep burgundy/forest gobos | Luxury, heritage brands, California wilderness |
| The Richmond | `"the-richmond"` | SF fog · cool lavender/grey gobos | Residential, food, culture, neighbourhood storytelling |
| Nob Hill | `"nob-hill"` | Champagne bokeh · gold/ivory gobos · light mist | Luxury real estate, finance, fundraising galas |
| Haight | `"haight"` | Floating emoji · spinning mandala · confetti drops · explosion on nav | Parties, creative decks, anything that should feel joyful |

**Choosing a theme:** dark themes (Blue Hour, Obsidian, Deep Space, Noir, Twin Peaks, The Mission, Redwood) are best for dramatic impact. Light/mid themes (Crissy Field, Golden Hour, Embarcadero, Sausalito, Nob Hill) read better in bright rooms. Forest and coastal themes (Muir Woods, Santa Cruz, Half Moon Bay, The Richmond) suit nature and community content. Haight is for when the presentation itself is the party. Each theme has its own ambient atmosphere — no configuration needed.

---

## Slide type reference

| Type | Best for | Key fields |
|------|----------|------------|
| `title` | Opening, section breaks | `heading`, `subheading`, `eyebrow`, `icon` |
| `content` | Facts, lists, features | `heading`, `bullets`, `note` |
| `stats` | Key metrics, financials | `stats[]` with `label`, `value`, `sublabel`, `featured` |
| `quote` | Social proof, emphasis | `quote`, `attribution`, `icon`, `credit` |
| `two-column` | Comparisons, before/after | `left`, `right` (each with `title` + `items`) |
| `gallery` | Photo showcases, properties | `srcs[]`, `caption` |
| `media` | Demos, YouTube, screenshots | `src`, `caption`, `media_type` |
| `closing` | CTA, thank you | `heading`, `cta`, `contact` |

---

## Animation reference (GSAP)

Per-slide-type entrance choreography is applied automatically — the full table is in [`references/slide-animations.md`](references/slide-animations.md). All animations use Apple's `cubic-bezier(0.16, 1, 0.3, 1)` easing (expo out); spring effects use `back.out(1.5)`.

---

## Ambient atmosphere

Every presentation includes layered ambient effects that run throughout:

- **Perlin gobo blobs** — Slow-drifting radial color blobs driven by 2D Perlin noise; unique path every load
- **Starfield** — 95 twinkling white stars (hidden in Crissy Field light theme)
- **Bokeh discs** — Blurred glowing circles that drift and breathe
- **SF fog** — Three-depth-layer fog clouds (☁️ emoji, blurred) that drift right-to-left like the real marine layer; Perlin noise drives vertical curl

**Emoji visualization techniques** (for hero slides, loading screens, closing moments, or any slide wanting a full-motion canvas): see [`references/emoji-visualizations.md`](references/emoji-visualizations.md) for three self-contained canvas-2D techniques — **Concentric Waves**, **Tunnel Vortex** (phyllotaxis), and **Fireworks** (themed parabolic-arc bursts in peony / ring / star / heart / smiley shapes). Each has a runnable demo in `showcase/` and a one-line hook to wire back to audio if you have it.

---

## HUD controls

Every deck includes a persistent heads-up display:

| Control | Function |
|---------|----------|
| `⏮ ⏭` buttons | Jump to first / last slide |
| `😅` button | Toggle emoji rain on the closing slide |
| `1 / 12` counter | Current slide position |
| `A− A A+ A++` | Text size presets (sm / md / lg / xl) — persisted in localStorage |
| Progress bar | Thin accent-colored bar along the bottom edge |

---

## Example prompts

### Presentations

**Investor pitch:**
> "Build a pitch deck for my SF duplex investment — include stats on rental income, a gallery of property photos, and a closing slide with my contact info. Use the light theme."

**Product launch:**
> "Create a 10-slide product launch deck for our new AI writing tool. Audience is B2B SaaS buyers. Include a demo slide with a YouTube link and a quote from a beta user."

**Team presentation:**
> "Make a quarterly business review deck — revenue stats, two-column comparison of Q3 vs Q4, key wins as bullets, and a strong closing."

**Educational:**
> "I need lecture slides on the water cycle for a high school class — eight slides, clear diagrams described as image placeholders, simple language, dark theme."

**Real estate:**
> "Build a property overview deck for 740-742 37th Ave. Stats: $5,340 current monthly income, $10,400 market rent potential, $1,662,761 projected 2031 value. Gallery of exterior photos."

### Motion & graphics

**Landing hero:**
> "Give me a landing-page hero background — the dancing emoji heart-pulse, subtle, behind centered headline text."

**Loading state:**
> "I need a small loading animation in a 200×200 box using the Concentric Waves emoji viz, slowed down."

**Celebration moment:**
> "Make a signup-success screen that fires the emoji fireworks (star-shape burst) once on load, then idles."

**Empty state:**
> "Build an empty-state illustration with the Wire Terrain WebGPU scene running dim behind a 'No results yet' message."

**Ambient backdrop:**
> "Drop the Tunnel Vortex in as a full-screen background for a kiosk attract loop — muted, no audio."