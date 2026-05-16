# Slide Animations (GSAP)

Per-slide-type entrance choreography for the presentation deck generator. Applied automatically by slide type — no configuration needed. (Extracted from `SKILL.md`; the deck builder reads this so the main skill doc stays motion-first.)

| Slide type | Animation |
|------------|-----------|
| `title` | Icon drops from top, eyebrow follows, headline rises, subheading fades |
| `content` | Eyebrow and headline slide from left, bullets stagger in one by one |
| `stats` | Eyebrow/headline animate in, cards spring up with scale, values count up from zero |
| `quote` | Quote-mark watermark scales in behind text, icon springs, quote fades up, attribution follows |
| `two-column` | Columns slide in from opposite sides, bullets stagger inside |
| `gallery` | Frame scales in, Ken Burns photo cycle begins (crossfade + pan/zoom) |
| `media` | Heading drops, frame scales up from 95%, caption fades |
| `closing` | Headline scales up with spring easing, CTA fades, emoji rain available |

**Easing.** All animations use Apple's `cubic-bezier(0.16, 1, 0.3, 1)` easing curve (expo out). Spring effects use `back.out(1.5)`.

**Ambient atmosphere.** Every deck also runs the layered ambient effects described in `SKILL.md` → *Ambient atmosphere* (Perlin gobo blobs, starfield, bokeh, SF fog), plus optional full-motion canvas backgrounds from the motion primitives — see [`emoji-visualizations.md`](emoji-visualizations.md).
