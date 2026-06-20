#!/usr/bin/env python3
"""
Render tokens/design-tokens.json back into CSS custom-property blocks.

This is the inverse of extract_tokens.py and serves two purposes:
  1. Proof — the round-trip (template.html → JSON → CSS) reproduces the exact
     token contract, so the JSON is a faithful representation.
  2. Example — a ready-made consumer showing how to turn the DTCG tokens into
     the `:root` + `[data-theme="…"]` CSS the engines actually use.

  python3 scripts/tokens_to_css.py            # → tokens/themes.css

Generated; do not hand-edit. assets/template.html stays the source of truth.
"""

import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DEFAULT_IN = SCRIPT_DIR.parent / "tokens" / "design-tokens.json"
DEFAULT_OUT = SCRIPT_DIR.parent / "tokens" / "themes.css"

# Canonical order of the 13-name color contract (matches template.html).
COLOR_ORDER = [
    "bg", "bg-gradient", "label-1", "label-2", "label-3", "accent",
    "accent-glow", "fill-1", "fill-2", "sep", "glass-bg", "glass-bdr", "glass-shd",
]
FONT_ORDER = ["sans", "serif", "chicago", "geneva", "lucida", "garamond", "monaco"]
FONT_CSS_NAME = {"sans": "font"}  # 'sans' → --font; others → --font-<key>


def font_var(key: str) -> str:
    return "--font" if key == "sans" else f"--font-{key}"


def render(doc: dict) -> str:
    fonts = doc["font"]
    themes = doc["theme"]
    lines = [
        "/* Studio Joe design tokens — GENERATED from tokens/design-tokens.json",
        "   by scripts/tokens_to_css.py. Do not hand-edit. Source of truth:",
        "   assets/template.html. This is the round-trip proof + a consume example. */",
        "",
    ]

    def emit_block(selector: str, theme_key: str, include_fonts: bool) -> None:
        t = themes[theme_key]
        if t.get("$description"):
            lines.append(f"/* {t['$description']} */")
        lines.append(f"{selector} {{")
        if include_fonts:
            for fk in FONT_ORDER:
                if fk in fonts:
                    lines.append(f"  {font_var(fk)}: {fonts[fk]['$value']};")
            lines.append("")
        for name in COLOR_ORDER:
            if name in t:
                lines.append(f"  --{name}: {t[name]['$value']};")
        lines.append("}")
        lines.append("")

    # dark is the :root default and carries the font tokens.
    emit_block(":root", "dark", include_fonts=True)
    for key in themes:
        if key == "dark":
            continue
        emit_block(f'[data-theme="{key}"]', key, include_fonts=False)

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Render DTCG tokens to CSS blocks")
    ap.add_argument("-i", "--input", default=str(DEFAULT_IN))
    ap.add_argument("-o", "--output", default=str(DEFAULT_OUT))
    args = ap.parse_args()
    doc = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(doc), encoding="utf-8")
    print(f"✓ {out} — {len(doc['theme'])} themes")


if __name__ == "__main__":
    main()
