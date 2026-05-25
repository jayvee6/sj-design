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

---

## sj-automation — PC test runner

An always-on Windows PC (Tailscale: `100.117.64.111`) runs a job server with
real Chrome (headless:false, WebGPU/D3D12). MCP tools are registered in Claude Desktop.

**Use these instead of asking the user to check manually:**

| Tool | When to use |
|---|---|
| `sja_health` | First tool call of any session — confirm PC is reachable |
| `sja_screenshot` | Visual review of any local or deployed URL |
| `sja_run_test` | Any page with `window.__RESULTS__`, `__SJTEST__`, or `__GITEST__` |
| `sja_gi_test` | Pages using graphics-inspector test harness |
| `sja_perf_sweep` | Quick fps check — reads `window.__GI_HUD__` after dwell |
| `sja_perfetto_trace` | Reliable fps — Chrome compositor timestamps, no rAF clamping |
| `sja_nsight_trace` | GPU-side fps via D3D12 Present() — NVIDIA hardware clock |
| `sja_pix_capture` | D3D12 frame debug — WebGPU pass breakdown, CPU vs GPU Δ |
| `sja_shell` | Run bash on the PC: git, builds, server control, file ops |
| `sja_metal_trace` | Metal System Trace on the Mac — MTLCommandBuffer GPU clock, utilization %, memory BW |
| `sja_jobs` | Check status of recent jobs |

Always call `sja_health` before the first job. If it fails, the PC is asleep or
the job server needs `pm2 restart sj-job-server` (via `sja_shell`).
