# tokens/

Machine-readable design tokens for the Studio Joe system, in **W3C DTCG** format.

## Files
- **`design-tokens.json`** — all 17 themes × the 13-name color contract, plus 7
  font families. **Generated, do not hand-edit.**

## Source of truth & regeneration
`assets/template.html` is the source of truth — its `:root` (the `dark` default)
and `[data-theme="…"]` blocks are the live token values used by every generated
deck. This JSON is extracted from them:

```bash
python3 scripts/extract_tokens.py            # → tokens/design-tokens.json
```

Re-run after editing any theme block. Editing the JSON by hand will be
overwritten and won't affect the decks (which read the CSS), so don't.

## Structure
```jsonc
{
  "font":  { "$type": "fontFamily", "sans": { "$value": "-apple-system, …" }, … },
  "theme": {
    "dark":  { "$description": "Dark — Blue Hour…",
               "bg":          { "$type": "color",       "$value": "#060618" },
               "bg-gradient": { "$type": "cssGradient", "$value": "radial-gradient(…)" },
               "accent":      { "$type": "color",       "$value": "#0A84FF" },
               "glass-shd":   { "$type": "cssShadow",   "$value": "0 8px 40px …" },
               … },
    "light": { … }, "obsidian": { … }, … 17 themes total
  }
}
```

The 13 names every theme implements: `bg · bg-gradient · label-1 · label-2 ·
label-3 · accent · accent-glow · fill-1 · fill-2 · sep · glass-bg · glass-bdr ·
glass-shd`. A new look = a new 13-token block; the names never fork.

## Custom `$type`s — and why
Values are kept as **raw CSS strings** for losslessness:
- **`color`** — a CSS color string (`#RRGGBB` or `rgba(…)`), not a structured
  DTCG color object. Accepted as-is by Style Dictionary and most tooling.
- **`cssGradient`** (`--bg-gradient`) — the full CSS gradient string verbatim.
  These are radial/elliptical, multi-stop gradients that the structured DTCG
  `gradient` type cannot represent without loss, so we keep the CSS.
- **`cssShadow`** (`--glass-shd`) — the 5-layer (outer + inset bevel) box-shadow
  string verbatim. The signature glass surface; not faithfully expressible as a
  flat DTCG `shadow` array, so kept as CSS.

If a consumer needs structured gradient/shadow tokens, decompose these two
fields downstream — but treat the CSS string as the authoritative value.

## Consuming (example: Style Dictionary)
Map the custom types to a CSS `value` transform (identity for `cssGradient` /
`cssShadow`, color for `color`) and emit `:root` / `[data-theme]` blocks — i.e.
round-trip back to the same CSS contract `template.html` already uses. The token
*names* and theme *structure* are the stable contract; the engines and
`scripts/build_presentation.py` consume the CSS, not this JSON.
