# Presentation Skill for Claude Code

A Claude Code skill that generates beautiful, animated HTML slide decks from natural language prompts.

**[→ View demo & docs](https://jayvee6.github.io/presentation-skill)**

---

## What it does

Ask Claude to make a presentation and get a self-contained `.html` file with:

- Cinematic GSAP animations (Apple's expo-out easing)
- Apple design system — SF Pro, exact color tokens, Liquid Glass fills
- Six slide layouts: title, content, quote, two-column, media, closing
- YouTube / video / image embeds on media slides
- Keyboard + click + swipe navigation
- Dark and light themes
- Fully responsive at any viewport size

## Example prompts

```
Make me a 6-slide presentation about the history of the internet
Create a pitch deck for a SaaS startup selling AI writing tools
Turn this outline into slides: [paste your bullets]
Build a product demo deck and embed this YouTube video on slide 3: [URL]
I need a deck comparing React vs Vue vs Svelte
```

## Installation

1. Clone this repo
2. Copy the `presentation/` folder into your Claude Code skills directory:
   ```
   ~/Library/Application Support/Claude/.../skills/presentation/
   ```
3. Ask Claude: *"make me a presentation about X"* — the skill triggers automatically.

## File structure

```
presentation-skill/
├── SKILL.md              # Skill instructions + JSON spec reference
├── scripts/
│   └── build_presentation.py   # Builds HTML from JSON spec
├── assets/
│   └── template.html           # GSAP template with Apple design tokens
├── evals/
│   └── evals.json              # Eval test cases
└── index.html            # This landing page (GitHub Pages)
```

## Slide spec format

```json
{
  "title": "My Deck",
  "theme": "dark",
  "slides": [
    { "type": "title",      "heading": "...", "subheading": "..." },
    { "type": "content",    "heading": "...", "bullets": ["..."] },
    { "type": "quote",      "quote": "...", "attribution": "..." },
    { "type": "two-column", "heading": "...", "left": {...}, "right": {...} },
    { "type": "media",      "src": "https://youtube.com/watch?v=...", "caption": "..." },
    { "type": "closing",    "heading": "...", "cta": "...", "contact": "..." }
  ]
}
```

## Build manually

```bash
python3 scripts/build_presentation.py spec.json -o deck.html
open deck.html
```

## Navigation

| Input | Action |
|-------|--------|
| `→` / `Space` / click right | Next slide |
| `←` / click left | Previous slide |
| `F` | Fullscreen |
| Swipe left/right | Next / previous (mobile) |

---

Built with [Claude Code](https://claude.ai/code) · Animations by [GSAP](https://gsap.com) · Apple design tokens
