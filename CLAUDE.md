# sj-design — Claude instructions

This is the Studio Joe design system and presentation skill repo. It generates self-contained animated HTML slide decks from natural language prompts.

## What it is

A Claude Code skill (`SKILL.md`) that produces beautiful `.html` presentations using GSAP animations and the Apple design system (SF Pro, Glass Refraction, Apple color tokens).

## Key files

- `SKILL.md` — the skill definition (main deliverable)
- `index.html` — showcase/demo page
- `assets/template.html` — base HTML template for generated decks
- `showcase/` — example generated decks
- `demo/` — demo assets
- `evals/` — evaluation prompts and outputs
- `scripts/` — build or utility scripts

## Tech

- Vanilla HTML/CSS/JS — no framework, no build step
- GSAP 3 via CDN for animations
- Six slide layouts: title, content, quote, two-column, media, closing
- Dark/light themes, keyboard + swipe navigation, YouTube/video/image embeds

## Working on the skill

Edit `SKILL.md` directly. Test by running the skill in Claude Code against prompts in `evals/`.
