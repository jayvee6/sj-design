# SwiftUI / iOS 26 Conventions

How to apply the sj-design palette to native iOS using Apple's iOS 26 Liquid Glass APIs. Reference target: the [StudioJoeMusic](../../StudioJoeMusic) app.

This document is for **native iOS** only. For web/HTML decks, the existing CSS glass mixin in the skill templates is the right tool. See the [`reference_design_tokens`](../../../.claude/projects/-Users-jdot-Documents-Development/memory/reference_design_tokens.md) memory for the canonical CSS spec.

---

## 1. Color palette → SwiftUI `Color`

Drop-in translation of the studiojoe dark-mode token set:

```swift
import SwiftUI

public enum StudioJoeColors {
    // Accent — #0A84FF
    public static let accent = Color(red: 0x0A / 255, green: 0x84 / 255, blue: 0xFF / 255)

    // Label hierarchy — white at declining alpha
    public static let label1 = Color.white.opacity(0.92)
    public static let label2 = Color.white.opacity(0.55)
    public static let label3 = Color.white.opacity(0.25)

    // Fills + separators
    public static let fill1 = Color.white.opacity(0.06)
    public static let fill2 = Color.white.opacity(0.11)
    public static let sep   = Color.white.opacity(0.12)

    // Blue Hour radial stops
    public static let bgBase  = Color.black
    public static let bgStop0 = Color(red: 0x1A / 255, green: 0x23 / 255, blue: 0x7E / 255)
    public static let bgStop1 = Color(red: 0x19 / 255, green: 0x19 / 255, blue: 0x70 / 255)
    public static let bgStop2 = Color(red: 0x0D / 255, green: 0x0D / 255, blue: 0x3A / 255)
    public static let bgStop3 = Color(red: 0x05 / 255, green: 0x05 / 255, blue: 0x10 / 255)
}
```

Set the accent once at the root view with `.tint(StudioJoeColors.accent)` so system controls (`.buttonStyle(.glassProminent)`, selection highlights, switches) pick it up.

---

## 2. Blue Hour background

iOS equivalent of the CSS `--bg-g: radial-gradient(ellipse at 35% 15%, …)`:

```swift
public struct BlueHourBackground: View {
    public init() {}
    public var body: some View {
        ZStack {
            StudioJoeColors.bgBase
            GeometryReader { geo in
                RadialGradient(
                    gradient: Gradient(stops: [
                        .init(color: StudioJoeColors.bgStop0, location: 0.00),
                        .init(color: StudioJoeColors.bgStop1, location: 0.28),
                        .init(color: StudioJoeColors.bgStop2, location: 0.58),
                        .init(color: StudioJoeColors.bgStop3, location: 1.00)
                    ]),
                    center: UnitPoint(x: 0.35, y: 0.15),
                    startRadius: 0,
                    endRadius: max(geo.size.width, geo.size.height) * 1.15
                )
            }
        }
        .ignoresSafeArea()
    }
}
```

Also call `.preferredColorScheme(.dark)` at the scene root so system chrome matches.

---

## 3. Liquid Glass API reference

Canonical signatures extracted from the iOS 26 SDK swiftinterface at:

```
/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/
  Developer/SDKs/iPhoneSimulator26.4.sdk/System/Library/Frameworks/
  SwiftUICore.framework/Modules/SwiftUICore.swiftmodule/
  arm64-apple-ios-simulator.swiftinterface
```

Grep this file any time you need to verify an API.

### `Glass` value type

```swift
@available(iOS 26.0, *)
public struct Glass: Equatable, Sendable {
    public static var regular: Glass { get }
    public static var clear: Glass { get }
    public static var identity: Glass { get }
    public func tint(_ color: Color?) -> Glass
    public func interactive(_ isEnabled: Bool = true) -> Glass
}
```

### View modifiers

```swift
@available(iOS 26.0, macOS 26.0, tvOS 26.0, watchOS 26.0, *)
@available(visionOS, unavailable)
public func glassEffect(_ glass: Glass = .regular,
                        in shape: some Shape = DefaultGlassEffectShape()) -> some View

public func glassEffectTransition(_ transition: GlassEffectTransition) -> some View
public func glassEffectID(_ id: (some Hashable & Sendable)?, in namespace: Namespace.ID) -> some View
public func glassEffectUnion(id: (some Hashable & Sendable)?, namespace: Namespace.ID) -> some View
```

### Container

```swift
@MainActor
public struct GlassEffectContainer<Content: View>: View {
    public init(spacing: CGFloat? = nil, @ViewBuilder content: () -> Content)
}
```

### Button styles

```swift
extension PrimitiveButtonStyle where Self == GlassButtonStyle {
    public static var glass: GlassButtonStyle { get }
    public static func glass(_ glass: Glass) -> Self       // iOS 26.1+
}
extension PrimitiveButtonStyle where Self == GlassProminentButtonStyle {
    public static var glassProminent: GlassProminentButtonStyle { get }
}
```

---

## 4. Usage patterns

| Case | Pattern |
|---|---|
| Primary action | `.buttonStyle(.glassProminent)` + root `.tint(StudioJoeColors.accent)` |
| Secondary action | `.buttonStyle(.glass)` |
| Chrome card (HUD / toolbar / sheet) | `view.padding(...).glassEffect(.regular, in: .rect(cornerRadius: 18))` |
| Grouped controls | Wrap in `GlassEffectContainer(spacing: 12) { … }` so adjacent glass pieces morph together |
| Tinted glass accent | `.glassEffect(Glass.regular.tint(StudioJoeColors.accent), in: .capsule)` |
| Touch-reactive glass | `.glassEffect(.regular.interactive(), in: .circle)` |
| Custom shape | `.glassEffect(.regular, in: Capsule())` or any `Shape` — defaults to `DefaultGlassEffectShape` |

### Typography — keep native

Use the system font; no custom font files. sj-design tokens in Apple's typography map directly:

```swift
.font(.system(.title3, design: .rounded, weight: .semibold))   // headings / HUD
.font(.system(.body, weight: .semibold))                        // primary action labels
.font(.system(.caption, design: .monospaced))                   // telemetry / BPM readouts
```

### Layout example (from StudioJoeMusic)

```swift
ZStack {
    BlueHourBackground()
    visualizerCanvas

    VStack {                                       // HUD card — top-left
        HStack {
            hudContent
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .glassEffect(.regular, in: .rect(cornerRadius: 18))
            Spacer()
        }
        Spacer()
    }

    VStack {                                       // Transport — bottom-center
        Spacer()
        GlassEffectContainer(spacing: 12) {
            HStack(spacing: 12) {
                Button { pickSong() } label: { Label("Pick Song", systemImage: "music.note.list") }
                    .buttonStyle(.glassProminent)
                Button { togglePlayPause() } label: { Image(systemName: "play.fill") }
                    .buttonStyle(.glass)
            }
        }
        .padding(.bottom, 28)
    }
}
.tint(StudioJoeColors.accent)
.preferredColorScheme(.dark)
```

---

## 5. When NOT to use native Liquid Glass

| Target | Use |
|---|---|
| Slide decks (`.html`), studiojoe.dev, sj-design web showcase | Existing CSS `feDisplacementMap` glass mixin |
| iOS < 26 fallback path | `.ultraThinMaterial` / `.regularMaterial` + `.clipShape(RoundedRectangle(...))` |
| Design handoff to non-iOS surfaces | CSS mixin, not the native APIs |

The iOS 26 Liquid Glass look is the real deal — system-refracted, device-accelerated, content-aware. Don't try to hand-roll it with `.background(.ultraThinMaterial)` + shadows on iOS 26 — use the system modifier.

---

## References

- Canonical SwiftUI surface: grep the SDK swiftinterface (path above)
- Production usage: [StudioJoeMusic](../../StudioJoeMusic) — Phase 1 VisualizerUI uses all of the above
- CSS token source of truth: [`reference_design_tokens`](../../../.claude/projects/-Users-jdot-Documents-Development/memory/reference_design_tokens.md)
- Apple Developer → Landmarks: Building an app with Liquid Glass (iOS 26 sample app)
