---
name: ingest-design-source
description: >
  Productized pipeline to feed a new source into the sj-design-expert skill —
  a first-party Studio Joe project (a repo under ~/Documents/Development or
  ~/Developer), a shipped feature worth distilling, OR an external source
  (a designer's site/repo, a motion-design article series, a design-system
  docs site). Use whenever the user wants to "feed sj-design-expert",
  "ingest/absorb <project-or-url> into the design expert", "distill the design
  patterns from <project>", "add this design source to the skill", or ships a
  project whose design/UX/motion lessons should make the expert smarter. This
  is the repeatable form of the 5-agent first-party run that built
  sj-design-expert (2026-06-12); invoke it instead of improvising an ad-hoc
  research run.
---

# ingest-design-source

Turn one design/UX/motion source into durable sj-design-expert knowledge via a
defensive multi-agent pipeline. Productized from the 2026-06-12 first-party
bootstrap run (5 agents over studiojoe / emoji-arcade / musicplayer-viz /
native Apple apps / verification lore).

**Input (`<source>`):** a first-party repo path, a shipped feature ("the
survivors polish pass"), a GitHub user/repo, or a docs/article site. Multiple
related sources in one run are fine (treat as one corpus).

**Output:** a distilled `references/<topic>.md` inside
`skills/sj-design-expert/` (or material appended to an existing reference),
the SKILL.md decision tree wired to reach it, a local commit, and a daily-note
closeout. Nothing is pushed without explicit human approval.

**Canonical target — non-negotiable.** sj-design's authoritative copy is
`~/Documents/Development/sj-design` (git remote `github.com/jayvee6/sj-design`).
All edits land there; `~/.claude/skills/*` entries are symlinks into it.

**The lens — what belongs here.** Design systems, motion language, touch/
mobile UX, visual composition, accessibility, copy style, native Apple design
conventions, and how to *verify* visual work. GPU/WGSL/Metal internals belong
to `graphics-api-expert` (use `ingest-graphics-source`); game architecture
belongs to `game-dev-expert`. When a source spans both, split the findings —
one line of cross-reference here, full distillation in the sibling.

---

## Core contracts (baked in — do not skip)

From the user's `best_practices.md`:

- **Zero-Guessing.** Agents report only what they actually read/fetched; every
  proposed URL or file path is verified before it ships. A candidate named in
  a dispatch prompt is a hypothesis, not a fact. Every report carries a
  mandatory `## UNVERIFIED` section — and finalized references KEEP it as a
  trust boundary.
- **Dispatch manifest + fan-out ≤ 5.** Record every task in
  `.claude/ingest-manifest-<date>.md` (task | slice | sources | owned output |
  status) before dispatch. Each agent owns exactly ONE output file; agents are
  otherwise READ-ONLY (no other edits, no git).
- **Arbiter fan-in.** Reconcile manifest vs. completions; validate every
  report has the required sections (Sources read · Distilled patterns ·
  Reviewer checklist candidates · Suggested decision-tree rows · UNVERIFIED).
  Missing report = `HUNG` (re-dispatch once); malformed = `PRECONDITION_FAILED`
  (re-run, never coerce). The orchestrator is the Arbiter; raw agent output is
  an intermediate artifact, never the deliverable.
- **Human gate before push.** Commit locally with specific staged files (never
  `git add -A`); report the SHA and await explicit push approval; verify
  fast-forward; never force-push.

---

## Pipeline

### Phase 0 — Bootstrap & precondition
1. Confirm session bootstrap (best_practices.md + vault Index + daily note).
2. `git -C ~/Documents/Development/sj-design status -sb` — note the branch and
   any unpushed work; you are layering on top of it, not clobbering it.
3. Read current state so the run dedupes instead of duplicating:
   `ls skills/sj-design-expert/references/`, the SKILL.md decision tree, and
   the root `references/`. **Gate:** you can name what the expert already
   covers for this source's topic.

### Phase 1 — Scope & slice
1. Verify the source exists (repo path resolves / URL fetches). For repos,
   inventory top-level structure first; for sites, enumerate the real section
   list. No guessing.
2. Carve into **≤ 5 non-overlapping slices** with one owned output file each
   (`references/draft-<topic>.md`). Small sources may need only 1–2 agents.
   **Gate:** the dispatch manifest file exists before any dispatch.

### Phase 2 — Dispatch (parallel, read-only)
- All slices in one message, `general-purpose` agents on **sonnet**.
- Every prompt must include: the ONE owned output file; READ-ONLY otherwise;
  the design/UX lens with the GPU-internals exclusion; Zero-Guessing with
  required `## UNVERIFIED`; the five required sections; "cite source paths
  inline"; target 150–300 lines, gotcha-first, tables over prose.

### Phase 3 — Fan-in & Arbiter synthesis
1. Reconcile manifest vs. returns; validate section schema per report
   (grep for the five headers — cheap and sufficient).
2. Arbitrate conflicts with evidence (read the disputed file yourself).
   Recurring ruling: divergent conventions between two shipped repos are a
   *finding to record*, not a conflict to normalize.
3. Promote `draft-<topic>.md` → `<topic>.md`.

### Phase 4 — Wire in
- Add decision-tree rows + the reference-table line to
  `skills/sj-design-expert/SKILL.md` (use each report's "Suggested
  decision-tree rows" as the starting point; merge, don't append blindly).
- Cross-link sibling references where the source materially extends them.
  **Gate:** `git diff --stat` shows only intended files; no duplicated
  coverage.

### Phase 5 — Commit local · close out · push on OK
- Stage specific files; commit with the `Co-Authored-By: Claude` trailer.
- Report the SHA; **do not push** without approval; verify fast-forward.
- Daily note: tagged Session Log entry + `## Next Session` carrying any
  unpushed SHA. Update `Projects/sj-design.md` if structure changed.

---

## Failure handling

Classify with the best_practices.md taxonomy — `TRANSIENT` / `INPUT_INVALID` /
`PRECONDITION_FAILED` / `HUNG` / `LOGIC_DEADLOCK` / `FATAL` — and take the
mapped action. A source that doesn't resolve is `INPUT_INVALID`: surface it,
never substitute a guess.
