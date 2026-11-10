# Ingest manifest — 2026-11-10 — emilkowalski/skills

**Source:** https://github.com/emilkowalski/skills @ `715c1807e08c497cfd1dc4feb450a2a3300ef2a9` (2026-11-09), MIT, © Emil Kowalski.
Shallow clone (markdown only, no scripts): `/private/tmp/claude-501/-Users-jdot--claude-spares-spare-3fZhWG/b1c151c5-034d-4851-9418-b4df526cbd51/scratchpad/src/emil-skills`
**Target:** `skills/sj-design-expert/references/` (canonical repo `/Users/jdot/Development/sj-design`, branch main, clean at `3f8dc10`).
**Orchestrator / Arbiter:** main session (Opus). Workers: general-purpose on sonnet, read-only except one owned file each.

| Task | Slice | Sources (under `skills/` unless noted) | Owned output | Status |
|---|---|---|---|---|
| A | Design-engineering principles + library picks | `emil-design-eng/`, `animation-vocabulary/`, `pick-ui-library/`, `ask-sonner/`, root `ui-cheatsheet.md` | `references/draft-design-eng-principles.md` | dispatched |
| B | Web motion recipes + choreography | `animate/`, `choreograph/`, `gestures/`, `find-animation-opportunities/` | `references/draft-web-motion-recipes.md` | dispatched |
| C | Motion review, audit, perf, removal | `review-animations/`, `improve-animations/`, `remove-animations/`, `animation-performance/`, root `performance-cheatsheet.md` | `references/draft-motion-review-audit.md` | dispatched |
| D | Native / mobile design + motion | `apple-design/`, `mobile-native/`, `write-swift/`, `animate-expo/` | `references/draft-native-mobile-motion.md` | dispatched |
| E | UI stress-testing + prototyping | `break-ui/`, `prototype/` | `references/draft-break-ui-prototype.md` | dispatched |

Required report sections: Sources read · Distilled patterns · Reviewer checklist candidates · Suggested decision-tree rows · UNVERIFIED.

## Fan-in log
(filled by Arbiter)
- Reconciled 5/5 dispatched vs 5/5 returned; no HUNG, no PRECONDITION_FAILED. Every report has the five required H2s (E adds a Divergences H2; C adds §12).
- Line counts: A 330, B 280, C 305, D 281, E 297 (A and C slightly over 300 target; kept, not truncated).
- Arbiter checks against source: `touch-action: pan-x` for vertical drag is CORRECT (B's suspicion overturned); swipe velocity 0.11 confirmed px/ms (emil-design-eng L443, animate/RECIPES L266).
- Promoted draft-* → emil-*; added emil-kowalski-index.md (file map, MIT notice, divergence register R0 + rulings; rows 1, 7, 10, 11 OPEN for human).
- Wired SKILL.md: description triggers, intro, References split first-party/external, new decision-tree block, operating rule 1. All § anchors grep-verified.
