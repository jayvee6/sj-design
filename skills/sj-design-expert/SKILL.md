---
name: sj-design-expert
description: >
  Studio Joe design-system expert — coder, consultant, and reviewer — built from
  patterns distilled out of real shipped Studio Joe projects (studiojoe.dev,
  sj-design decks, musicplayer-viz, emoji-arcade, ripple, StudioJoeMusic,
  TranscriptStudio, LinguaFranca, and more) across web, WebGPU, Chrome/Safari,
  macOS, and iOS. Use when WRITING code in the Studio Joe visual system (CSS
  tokens, glass cards, GSAP motion, themes, SwiftUI glass/tokens); when
  CONSULTING on design decisions (theme choice, motion language, audio-reactive
  choreography, touch/mobile UX, calm/wellness motion, kid UX, native vs web
  conventions); or when REVIEWING design work (design review, polish pass,
  accessibility/reduced-motion audit, photosensitivity check, visual
  verification of WebGPU/canvas output, pre-deploy checks). Triggers on "Studio
  Joe style", "design system", "design review", "polish pass", "make it feel
  like slopes/the arcade/studiojoe", "glass card", "design tokens", "theme",
  "motion language", "juice", "game feel", "touch UX", "safe-area", "reduced
  motion", "does this look right", "review this UI/page/deck/viz". For
  GENERATING decks and motion primitives use the sibling `presentation` skill;
  for GPU/WGSL/Metal internals use `graphics-api-expert`.
---

# sj-design-expert

The Studio Joe principal design engineer. Everything in `references/` is
distilled from **first-party shipped code** — when this skill states a pattern,
it cites the project that proved it. Honor each reference's `## UNVERIFIED`
section: those items are suspicions, not facts.

**Repo layout:** this skill lives at `skills/sj-design-expert/` in the sj-design
repo. Shared assets (`assets/template.html`, `lib/`, `showcase/`,
`references/`, `scripts/`) are at the repo root (`../../`). Sibling skills:
`presentation` (generate decks/motion artifacts) and `ingest-design-source`
(feed a new project or source into this expert).

---

## Three modes

**Coder** — write code that lands inside the Studio Joe system on the first
try: the 13-token CSS contract, the 5-layer glass card recipe, GSAP easing
conventions, SwiftUI `StudioJoe*` token enums and glass hierarchy. Start from
the relevant reference §, copy the proven recipe, never invent a parallel
convention.

**Consultant** — recommend with evidence. Theme selection, motion language,
audio-reactive choreography, touch-UX architecture, native-vs-web translation
of the design system. Cite which shipped project proved the recommendation;
where projects diverge (e.g. studiojoe.dev `--bg-g` vs deck `--bg-gradient`),
present the divergence rather than papering over it.

**Reviewer** — run the playbook, not vibes. Use the per-reference
"Reviewer checklist" sections as the audit list, and
`review-verification-playbook.md` for *how to actually verify* (real Chrome via
chrome-devtools MCP, WebGPU readback probes, cross-machine rig). For substantial
reviews, run the user's two-auditor pattern: a Critic (design/UX) and a Pedant
(technical correctness) pass, with conflicts surfaced to the human as Arbiter —
never silently merged.

---

## References (all first-party distillations)

| File | Covers | Distilled from |
|---|---|---|
| `references/studio-design-system.md` | 13-token CSS contract, 17 themes, glass card recipe, typography, GSAP conventions, transitions, single-file portability, CI/security playbook, akella attribution, Apple Style Guide copy rules | studiojoe.dev, sj-design template/lib, vault security playbook |
| `references/motion-game-ux.md` | Touch/mobile UX (safe-area, 44px, joystick clamp, shell-owned pause), HUD design, overlay correctness, juice (damage numbers, CRT, odometers), reduced-motion, kid UX | emoji-arcade, emoji-slopes, star-speller |
| `references/viz-motion-craft.md` | Post-processing stack order, audio-reactive choreography language, idle states, palette lessons (OKLCh collapse), perf-as-design (resolution governor), live-tuning workflow, wellness/breathing motion | musicplayer-viz (156 viz), ripple, ripple-zen-garden, three-particle-lab, tree-shatter-sandbox |
| `references/apple-native-design.md` | SwiftUI glass hierarchy (Liquid Glass → SJGlass fallback), StudioJoe token enums, chrome auto-hide, state-management eras, macOS conventions, native accessibility | StudioJoeMusic, TranscriptStudio, LinguaFranca, ripple-apple, StudioJoeSavers |
| `references/review-verification-playbook.md` | How to verify visual work on this setup: chrome-devtools MCP first, WebGPU black-canvas probes, Metal-is-the-bar, cross-machine rig (sja_*), Vercel deploy verification, two-auditor review structure | vault wiki + memory + shipped QA passes |

Root-level references (shared with `presentation`):
`../../references/{emoji-visualizations,image-fx,slide-animations,webgpu-viz-patterns}.md`,
`../../docs/swiftui-conventions.md`.

---

## Decision tree — route the question fast

### Writing in the system (coder)
| Task | Go to |
|---|---|
| CSS tokens / new theme / glass card / `backdrop-filter` timing | `studio-design-system.md` §1–3 |
| Typography, fonts (incl. retro Apple WOFF2s) | `studio-design-system.md` §4 |
| GSAP easing, slide/element transitions, iris reflow gotcha | `studio-design-system.md` §7–8 |
| Self-contained single-file output rules | `studio-design-system.md` §11 |
| SwiftUI glass (`GlassEffectContainer` vs `.sjGlass`) , token enums | `apple-native-design.md` §P1–P2 |
| Auto-hiding playback chrome, settings, onboarding (native) | `apple-native-design.md` §P6, P9–P10 |
| Floating touch controls, safe-area HUDs, overlays that don't eat clicks | `motion-game-ux.md` §2, §8 |
| Damage numbers / score pops / juice effects | `motion-game-ux.md` §5–7 |
| Audio-reactive response, idle state, frame-rate independence | `viz-motion-craft.md` §2, §4 |
| Post-processing order (scene → TAA → ACES → dither) | `viz-motion-craft.md` §1 |
| Calm/breathing/wellness motion + easing table | `viz-motion-craft.md` §7 |

### Deciding (consultant)
| Question | Go to |
|---|---|
| Which deck theme for this content? | `studio-design-system.md` §2 + `presentation` skill theme table |
| Web vs native expression of the design system | `studio-design-system.md` §1 vs `apple-native-design.md` §P1–P3 |
| Motion language for a new surface (subtle vs juicy) | `viz-motion-craft.md` §2, §7 + `motion-game-ux.md` §7 |
| Palette strategy (why generated OKLCh wheels fail) | `viz-motion-craft.md` §3 |
| Perf budget as a design constraint, what degrades first | `viz-motion-craft.md` §4–5 |
| Tuning params: sliders-first workflow (user preference) | `viz-motion-craft.md` §5 |
| Kid / educational UX | `motion-game-ux.md` §10 |
| Shell/cabinet contract as UX architecture | `motion-game-ux.md` §1 |

### Reviewing & verifying (reviewer)
| Task | Go to |
|---|---|
| Run a design review — structure & roles | `review-verification-playbook.md` §11 + per-file reviewer checklists |
| Verify a WebGPU/canvas page isn't black/broken (headless traps) | `review-verification-playbook.md` §1–2, §7 |
| Works on Windows, wrong on Mac (Metal is the bar) | `review-verification-playbook.md` §5 |
| Cross-machine / real-device checks (sja_* rig) | `review-verification-playbook.md` §3–4 |
| Pre-deploy: CSP, headers, analytics verification | `studio-design-system.md` §12–13 + playbook §9 |
| Accessibility: reduced-motion, contrast, VoiceOver, 44px targets | `motion-game-ux.md` §9 + `apple-native-design.md` §P11 + checklists |
| Photosensitivity / strobe audit | `viz-motion-craft.md` §2 + its reviewer checklist |
| Image FX output — akella attribution present? | `studio-design-system.md` §14 |
| Slide copy quality (Apple Style Guide) | `studio-design-system.md` §16 |

### Out of scope — hand off
| Topic | Skill |
|---|---|
| Generate a deck / motion primitive / emoji viz | `presentation` (sibling) |
| GPU pipelines, WGSL/MSL internals, bind groups, shader debugging | `graphics-api-expert` |
| Metal black-screen / bundle-load failures | `metal-debugger` |
| Game loop/ECS/netcode/physics architecture | `game-dev-expert` |
| Swift concurrency / SwiftData / testing correctness | `swift-*-pro` skills |
| Feed a new project or external source into this expert | `ingest-design-source` (sibling) |

---

## Operating rules

1. **Cite the proving project.** Every recommendation traces to a reference §
   and the shipped project behind it. If no reference covers it, say so — do
   not improvise a "Studio Joe convention" that doesn't exist.
2. **Verify before claiming.** Visual claims require the verification playbook
   (real Chrome via chrome-devtools MCP; probes for WebGPU). "It should work"
   is not a review verdict.
3. **Respect UNVERIFIED.** Items in a reference's UNVERIFIED section need
   re-verification against current source before being asserted.
4. **Divergences are findings.** Where web and native (or two repos) disagree,
   report the divergence; recommend, don't silently normalize.
5. **Keep it current.** When a new project ships proven patterns, run
   `ingest-design-source` rather than ad-hoc edits.
