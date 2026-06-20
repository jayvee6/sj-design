#!/usr/bin/env python3
"""
Verify the token round-trip: assets/template.html  ⇄  tokens/design-tokens.json.

Regenerates the JSON (extract_tokens) and the CSS (tokens_to_css) in memory and
asserts that the reconstructed `:root` / `[data-theme]` token declarations match
template.html exactly (whitespace-normalized). Exits non-zero on any drift, so
this can gate CI or a pre-commit hook.

  python3 scripts/verify_tokens.py        # prints a summary; exit 0 = clean

This guards the invariant that the published tokens never diverge from the live
CSS the decks actually use.
"""

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

import extract_tokens  # noqa: E402
import tokens_to_css   # noqa: E402

TEMPLATE = SCRIPT_DIR.parent / "assets" / "template.html"

BLOCK_RE = re.compile(r'(:root|\[data-theme="([a-z-]+)"\])\s*\{(.*?)\}', re.DOTALL)
DECL_RE = re.compile(r'--([\w-]+):\s*(.+?);', re.DOTALL)


def parse(css: str) -> OrderedDict:
    out = OrderedDict()
    for m in BLOCK_RE.finditer(css):
        sel, named, body = m.group(1), m.group(2), m.group(3)
        if "--bg:" not in body:
            continue
        name = "dark" if sel == ":root" else named
        toks = OrderedDict()
        for d in DECL_RE.finditer(body):
            toks[d.group(1)] = re.sub(r"\s+", " ", d.group(2).strip())
        out[name] = toks
    return out


def main() -> int:
    src_css = TEMPLATE.read_text(encoding="utf-8")
    tpl = parse(src_css)

    # round-trip: CSS -> DTCG JSON -> CSS
    doc = extract_tokens.extract(src_css)
    json.loads(json.dumps(doc))                       # JSON must serialize cleanly
    gen = parse(tokens_to_css.render(doc))

    if set(tpl) != set(gen):
        print(f"FAIL: theme sets differ: {set(tpl) ^ set(gen)}")
        return 1

    mismatches, total = 0, 0
    for theme in tpl:
        a, b = tpl[theme], gen[theme]
        for k in set(a) | set(b):
            total += 1
            if a.get(k) != b.get(k):
                mismatches += 1
                print(f"FAIL {theme}.{k}: template={a.get(k)!r} generated={b.get(k)!r}")

    print(f"themes: {len(tpl)} · declarations checked: {total} · mismatches: {mismatches}")
    if mismatches:
        print("RESULT: DRIFT — regenerate tokens (scripts/extract_tokens.py).")
        return 1
    print("RESULT: round-trip exact ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
