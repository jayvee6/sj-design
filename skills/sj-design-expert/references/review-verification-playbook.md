# Reviewer Verification Playbook

> Scope: how to actually verify visual and design work on this user's setup.
> Lens: cross-browser, cross-machine, native, deployed, and two-auditor review structure.
> All patterns grounded in cited source files — no guessing.

---

## Sources read

| File | Key contribution |
|---|---|
| `joeOS/AI/WebGPU Cross-Machine Testing.md` | LAN HTTPS playbook, machine roles, harness fps confound |
| `joeOS/AI/WebGPU Scene Architecture — Best Practices.md` | Metal vs D3D12 strictness delta, GPU debug checklist |
| `joeOS/AI/Multi-Agent Codebase Workflow.md` | Verify-twice rule, single-driver pattern, model tiers |
| `joeOS/AI/Multi-Instance Protocol.md` | Machine tags, parallel fan-out lane ownership, Claim lines |
| `joeOS/AI/Index.md` | Recently-added pages, stack pointer |
| `joeOS/AI/Stack - Shared Design System.md` | Studio Joe token set, Glass, themes |
| `sj-design/CLAUDE.md` | sj-automation PC tools table |
| `sj-design/evals/evals.json` | Eval criteria for skill output verification |
| `emoji-arcade/GAME-API.md` | headless `?debug`/`window.__game`, shell responsibility split |
| `memory/project_musicplayer_viz_gotchas.md` | drawImage black trap, reload no-op, concurrent tab false-black, destroyed-texture re-entry |
| `memory/reference_webgpu_headless_verification.md` | Claude_Preview hidden-page limits, GPU error-scopes, offscreen probe |
| `Daily Notes/2026-06-12.md` | Vercel bot-filtering, CSP inline-script trap, two-auditor pass notes, WGSL `patch` keyword kill, vec3f trap re-hit |
| `Daily Notes/2026-06-11.md` | `preview_eval` setTimeout destroys game, `pointer-events` overlay kill, programmatic `.click()` bypass, elementFromPoint lesson |
| `Daily Notes/2026-06-10.md` | Chrome cache-stale trap (`no-store`), foreground tab double-step sim, 60s steady-state requirement |
| `Daily Notes/2026-06-09.md` | 5-way review swarm pattern, `frame.beat` silent-black diagnosis, serve.js secrets/ security |
| `musicplayer-viz/audit/CODE-REVIEW-2026-06-09.md` | Review swarm structure, P0–P2 taxonomy, "frozen art" ground rule |
| `musicplayer-viz/audit/MULTI-AGENT-PLAYBOOK.md` | Context Packet, Lean parent, scout-first, fan-out cap |

---

## Distilled patterns

### 1. Tool hierarchy — always use the right tier

| Priority | Tool | When |
|---|---|---|
| 1st | `chrome-devtools MCP` (`take_screenshot`, `evaluate_script`, etc.) | Primary live-verify for ALL web pages — real Chrome, real GPU, real DOM |
| 2nd | `sja_*` tools (PC runner at 100.117.64.111) | D3D12 visual QA, fps sweeps, perf traces, iOS captures |
| 3rd | `Claude_Preview` (`preview_eval`, `preview_screenshot`) | Fallback only — hidden page, RAF paused, swapchain unreliable |

Source: `memory/project_musicplayer_viz_gotchas.md`, `memory/reference_webgpu_headless_verification.md`, `sj-design/CLAUDE.md`

**Why Chrome MCP over Preview:** Claude_Preview runs with `document.hidden === true`. RAF is paused → any rAF-driven loop never ticks. `drawImage(webgpuCanvas)` historically returns black (though not always — see UNVERIFIED). `preview_eval` with `setTimeout` >~2s collects the promise AND reloads the page, killing the running game mid-verify. Source: `Daily Notes/2026-06-11.md` ("destroyed the running game mid-verify twice").

---

### 2. WebGPU canvas — what reads black and what doesn't

| Method | Reliable? | Notes |
|---|---|---|
| `drawImage(gpuCanvas, ctx2d)` | NO (usually) | Returns black — WebGPU swapchain not CPU-readable via 2D canvas. Source: `memory/project_musicplayer_viz_gotchas.md` |
| `chrome-devtools take_screenshot` with `filePath` | YES | Saves to disk without attaching to context; works on background tabs; enabled 156-frame sweeps. Source: `memory/project_musicplayer_viz_gotchas.md` |
| GPU error-scope probe | YES | `pushErrorScope('validation')` → manual render frames → `popErrorScope()`. No readback needed. Source: `memory/reference_webgpu_headless_verification.md` |
| Offscreen texture + `copyTextureToBuffer` + `mapAsync` | YES (ground truth) | Compositor-independent. Preferred canvas format is often `bgra8unorm` — swap R/B on read. Source: `memory/reference_webgpu_headless_verification.md` |
| `window.VizShaderUtils.getCompilationInfo()` / `createShaderModuleChecked` | YES | Catches WGSL reserved-word kills (`patch`, `target`, `half`, `sample`, `filter`) that produce a silently-invalid pipeline with NO console error. Source: `Daily Notes/2026-06-12.md`, `memory/reference_webgpu_headless_verification.md` |

---

### 3. sj-automation PC runner — mandatory session protocol

```
1. sja_health  → confirm PC is awake (if fails: pm2 restart sj-job-server via sja_shell)
2. sja_screenshot / sja_perf_sweep  → quick visual + fps pass
3. sja_perfetto_trace  → reliable fps (Chrome compositor timestamps, no rAF clamping)
4. sja_nsight_trace  → GPU-side fps via D3D12 Present() — NVIDIA hardware clock
5. sja_pix_capture  → D3D12 frame debug (WebGPU pass breakdown, CPU vs GPU Δ)
6. sja_metal_trace  → Mac Metal System Trace (MTLCommandBuffer GPU clock, utilization %, BW)
```

Source: `sj-design/CLAUDE.md`, `musicplayer-viz/CLAUDE.md`

**Never skip `sja_health`.** If the PC is asleep, all subsequent tool calls silently fail or hang.

---

### 4. Cross-machine LAN HTTPS — secure context requirement

| Step | Detail | Source |
|---|---|---|
| WebGPU needs HTTPS (or localhost) | `navigator.gpu` is `undefined` over plain HTTP on a LAN IP | `WebGPU Cross-Machine Testing.md` |
| Expose on LAN | `HOST=0.0.0.0 PORT=3002 HTTPS_PORT=3444 node serve.js` (leaves loopback untouched) | `WebGPU Cross-Machine Testing.md` |
| Re-check host IP each session | `ipconfig getifaddr en0` — DHCP drifts | `WebGPU Cross-Machine Testing.md` |
| Self-signed cert interstitial | Chrome MCP often can't attach to the interstitial frame → human clicks "Proceed" once | `WebGPU Cross-Machine Testing.md` |
| Browser selection | `list_connected_browsers` → confirm with user → `select_browser <deviceId>` | `WebGPU Cross-Machine Testing.md` |
| Platform-probe before trusting | `navigator.platform` + `adapter.info` — extension browser selection can silently land elsewhere | `memory/project_musicplayer_viz_gotchas.md` |
| Teardown | `pkill -f "HOST=0.0.0.0"` ; `select_browser <mac id>` to restore MCP | `WebGPU Cross-Machine Testing.md` |

**Machine roles (fixed):**

| Machine | Tag | Role |
|---|---|---|
| Mac Air (`jdot-air`) | `[Mac]` | Canonical files + dev server + **weak-GPU perf bar** (if it holds 60fps here, it holds everywhere) |
| Windows PC (`Ray_Chrome`) | `[Win]` | Fast/clean visual QA + cross-platform D3D12 reference; fps is optimistic, never the perf bar |

Source: `WebGPU Cross-Machine Testing.md`

---

### 5. Metal vs D3D12 — which platform is stricter

| Behavior | Metal (Mac) | D3D12 (Win) |
|---|---|---|
| Undefined WGSL function | White screen | May silently succeed |
| Unfilterable-float + filtering sampler | Pipeline error | May pass |
| Storage texture alignment mismatch | Caught | Often missed |
| Missing shader utility include | White screen | Renders correctly |

**Rule: D3D12-clean does NOT mean cross-platform-clean. Mac Metal is the correctness bar.**
If a viz renders on Windows but is white on Mac → look for missing function includes or wrong sampler types.
Source: `WebGPU Scene Architecture — Best Practices.md §8`

---

### 6. Harness fps confound — don't trust suite fps

`_test-runner.html` runs many WebGPU contexts sequentially → driver memory pressure → artificially low fps (viz reading 4–10fps that run at 80–556fps standalone). **Trust the harness for pass/fail only. Re-measure fps STANDALONE (full navigate + ≥8s settle).** Slow-fill volumetrics (ink, cloud, nebula) start black; allow 15–20s warm-up before judging.
Source: `WebGPU Cross-Machine Testing.md`

---

### 7. Common false-black triggers (and their distinguishing probes)

| Symptom | Likely cause | Probe |
|---|---|---|
| Black on Metal, correct on D3D12 | Missing WGSL util include or wrong sampler | `getCompilationInfo()` on Mac |
| Black with audio, correct without | `frame.beat` undefined → NaN → uniform corrupt | `grep "f\.beat\|frame\.beat"` + alias to `beatPulse` |
| Black on first load only | `loadOp` missing `clear` on HDR attachment → garbage on frame 0 | Add `loadOp:'clear'` |
| Black after viz cycling | Destroyed-texture re-entry: teardown destroys textures, re-init leaves stale bind groups | Activate → switch-away → switch-back test |
| Black regardless of audio | All emission proportional to audio level; no idle floor | Add `max(audioLevel, 0.04)` floor |
| Black canvas but DOM HUD runs | WGSL reserved keyword (`patch`, `target`, `half`) → silently invalid pipeline; invalid bind group kills entire command buffer | `getCompilationInfo()` |
| NaN / everything black | `lastT` initialized to wall-clock; `t` starts near 0 → first `dt` is huge → `exp(Inf) = NaN` in uniform | Init `lastT = 0` or `lastT = t` |
| False-black in grading fan-out | 5+ concurrent WebGPU tabs → GPU-starved init | Cap at ~2 tabs; re-verify any "black" verdict single-tab |

Source: `WebGPU Scene Architecture — Best Practices.md §9`, `memory/project_musicplayer_viz_gotchas.md`

---

### 8. Page reload and cache traps

| Trap | Symptom | Fix |
|---|---|---|
| `window.location.reload()` via Chrome MCP is a no-op | Page does NOT actually reload; stale code runs; cost ~30min | Use `navigate` MCP tool; confirm `performance.now() < ~5000ms` |
| Chrome heuristic-caches stale scripts | Edit "doesn't take" even after server restart | `serve.js` should send `Cache-Control: no-store`; hard-reload Ctrl+Shift+R |
| Foreground tab + manual frame eval | Real RAF + manual `update()` → double-stepped sim → false washout | On foreground tab: wait + screenshot; drive only via `update()` loops in headless evals |
| `preview_eval` setTimeout >~2s | Promise collects AND reloads the page, destroying running game state | Use sync evals + explicit `sleep` between calls |

Source: `memory/project_musicplayer_viz_gotchas.md`, `Daily Notes/2026-06-11.md`

---

### 9. Deployed Vercel site verification

| Check | Method | Gotcha |
|---|---|---|
| CSP violations | `chrome-devtools list_console_messages` (clear:true first) after navigating prod URL | CSP forbids inline scripts: move `window.va` shim into external JS; `style 'unsafe-inline'` needed for injected game styles |
| Analytics beacon firing | Script request 200 + zero CSP errors = verified; beacon itself won't fire | CDP-driven Chrome has `navigator.webdriver=true` → Vercel bot-filters analytics. Never trust "no /view hit" as a bug from automated browsers. |
| Vercel auto-deploy | `vercel link --yes` connects repo; push to master → instant PRODUCTION (no gate) | No staging step: first push is prod |
| Security headers | `vercel.json` headers block: nosniff, X-Frame-Options DENY, Permissions-Policy | Verify headers in Network tab on prod; local serve.js may not replicate them |
| Private repo auto-deploy | Works; verify with an empty-commit push → check READY in ~23s | No diff from public repo flow |

Source: `Daily Notes/2026-06-12.md`

---

### 10. UI interaction verification — don't trust `.click()`

| What to verify | Right method | Wrong method |
|---|---|---|
| Element is clickable (not behind overlay) | `document.elementFromPoint(x, y)` returns expected element | `element.click()` — bypasses hit-testing, clicks invisible elements |
| Hidden overlay not eating events | `visibility:hidden` (removes from hit-test tree) | `display:none` or `pointer-events:none` alone — see emoji-slopes prod hotfix |
| Touch targets | Resize Chrome to 390×844 + functional click-path tests + CSS-rule asserts | `emulate` touch mode (blocked by classifier outage in at least one session) |

Source: `Daily Notes/2026-06-11.md` — "programmatic `.click()` bypasses hit-testing — verify UI with elementFromPoint + a real mouse click."

---

### 11. Two-auditor design review pattern

Confirmed used on emoji-slopes, emoji-arcade, and emoji-survivors (`Daily Notes/2026-06-12.md`):

```
Pedant (graphics/tech) — parallel subagent
Critic (game-dev / UX / design) — parallel subagent
Human = Arbiter
```

| Auditor role | Focus |
|---|---|
| Pedant (graphics) | WGSL correctness, GPU resource leaks, pipeline errors, Metal vs D3D12 deltas, uniform struct alignment |
| Critic (design/UX/game-dev) | Hit-guard logic, balance, responsive layout, GAME-API contract compliance, visual hierarchy, A11y |
| Human Arbiter | Resolves conflicts; ships only the Arbiter's accepted output |

Dispatch rules: parallel agents, file-ownership partitioned (no two agents touch the same file), structured output ("one block per file: finding/fix/effort"), self-verify before reporting.
Source: `Daily Notes/2026-06-12.md`, `musicplayer-viz/audit/MULTI-AGENT-PLAYBOOK.md`

---

### 12. sj-design skill eval verification

Evals live at `sj-design/evals/evals.json`. Current suite: 4 prompts (history-of-internet, saas-pitch-deck, outline-to-slides, youtube-embed).

| Criterion category | What to check |
|---|---|
| Structure | Correct slide count, correct types (title/content/quote/two-column/media/closing) |
| Style compliance | Sentence-case headings, active voice, no filler words (Apple Style Guide) |
| Output validity | Self-contained HTML, opens without errors, animations play |
| Media embeds | YouTube URL converted to embed format, iframe renders |
| Theme | Dark by default unless overridden |

Source: `sj-design/evals/evals.json`

---

### 13. Steady-state verification for simulations

For feedback simulations (fluid, reaction-diffusion, sand, wave), **10s windows hide saturation**. Verify at ≥60s steady state — `inject/(1 − dissipation)` is the saturation bound.
For WebGPU viz with audio, inject MODERATE synthetic audio (energy ~0.5, ~120bpm). HOT over-blooms → false washout; CALM/no-beat → energy-driven viz go black → false "broken".
Source: `memory/project_musicplayer_viz_gotchas.md`

---

### 14. Headless game verification (Emoji Arcade pattern)

The `GAME-API.md` contract requires `?debug` to expose `window.__game` (the sim). This enables headless verification without a visible game loop:

```js
// Drive update loop via sync evals
window.__game.update(dt)  // safe, no RAF dependency
window.__arcade  // shell state
```

Source: `emoji-arcade/GAME-API.md §Debug hook`, `Daily Notes/2026-06-12.md`

---

## Reviewer checklist candidates

Before claiming any visual/design output "verified":

- [ ] Used chrome-devtools MCP (not Preview) as primary verification tool
- [ ] `sja_health` called first if using PC runner
- [ ] Page reloaded via `navigate` MCP tool, not `window.location.reload()`
- [ ] `performance.now()` confirmed < a few thousand ms before trusting an edit took
- [ ] `Cache-Control: no-store` confirmed or hard-reload performed before judging output
- [ ] For WebGPU: `getCompilationInfo()` probe run (catches WGSL reserved-keyword kills)
- [ ] Black screen verdict re-verified single-tab (not during a multi-tab fan-out)
- [ ] Simulations verified at ≥8s settle (volumetrics: ≥15–20s; feedback sims: ≥60s)
- [ ] Clickable UI verified via `elementFromPoint`, not `element.click()`
- [ ] On Vercel: CSP violations checked in console, analytics verified by script 200 (not beacon)
- [ ] Cross-platform: tested on Mac Metal (correctness bar) not only Win D3D12
- [ ] Two-auditor pass run for significant design/feature changes (Pedant + Critic + Arbiter)
- [ ] `[x]` items in todo doc marked only AFTER verified, not just after edit

---

## Suggested decision-tree rows

| Question / task | Go to § |
|---|---|
| How do I verify a WebGPU canvas isn't black? | §2, §7 |
| Which browser tool should I use for live verification? | §1 |
| How do I set up cross-machine testing from the PC? | §4 |
| A viz works on Windows but shows white on Mac — why? | §5 |
| The fps from the test harness seems way too low — is it broken? | §6 |
| Black screen — where do I start diagnosing? | §7 |
| My edit "didn't take" even after saving | §8 |
| Vercel analytics aren't firing from my automated Chrome | §9 |
| A button click works in eval but fails in real Chrome | §10 |
| Running a design review — who plays what role? | §11 |
| Evaluating sj-design skill output — what criteria apply? | §12 |
| Verifying a fluid/particle sim isn't washed out or stuck | §13 |
| Driving an Emoji Arcade game headlessly | §14 |
| How do I start an sj-automation PC session? | §3 |

---

## UNVERIFIED

The following items could not be confirmed from the named source files and are noted as suspicions only:

- **`drawImage` sometimes works on Preview**: `reference_webgpu_headless_verification.md` states an earlier claim that it "always returns black" was "too absolute" and notes it worked in one session on musicplayer-viz. The condition (context `alphaMode:'opaque'` + immediate manual submit before capture) is described but not deterministically reproducible. Treat as unreliable — fall back to error-scope probe or offscreen readback.
- **Vercel CSP `style 'unsafe-inline'` requirement for sj-design**: noted for emoji-arcade in `2026-06-12.md`; sj-design CLAUDE.md does not explicitly document this CSP rule for presentation decks. Verify when sj-design first deploys.
- **Safari-specific behavioral differences**: `Daily Notes/2026-06-11.md` notes "Safari v1 user-verified" for Emoji Slopes and that Safari hardening was done in commit `6ac9bfe`. No explicit list of observed Safari vs Chrome behavioral deltas was found in the named files. A `joeOS/AI/` page for Safari testing was not found in the directory listing — this may be undocumented or live elsewhere.
- **`sja_capture` for Mac apps and iOS sims**: documented in `sj-design/CLAUDE.md` tool table but the current project (sj-design skill) has no native Mac/iOS target. Included for completeness; verify before applying to this skill's outputs.
- **musicplayer-viz `prototypes/_QA-LOG.md`**: referenced as the live rig + full QA detail in `WebGPU Cross-Machine Testing.md`. File not read in this pass; may contain additional cross-machine verification steps.
- **`graphics-inspector` test harness (`sja_gi_test`)**: mentioned in `sj-design/CLAUDE.md`; a `reference_wgsl_tools.md` memory note says `webgpu_inspector (adopt)`. Not read in this pass — additional verification patterns may exist there.
