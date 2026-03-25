---
name: presentation
description: >
  Use this skill whenever the user wants to create a presentation, slideshow, slide deck, pitch deck,
  or lecture slides. Trigger on prompts like "make me a presentation about X", "create slides for Y",
  "I need a deck on Z", "turn this into a slideshow", "build a pitch for X", "make slides explaining Y",
  "present this as slides", or any request to visually present information as a series of slides.
  Even if the user just says "present this", use this skill. The output is a self-contained HTML file
  with cinematic GSAP animations navigable by keyboard or click, in Apple design style.
---

# Presentation Skill

Generate beautiful, animated HTML slide decks with Apple-style design and GSAP animations. Presentations are self-contained `.html` files — no dependencies to install.

---

## Workflow

### Step 1 — Understand the request
Read the user's prompt carefully. Identify:
- Topic / subject matter
- Audience (executive, technical, general)
- Tone (professional, educational, inspirational)
- Any specific slides, sections, or content to include
- Preferred theme: `dark` (default) or `light`

### Step 2 — Plan the structure
Design a narrative arc. A good deck has:
- **Opening**: title slide that names the thing and creates interest
- **Problem / context**: why this matters
- **Body**: 3–6 slides covering the core content (use two-column for comparisons, quote for social proof, media for demos)
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
      "subheading": "Optional subtitle or speaker name"
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
      "type": "quote",
      "eyebrow": "Context label (e.g. 'Industry consensus')",
      "heading": "Slide heading (used if no eyebrow)",
      "icon": "💬",
      "quote": "The actual quote text goes here.",
      "attribution": "Person Name, Title"
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

**Media slide notes:**
- `media_type` can be `"auto"` (detected from URL), `"youtube"`, `"video"`, or `"image"`
- YouTube URLs (youtube.com/watch or youtu.be) are auto-converted to embeds
- Video files: `.mp4`, `.webm`, `.ogg`
- Images: any URL ending in `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, or `.svg`

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

## Slide type reference

| Type | Best for | Key fields |
|------|----------|------------|
| `title` | Opening, section breaks | `heading`, `subheading`, `eyebrow` |
| `content` | Facts, lists, features | `heading`, `bullets`, `note` |
| `quote` | Social proof, emphasis | `quote`, `attribution`, `icon` |
| `two-column` | Comparisons, before/after | `left`, `right` (each with `title` + `items`) |
| `media` | Demos, YouTube, screenshots | `src`, `caption`, `media_type` |
| `closing` | CTA, thank you | `heading`, `cta`, `contact` |

## Animation reference (GSAP)

Animations are applied automatically by slide type — no configuration needed:

| Slide type | Animation |
|------------|-----------|
| `title` | Headline drops in from top, subtitle rises from below |
| `content` | Headline slides from left, bullets stagger in one by one |
| `quote` | Quote mark scales up as watermark, quote text fades in |
| `two-column` | Columns slide in from opposite sides |
| `media` | Frame scales up from 95%, caption fades in |
| `closing` | Headline scales up with spring easing, CTA fades in |

All animations use Apple's `cubic-bezier(0.16, 1, 0.3, 1)` easing curve (expo out).
