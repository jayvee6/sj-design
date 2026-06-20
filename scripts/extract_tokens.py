#!/usr/bin/env python3
"""
Extract Studio Joe design tokens from assets/template.html into W3C DTCG JSON.

`assets/template.html` is the single source of truth for tokens — its :root
(dark, the default) and [data-theme="…"] blocks ARE the live token values. This
script parses those blocks and emits tokens/design-tokens.json so a tokens
pipeline (Style Dictionary, etc.) can consume them without re-implementing the
values. Re-run after editing any theme block; never hand-edit the JSON.

  python3 scripts/extract_tokens.py            # writes tokens/design-tokens.json
  python3 scripts/extract_tokens.py -o out.json

Design decision: gradients (--bg-gradient) and the 5-layer glass shadow
(--glass-shd) are kept as RAW CSS STRINGS under custom $types ('cssGradient',
'cssShadow'). Radial/elliptical gradients and multi-layer inset box-shadows are
not losslessly representable by the structured DTCG gradient/shadow types, so we
preserve them verbatim rather than lose fidelity. Plain colors keep their CSS
string value (hex or rgba()).
"""

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
TEMPLATE_PATH = SCRIPT_DIR.parent / "assets" / "template.html"
DEFAULT_OUT = SCRIPT_DIR.parent / "tokens" / "design-tokens.json"

BLOCK_RE = re.compile(r'(:root|\[data-theme="([a-z-]+)"\])\s*\{(.*?)\}', re.DOTALL)
DECL_RE = re.compile(r'--([\w-]+):\s*(.+?);', re.DOTALL)
COMMENT_RE = re.compile(r'/\*\s*(.*?)\s*\*/', re.DOTALL)


def tok_type(name: str) -> str:
    if name.startswith("font"):
        return "fontFamily"
    if name == "bg-gradient":
        return "cssGradient"
    if name == "glass-shd":
        return "cssShadow"
    return "color"


def font_key(k: str) -> str:
    return "sans" if k == "font" else k.replace("font-", "")


def extract(css: str) -> OrderedDict:
    themes = OrderedDict()
    fonts = OrderedDict()
    order = []

    for m in BLOCK_RE.finditer(css):
        sel, named, body = m.group(1), m.group(2), m.group(3)
        if "--bg:" not in body:          # skip non-token rules (#starfield opacity, etc.)
            continue
        name = "dark" if sel == ":root" else named
        cm = COMMENT_RE.search(body)
        desc = re.sub(r"\s+", " ", cm.group(1)).strip() if cm else ""
        color = OrderedDict()
        for d in DECL_RE.finditer(body):
            tname = d.group(1)
            tval = re.sub(r"\s+", " ", d.group(2).strip())
            if tname.startswith("font"):
                fonts.setdefault(tname, tval)   # global — only defined in :root
            else:
                color[tname] = tval
        themes[name] = (desc, color)
        order.append(name)

    doc = OrderedDict()
    doc["$description"] = (
        "Studio Joe design tokens (W3C DTCG format). Source of truth: "
        "assets/template.html — regenerate with scripts/extract_tokens.py, do "
        "not hand-edit. Every theme implements the same 13-name color contract. "
        "Custom $types: 'cssGradient' and 'cssShadow' hold raw CSS strings "
        "(radial/linear gradients and multi-layer inset box-shadows) verbatim, "
        "because they are not losslessly representable as structured DTCG "
        "gradient/shadow tokens. 'color' values are raw CSS color strings "
        "(hex or rgba()). Font families are 'fontFamily'."
    )

    font_group = OrderedDict({"$type": "fontFamily"})
    for k, v in fonts.items():
        font_group[font_key(k)] = OrderedDict({"$value": v})
    doc["font"] = font_group

    ordered = ["dark"] + [t for t in order if t != "dark"]
    theme_group = OrderedDict()
    for name in ordered:
        desc, color = themes[name]
        g = OrderedDict()
        if desc:
            g["$description"] = desc
        for tname, tval in color.items():
            g[tname] = OrderedDict({"$type": tok_type(tname), "$value": tval})
        theme_group[name] = g
    doc["theme"] = theme_group

    # sanity: every theme implements the full 13-name contract
    bad = {n: len(c) for n, (d, c) in themes.items() if len(c) != 13}
    if bad:
        raise SystemExit(f"Token contract violated (expected 13 per theme): {bad}")
    return doc


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract DTCG tokens from template.html")
    ap.add_argument("-o", "--output", default=str(DEFAULT_OUT))
    args = ap.parse_args()
    css = TEMPLATE_PATH.read_text(encoding="utf-8")
    doc = extract(css)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    n_themes = len(doc["theme"])
    n_fonts = len(doc["font"]) - 1  # minus $type
    print(f"✓ {out} — {n_themes} themes, {n_fonts} font families")


if __name__ == "__main__":
    main()
