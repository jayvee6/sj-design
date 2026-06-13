# First-party ingest — dispatch manifest (2026-06-12, Mac)

Run: sj-design-expert bootstrap ingest. Orchestrator = main session (Arbiter).
Fan-out cap: 5. Agents: general-purpose, sonnet, READ-ONLY except their one owned output file.
Output dir: `skills/sj-design-expert/references/` (draft-*.md, finalized by Arbiter).

| Task | Slice | Sources | Owned output | Status |
|---|---|---|---|---|
| T1 | Web design system & deployment | ~/Documents/Development/studiojoe, sj-design root (assets/template.html, lib/, showcase/), vault Projects/studiojoe*.md | draft-studio-design-system.md | dispatched |
| T2 | Game & touch UX presentation | ~/Documents/Development/emoji-arcade, emoji-slopes, star-speller | draft-motion-game-ux.md | dispatched |
| T3 | Viz & motion craft | ~/Documents/Development/musicplayer-viz, three-particle-lab, tree-shatter-sandbox, ripple-zen-garden; ~/Developer/ripple | draft-viz-motion-craft.md | dispatched |
| T4 | Native Apple design | ~/Documents/Development/StudioJoeMusic, StudioJoeSavers, TranscriptStudio, LinguaFranca; ~/Developer/ripple-apple | draft-apple-native-design.md | dispatched |
| T5 | Review & verification toolkit | joeOS vault AI/ wiki pages, project docs/evals across the above repos, sj-design/CLAUDE.md (sj-automation) | draft-review-verification-playbook.md | dispatched |

Report schema (required sections): Sources actually read · Distilled patterns (gotcha-first) ·
Reviewer checklist candidates · Decision-tree rows · UNVERIFIED.
A draft missing a section = PRECONDITION_FAILED → re-run that slice.
