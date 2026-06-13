# Apple-Platform (Native) Design Patterns — sj-design-expert reference

**Scope:** macOS/iOS SwiftUI conventions used across Studio Joe native apps.
**Lens:** design patterns, token translation, structural choices that affect visual iteration speed.
**Excludes:** Metal/GPU shader internals (one-line cross-refs only; see graphics-api-expert / metal-debugger).
**Do not duplicate** the existing distillation in `sj-design/docs/swiftui-conventions.md`; this file extends it.

---

## Sources read

| File | App | What it captures |
|---|---|---|
| `StudioJoeMusic/Packages/Core/Sources/Core/UI/Theme/DesignTokens.swift` | StudioJoeMusic | Canonical Swift token enums: `StudioJoeColors`, `StudioJoeSpace`, `StudioJoeRadius`, `StudioJoeType`, `StudioJoeMotion`, `BlueHourBackground` |
| `StudioJoeMusic/Packages/Core/Sources/Core/UI/Theme/SJGlass.swift` | StudioJoeMusic | `SJGlassModifier`, `.sjGhost` / `.sjProminent` button styles — macOS glass fallback when system `.glass` renders flat |
| `StudioJoeMusic/StudioJoeMusicMac/MacRootView.swift` | StudioJoeMusic (Mac) | Full mac chrome architecture: `GlassEffectContainer` capsule, chrome auto-hide, popovers, `@Observable` AudioConductor, isolated `LiveReadoutView`, `@StateObject` VisualizerViewModel, `.windowStyle(.hiddenTitleBar)` |
| `StudioJoeMusic/Packages/Core/Sources/Core/UI/Components/ChromeAutoHide.swift` | StudioJoeMusic | Shared `ChromeAutoHide` state machine (`ObservableObject`, suspend-veto, popover pinning) |
| `StudioJoeMusic/StudioJoeMusic/App/RootView.swift` | StudioJoeMusic (iOS) | Tab structure, `@AppStorage` onboarding gate, `@StateObject GemmaModelManager`, `AnyView` injection pattern |
| `StudioJoeMusic/Packages/Core/Sources/Core/UI/Components/SettingsView.swift` | StudioJoeMusic | `#if os(iOS) … #else` branching, `.listStyle(.insetGrouped)` / `.listStyle(.inset)`, `.scrollContentBackground(.hidden)`, `listRowBackground(Color.white.opacity(0.06))`, `BlueHourBackground` behind List |
| `StudioJoeMusic/StudioJoeMusic/StudioJoeMusicApp.swift` | StudioJoeMusic (iOS) | `@UIApplicationDelegateAdaptor`, `WindowGroup`, constructor dependency injection |
| `StudioJoeMusic/StudioJoeMusicMac/StudioJoeMusicMacApp.swift` | StudioJoeMusic (Mac) | `Window(…)` scene, `.defaultSize`, `.windowStyle(.hiddenTitleBar)` |
| `LinguaFranca/LinguaFranca/Resources/ColorTokens.swift` | LinguaFranca | Parallel `Color` extension approach: `sjAccent`, `sjLabel1/2/3`, `sjFill1/2`, `sjGlassBg/Bdr`, `sjSep`; `LinearGradient.blueHour` as diagonal approximation of the radial CSS gradient |
| `LinguaFranca/LinguaFranca/Views/Components/GlassCard.swift` | LinguaFranca | `GlassCard` ViewModifier — `ultraThinMaterial` + `sjGlassBg` fill + gradient `strokeBorder` + shadows; extension `.glassCard(cornerRadius:)` |
| `LinguaFranca/LinguaFranca/App/LinguaFrancaApp.swift` | LinguaFranca | `Result<ModelContainer, Error>` init guard for SwiftData, `.environmentObject(TranslationService.shared)`, `@AppStorage("hasSeenOnboarding")`, `ContainerFailureView` recovery pattern |
| `LinguaFranca/LinguaFranca/Views/ContentView.swift` | LinguaFranca | `NavigationSplitView` with column-width constraints (240/280/360), `.navigationSplitViewStyle(.balanced)`, `.sheet` for settings |
| `LinguaFranca/LinguaFranca/Views/OnboardingView.swift` | LinguaFranca | `TabView` multi-page onboarding, `.tabViewStyle(.page)` iOS-only `#if`, `@ViewBuilder` action slot pattern |
| `ripple-apple/Packages/RippleCore/Sources/RippleCore/DesignSystem.swift` | Ripple (iOS) | App-specific color palette + typography (ultra-light weights, `.monospacedDigit()`); `DesignSystem.GlassPanel` with `if #available(iOS 26) { .glassEffect } else { ultraThinMaterial }` |
| `ripple-apple/Ripple/Views/RootView.swift` | Ripple (iOS) | `@Observable AppState`, persistent Metal canvas as background, curtain overlay for screen transitions (fade-to-black + swap-under-curtain), Reduce Motion gating, `UIAccessibility.post(notification:)` on screen change |
| `ripple-apple/Ripple/Views/LiquidGlassOrb.swift` | Ripple (iOS) | `.clear` Glass variant for lens body; angular gradient bezel; `.blendMode(.plusLighter)` specular; `OrbCaustic` RadialGradient caustic detail |
| `TranscriptStudio/Sources/TranscriptStudio/ContentView.swift` | TranscriptStudio (Mac) | `GlassEffectContainer` as top-level card wrapper; `.glassEffect(.regular, in: .rect(cornerRadius: 22))` for cards; `.buttonStyle(.glassProminent)` / `.buttonStyle(.glass)`; drop-zone pattern with `.onDrop` + `$dropTargeted`; uppercase caption-weight card labels |
| `StudioJoeSavers/Savers/StudioJoeSavers/MainScreenSaverView.swift` | StudioJoeSavers | AppKit `ScreenSaverView` + NSWindow configure panel; `NSPopUpButton` for scene picker; `CAKeyframeAnimation` fade-transition; occlusion-based GPU teardown; `DistributedNotificationCenter` willstop hook — Metal design only, not SwiftUI |
| `StudioJoeSavers/Savers/StudioJoeSavers/Prefs.swift` | StudioJoeSavers | `@propertyWrapper SimpleStorage<T>` backed by `ScreenSaverDefaults` |
| `sj-design/docs/swiftui-conventions.md` | All | Existing distillation (Liquid Glass API, color → SwiftUI translation, BlueHourBackground, button patterns, pre-iOS 26 fallback) — **do not re-derive** |

---

## Distilled patterns

### P1 — Token systems (one per app, all derive from CSS source of truth)

| App | Namespace | Approach |
|---|---|---|
| StudioJoeMusic | `StudioJoeColors`, `StudioJoeSpace`, `StudioJoeRadius`, `StudioJoeType`, `StudioJoeMotion` | Enums with static properties; semantic scales (not raw point sizes) |
| LinguaFranca | `Color` extension (`sjAccent` etc.) | Extension constants; `LinearGradient.blueHour` as diagonal for radial CSS gradient |
| Ripple | `DesignSystem.Palette`, `DesignSystem.Typography` | Nested enums inside a single `DesignSystem` container |
| StudioJoeSavers | No SwiftUI tokens — Metal/AppKit only | `ScreenSaverDefaults`-backed `@propertyWrapper SimpleStorage<T>` for prefs |

**Key divergence to flag:** `StudioJoeColors.label3` was raised from `0.25` → `0.46` alpha for WCAG 1.4.3 (≥4.5:1 AA on black). LinguaFranca still uses `0.25`. Any new app should start at `0.46`.

### P2 — Glass surface hierarchy (three tiers)

| Tier | SwiftUI | When |
|---|---|---|
| System Liquid Glass (iOS/macOS 26+) | `.glassEffect(.regular, in: shape)` / `GlassEffectContainer` | Primary chrome — transport, cards, HUDs. All apps targeting iOS/macOS 26+ use this first. |
| sj-design manual glass (pre-26 or Mac flat rendering) | `.sjGlass(in: shape)` (`SJGlassModifier`) — `ultraThinMaterial` + white fill + lip-gradient `strokeBorder` + dual shadow | Mac target, or when system `.glass` looks flat (macOS 26 renders `.glass` button styles as flat dark pills on some surfaces) |
| App-scoped glass card | `.glassCard(cornerRadius:)` (LinguaFranca) / `DesignSystem.GlassPanel` (Ripple) | Apps without the Core package; same visual recipe as SJGlassModifier |

**Ripple availability guard pattern** (copy-paste ready for any cross-deployment target):
```swift
// DesignSystem.GlassPanel body:
#if os(iOS)
if #available(iOS 26, *) {
    content.glassEffect(.regular, in: .rect(cornerRadius: cornerRadius, style: .continuous))
} else {
    legacyPanel(content)   // ultraThinMaterial fallback
}
#else
legacyPanel(content)
#endif
```

### P3 — Background: Blue Hour

The CSS `radial-gradient(ellipse at 35% 15%, …)` translates two ways:

| App | Swift form | Notes |
|---|---|---|
| StudioJoeMusic | `BlueHourBackground` — `ZStack { bgBase; GeometryReader { RadialGradient(center: 0.35/0.15, endRadius: max(w,h)*1.15) } }` | Canonical; `.ignoresSafeArea()` inside |
| LinguaFranca | `LinearGradient.blueHour` — diagonal `topLeading → bottomTrailing` | Approximation; avoids `GeometryReader` overhead but loses the directional radial feel |
| TranscriptStudio | Inline `RadialGradient` + secondary `RadialGradient` counter-glow | Two-layer for depth on long-scroll Mac surfaces |

**Rule:** Use `BlueHourBackground` (or the radial form) wherever the viz or a full-screen chrome sits. Use the linear approximation only for sidebar / column content.

### P4 — State management patterns

| Pattern | Apps | Notes |
|---|---|---|
| `@Observable` (iOS 17+/macOS 14+) | `AudioConductor` (StudioJoeMusic Mac), `AppState` (Ripple) | Used for lightweight models directly observed by views — no wrapper needed |
| `ObservableObject` + `@StateObject` / `@ObservedObject` | `VisualizerViewModel`, `ChromeAutoHide`, `TranslationService`, `SpotifyPlaybackSource` | Still dominant for models with complex lifecycle or cross-package sharing |
| `@AppStorage` | Onboarding gate (`didCompleteOnboarding`, `hasSeenOnboarding`), HUD toggle (`sjHudVisible`) | All persistent single-value state; never session data |
| SwiftData `@Query` | LinguaFranca (`sessions`) | Only app using SwiftData; init guards for migration safety |
| Dependency injection via struct `Dependencies` | `VisualizerViewModel.Dependencies` | App-level services built in `App.init`, injected; Core has zero knowledge of app types |
| `AnyView` injection | `SettingsView(modelSection: AnyView(GemmaModelSettingsView(…)))` | Cross-package boundary pattern; Core can reference `AnyView` without importing app modules |

### P5 — macOS-specific conventions

| Convention | Source | Detail |
|---|---|---|
| Hidden title bar window | `StudioJoeMusicMacApp` | `.windowStyle(.hiddenTitleBar)` + `.defaultSize(width: 1000, height: 700)` + `.frame(minWidth: 700, minHeight: 480)` on root view |
| `Window(…, id:)` not `WindowGroup` | `StudioJoeMusicMacApp` | Single-window apps use `Window` scene; `WindowGroup` for document-style |
| `NavigationSplitView` | LinguaFranca | Master-detail Mac layout; `.navigationSplitViewColumnWidth(min: 240, ideal: 280, max: 360)` + `.navigationSplitViewStyle(.balanced)` |
| `.listStyle(.inset)` | `SettingsView` (Mac branch) | macOS branch of `#if os(iOS) … .listStyle(.insetGrouped) #else .listStyle(.inset)` |
| Popovers as control panels | `MacRootView` | Settings that would be sheets on iOS become `.popover(isPresented:, arrowEdge: .top)` on Mac; popover open state vetoes chrome auto-hide |
| Settings sheet sizing | LinguaFranca | `.sheet` + `#if os(macOS) .frame(minWidth: 520, minHeight: 520)` |
| `.onHover` for row feedback | `TranscriptStudio.LibraryRow` | `.onHover { hovering = $0 }` + background fill opacity change + arrow icon reveal; `.animation(.easeOut(duration: 0.12), value: hovering)` |
| Context menu on rows | `TranscriptStudio.LibraryRow` | `.contextMenu { Button/Divider/Button(role:.destructive) }` — standard Mac right-click |
| `NSWorkspace.shared.activateFileViewerSelecting([url])` | `TranscriptStudio` | Standard "Reveal in Finder" action |
| AppKit configure panel via `ScreenSaverView` | `StudioJoeSavers` | `hasConfigureSheet + configureSheet` override; free-floating `NSWindow` workaround for macOS 14+ sandboxed appex |

### P6 — Chrome auto-hide (shared state machine)

`ChromeAutoHide` (`ObservableObject`, `@MainActor`) is the canonical pattern for floating playback chrome. Key behaviors:

- Auto-hides only **while playing**; pause/idle keeps chrome up indefinitely.
- `note()` on any interaction shows chrome and re-arms the timer.
- `suspendHide: Bool` is an external veto (popover open, VoiceOver running).
- iOS default: 4 s hide delay. Mac: 3 s.
- Opacity + `allowsHitTesting` are both gated on `chrome.isVisible`.
- Animation: `.easeInOut(duration: 0.22)` for opacity; optionally `.spring` for scale.

```swift
// Canonical wiring (Mac):
.opacity(chrome.isVisible ? 1 : 0)
.allowsHitTesting(chrome.isVisible)
.animation(.easeInOut(duration: 0.22), value: chrome.isVisible)
```

**Veto pattern when popover is open:**
```swift
.onChange(of: showSourcePopover) { _, _ in
    chrome.suspendHide = showSourcePopover || showModePopover
}
```

### P7 — Motion / animation tokens

From `StudioJoeMotion` (canonical):

| Token | Value | Use |
|---|---|---|
| `durationFast` | 0.18 s | Taps, toggles, state flips |
| `durationStandard` | 0.28 s | Default transitions |
| `durationSlow` | 0.45 s | Large / expressive movements |
| `springSnappy` | `response: 0.28, dampingFraction: 0.78` | Interactive controls |
| `springSmooth` | `response: 0.45, dampingFraction: 0.86` | Content reveals, sheets |

Ripple uses longer curtain durations (1.2 s fade-out, 5.0 s fade-in on outro) for meditative pacing — appropriate for breathing app, not general UI.

**Reduce Motion** is gated at two levels:
1. `@Environment(\.accessibilityReduceMotion)` — swap springs for instant or `.opacity` only.
2. Ripple: `withAnimation(reduceMotion ? nil : …)` — nil animation = instant snap.

### P8 — Typography approach

| App | Approach | Notes |
|---|---|---|
| StudioJoeMusic | `StudioJoeType` semantic tokens (`Font.largeTitle.weight(.bold)`, etc.) + `.monospacedDigit()` for readouts | Dynamic Type-safe: no fixed point sizes |
| LinguaFranca | System text styles directly (`.title.bold()`, `.body`, `.caption`) | Same effect as StudioJoeType without the enum |
| Ripple | Fixed sizes (`size: 34`, `size: 64`) with ultra-light/thin weights | **Exception:** bespoke meditation aesthetic; do not apply to general UI |
| TranscriptStudio | Inline `.font(.system(size: 34, weight: .bold))` for hero; `.callout`/`.caption` for content | Pre-token era; hero size hardcoded |

**Rule:** Prefer semantic text styles over fixed `.system(size:)` calls so the whole app scales with Dynamic Type for free. Match `StudioJoeType` enum in new apps; use `StudioJoeRadius.card` (26 pt) for transport / prominent glass cards.

### P9 — Settings / preferences UI pattern

All apps use a `List`-based settings view with:
- `.scrollContentBackground(.hidden)` + `BlueHourBackground()` as list background.
- `.listRowBackground(Color.white.opacity(0.06))` on each Section.
- `.preferredColorScheme(.dark)` + `.tint(StudioJoeColors.accent)` at settings root.
- `NavigationStack` wrapping with `.navigationTitle("Settings")`.
- Cross-platform branch: `.navigationBarTitleDisplayMode(.inline)` iOS only.
- **No "Done" button when settings is a full tab** — only when sheet-presented.

### P10 — Onboarding gate pattern

Consistent across StudioJoeMusic and LinguaFranca:
```swift
@AppStorage("didCompleteOnboarding") private var didCompleteOnboarding = false

// Presentation:
.fullScreenCover(isPresented: Binding(get: { !didCompleteOnboarding }, set: { … })) {
    OnboardingFlow(onComplete: { didCompleteOnboarding = true })
}
```
LinguaFranca adds a model-presence gate between onboarding and main content — a three-state router: onboarding → model download → main content.

### P11 — Accessibility

| Pattern | Where applied |
|---|---|
| `.accessibilityHidden(true)` on decorative visualizers/Metal views | `VisualizerUI`, `RootView` (Ripple), `LiquidGlassOrb` bezel |
| `.accessibilityLabel("Back 10 seconds")` etc. on icon-only buttons | `MacRootView`, `VisualizerUI` transport |
| `.accessibilityAddTraits(.startsMediaSession)` on play button | `VisualizerUI` |
| `.accessibilityElement(children: .contain)` + `.accessibilityLabel("Playback controls")` on transport group | `MacRootView` |
| `UIAccessibility.post(notification: .screenChanged, argument: nil)` after screen swap | Ripple `RootView` — fires after curtain retraction so VoiceOver focus moves |
| `VoiceOver veto` of chrome auto-hide | `VisualizerUI` (`voiceOverRunning` state; chrome.suspendHide when VO is on) |
| `.accessibilityAddTraits(.isHeader)` on titles | LinguaFranca onboarding, ContainerFailureView |
| `.accessibilityHint("Permanently deletes…")` | LinguaFranca ContainerFailureView destructive button |

### P12 — macOS-only design elements (StudioJoeSavers)

StudioJoeSavers is AppKit-only (Metal + ScreenSaver framework). SwiftUI is not used. Key design-side conventions:
- `NSWindow` configure panel (360×160, `.titled .closable`) with `NSPopUpButton` for scene selection.
- `CAKeyframeAnimation` `.cubic` calculation mode for S-curve scene transition fade (0.4 s out → rebuild → 0.4 s in).
- `ScreenSaverDefaults` + `@propertyWrapper SimpleStorage<T>` for persistent prefs.
- GPU occlusion teardown: 30 s debounce before freeing Metal resources on hidden windows.
- **No sj-design CSS tokens** — purely system/Metal aesthetic; no Blue Hour here.

---

## Reviewer checklist candidates

- [ ] **label3 alpha** — is `Color.white.opacity(0.46)` (WCAG AA floor) used, not `0.25`?
- [ ] **Glass tier** — does code use `.glassEffect()` on iOS/macOS 26+, `.sjGlass()` as Mac fallback, and `ultraThinMaterial` as the pre-26 path? No naked `.background(.ultraThinMaterial)` + manual shadow stack on iOS 26.
- [ ] **Blue Hour form** — full `RadialGradient` (canonical) vs. diagonal `LinearGradient` (approximation)? Approximation is only acceptable in column/sidebar contexts.
- [ ] **Token use** — spacing from `StudioJoeSpace.*`, radii from `StudioJoeRadius.*`, font from `StudioJoeType.*` or semantic system styles? No bare magic numbers.
- [ ] **Motion tokens** — `StudioJoeMotion` durations and springs used? Reduce Motion path exists (nil animation or opacity-only)?
- [ ] **Settings list background** — `.scrollContentBackground(.hidden)` + `BlueHourBackground()` + `.listRowBackground(Color.white.opacity(0.06))`?
- [ ] **Chrome veto** — popover/sheet open state sets `chrome.suspendHide = true`?
- [ ] **Perf isolation** — fast-changing audio state in an isolated `private struct` view so parent body doesn't re-evaluate at audio frame rate?
- [ ] **Accessibility** — decorative Metal/Canvas view has `.accessibilityHidden(true)`? Icon-only buttons have `.accessibilityLabel`?
- [ ] **Onboarding gate** — `@AppStorage` bool used (not in-memory) so gate survives cold launches?
- [ ] **macOS window** — single-window apps use `Window(…, id:)` not `WindowGroup`? `.windowStyle(.hiddenTitleBar)` set?
- [ ] **SwiftData init guard** — `Result<ModelContainer, Error>` with a recovery view, not `try!` or `fatalError`?

---

## Suggested decision-tree rows

| Question / task | Go to § |
|---|---|
| "What glass modifier should I use?" | § P2 — Glass surface hierarchy |
| "How do I add auto-hiding playback chrome?" | § P6 — Chrome auto-hide |
| "What spacing/radius/motion values should I use?" | § P1, P7 — Token systems, Motion tokens |
| "Which Observable pattern fits my model?" | § P4 — State management |
| "How do I set up a macOS single-window app?" | § P5 — macOS conventions |
| "How do I implement settings UI?" | § P9 — Settings pattern |
| "How do I implement first-launch onboarding?" | § P10 — Onboarding gate |
| "The Blue Hour background looks wrong on Mac" | § P3 — choose RadialGradient form |
| "Is my label3 color accessible?" | § P11, reviewer checklist |
| "Font sizes look off / don't scale" | § P8 — Typography approach |
| "Saver needs a configure panel" | § P12 — StudioJoeSavers (AppKit) |
| "What's the fallback for iOS < 26?" | swiftui-conventions.md §5 + § P2 here |
| "Metal / GPU shader internals" | graphics-api-expert skill, metal-debugger skill |

---

## UNVERIFIED

- **`StudioJoeType` / `StudioJoeSpace` / `StudioJoeRadius` / `StudioJoeMotion` adoption at call sites:** The four scale enums were added in `DesignTokens.swift` with an explicit note that "call sites migrate later." As of reading, some existing views in StudioJoeMusic still use inline literal values (e.g., `padding(14)`, `.system(size: 34, weight: .bold)` in TranscriptStudio). Migration completeness not verified across all views.
- **Ripple iOS 26 glassEffect live in production:** `DesignSystem.GlassPanel` has the `#available(iOS 26, *)` branch, but the exact call sites using `.glassPanel()` were not fully traced to confirm they've been tested on device.
- **LinguaFranca light-mode behavior:** The app uses `preferredColorScheme(.dark)` in some views, but `ColorTokens.swift` uses `Color.white.opacity(...)` semantics with a comment "system adapts in light mode via .primary/.secondary." Whether light mode is explicitly supported or intentionally unsupported was not confirmed from source.
- **StudioJoeSavers design layer:** Only `MainScreenSaverView.swift` and `Prefs.swift` were read. Scene-level design decisions (visual style, typography, palette choices inside individual Metal scenes) live in `Sources/SaverCore/Scenes/*.swift` — not read because they are Metal/GPU scope (graphics-api-expert territory).
- **TranscriptStudio `App.swift` and `ViewerView.swift`:** Not read (not directly design-relevant); viewer is an embedded WKWebView that opens the generated HTML page.
