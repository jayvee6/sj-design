#!/usr/bin/env python3
"""build_design_md.py — render a project's DESIGN.md from the canonical tokens.

    python3 scripts/build_design_md.py                       # → ./DESIGN.md (theme: dark)
    python3 scripts/build_design_md.py --theme deep-space --out ~/Development/foo/DESIGN.md
    python3 scripts/build_design_md.py --theme dark --out <project>/DESIGN.md --link

Token values come ONLY from tokens/design-tokens.json (which verify_tokens.py proves
round-trips to assets/template.html). Rules/prose come from tokens/DESIGN.template.md.
Nothing here is hand-copied, so DESIGN.md cannot drift from the live CSS: re-run to refresh.

--link adds (idempotently) a pointer block to <project>/CLAUDE.md so every session in
that project reads DESIGN.md before visual work.
"""
import argparse
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS = os.path.join(REPO, "tokens", "design-tokens.json")
TEMPLATE = os.path.join(REPO, "tokens", "DESIGN.template.md")
CONTRACT = ["bg", "bg-gradient", "label-1", "label-2", "label-3", "accent", "accent-glow",
            "fill-1", "fill-2", "sep", "glass-bg", "glass-bdr", "glass-shd"]
LINK_BEGIN = "<!-- sj-design:DESIGN.md begin -->"
LINK_END = "<!-- sj-design:DESIGN.md end -->"


def load_tokens():
    with open(TOKENS) as fh:
        return json.load(fh)


def theme_values(tokens, name):
    theme = tokens["theme"].get(name)
    if theme is None:
        raise SystemExit("unknown theme %r; choose from: %s" % (name, ", ".join(tokens["theme"])))
    missing = [k for k in CONTRACT if k not in theme]
    if missing:
        raise SystemExit("theme %r is missing contract tokens: %s" % (name, missing))
    return {k: theme[k]["$value"] for k in CONTRACT}, theme.get("$description", "")


def luminance(hex_color):
    m = re.fullmatch(r"#([0-9a-fA-F]{6})", hex_color.strip())
    if not m:
        return None
    r, g, b = (int(m.group(1)[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def mode(values):
    lum = luminance(values["bg"])
    return "unknown" if lum is None else ("light" if lum > 0.5 else "dark")


def source_rev():
    try:
        out = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
        return out.stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def parse_root_vars(css_text):
    """All custom properties declared in :root blocks, in order, comments stripped."""
    text = re.sub(r"/\*.*?\*/", "", css_text, flags=re.S)
    found = {}
    for block in re.finditer(r":root\s*\{(.*?)\}", text, re.S):
        for m in re.finditer(r"--([A-Za-z0-9-]+)\s*:\s*(.*?);", block.group(1), re.S):
            found[m.group(1)] = " ".join(m.group(2).split())
    return found


def shadow_layers(value):
    """Count top-level comma-separated layers (commas inside rgba() don't count)."""
    depth, layers = 0, 1
    for ch in value:
        depth += ch == "("
        depth -= ch == ")"
        layers += ch == "," and depth == 0
    return layers


def divergences(project_vars):
    """Human-readable differences between a project's live tokens and the 13-name contract."""
    notes = []
    have = [k for k in CONTRACT if k in project_vars]
    missing = [k for k in CONTRACT if k not in project_vars]
    extra = [k for k in project_vars if k not in CONTRACT and not k.startswith("font")]
    notes.append("- Contract coverage: %d of 13 names" % len(have))
    if missing:
        notes.append("- Contract names this project does not declare: %s"
                     % ", ".join("`--%s`" % k for k in missing))
    if extra:
        notes.append("- Project-specific names: %s" % ", ".join("`--%s`" % k for k in extra))
    if "glass-shd" in project_vars:
        n = shadow_layers(project_vars["glass-shd"])
        if n != 5:
            notes.append("- `--glass-shd` has %d layer%s (contract recipe: 5)" % (n, "" if n == 1 else "s"))
    return notes


def render(theme, from_css=None):
    tokens = load_tokens()
    values, desc = theme_values(tokens, theme)
    with open(TEMPLATE) as fh:
        tpl = fh.read()
    theme_css = "\n".join("  --%s: %s;" % (k, values[k]) for k in CONTRACT)
    if from_css is None:
        project_line = "**Project theme:** `%s` (%s) — %s" % (theme, mode(values), desc or "no description")
        token_block = "```css\n:root, [data-theme=\"%s\"] {\n%s\n}\n```" % (theme, theme_css)
        div = ""
    else:
        with open(from_css) as fh:
            pvars = parse_root_vars(fh.read())
        src = os.path.basename(os.path.dirname(os.path.abspath(from_css))) + "/" + os.path.basename(from_css)
        project_line = ("**Project palette:** this project's own, live in `%s`. It is not one of the 17 deck "
                        "themes. Its tokens below are the truth for this repo." % src)
        if pvars:
            token_block = ("Live tokens from `%s` (re-run the generator after changing them):\n\n```css\n:root {\n%s\n}\n```"
                           % (src, "\n".join("  --%s: %s;" % kv for kv in pvars.items())))
            div = ("\n### This project's divergences from the contract\n\n" + "\n".join(divergences(pvars)) +
                   "\n\nThese are the project's current, shipped state. Use the project's own names and values. "
                   "Do not \"fix\" them toward the contract (or apply a slop tell that contradicts them) unless "
                   "asked. New shared components should still use the contract names.\n")
        else:
            project_line = ("**Project palette:** not tokenized yet. `%s` declares no `:root` custom properties; "
                            "colors live inline or in shaders." % src)
            token_block = ("No `:root` token block in `%s`: this project's palette lives inline or in shaders. "
                           "When adding CSS, adopt the 13-name contract. Which theme's values to use is a design "
                           "decision, so ask rather than picking one." % src)
            div = ""
    font_rows = "\n".join("| `--font%s` | `%s` |" % ("" if k == "sans" else "-" + k, v["$value"])
                          for k, v in tokens["font"].items() if not k.startswith("$"))
    rows = []
    for name, t in tokens["theme"].items():
        if name.startswith("$"):
            continue
        tv, _ = theme_values(tokens, name)
        rows.append("| `%s`%s | %s | `%s` | `%s` |" % (name, " (this project)" if name == theme and not from_css else "",
                                                     mode(tv), tv["bg"], tv["accent"]))
    notice = ("GENERATED by sj-design/scripts/build_design_md.py from tokens/design-tokens.json @ %s. "
              "Do not edit; re-run the script to refresh." % source_rev())
    out = tpl
    for key, val in (("GENERATED_NOTICE", notice), ("PROJECT_LINE", project_line), ("TOKEN_BLOCK", token_block),
                     ("DIVERGENCES", div), ("FONT_ROWS", font_rows), ("THEME_ROWS", "\n".join(rows))):
        out = out.replace("{{%s}}" % key, val)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", out)
    if leftover:
        raise SystemExit("unfilled placeholders: %s" % leftover)
    return out, (values if from_css is None else None)


def verify(text, values):
    """The emitted CSS block must carry every contract token with its exact JSON value."""
    if values is None:  # --from-css: values are the project's own, copied verbatim
        return
    for k in CONTRACT:
        line = "  --%s: %s;" % (k, values[k])
        if line not in text:
            raise SystemExit("verify failed: %s missing or altered" % k)


def link(project_dir):
    path = os.path.join(project_dir, "CLAUDE.md")
    block = (LINK_BEGIN + "\n## Visual design\n\nBefore any UI, styling, deck, or motion work, read "
             "`DESIGN.md` in this repo (the Studio Joe visual system: tokens, glass, type, motion, copy, "
             "slop tells). For anything it doesn't cover, invoke the `sj-design-expert` skill.\n" + LINK_END)
    existing = open(path).read() if os.path.exists(path) else ""
    if LINK_BEGIN in existing:
        new = re.sub(re.escape(LINK_BEGIN) + r".*?" + re.escape(LINK_END), block, existing, flags=re.S)
    else:
        new = existing.rstrip("\n") + ("\n\n" if existing else "") + block + "\n"
    if new != existing:
        with open(path, "w") as fh:
            fh.write(new)
        return "updated"
    return "unchanged"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--theme", default="dark")
    ap.add_argument("--out", default=os.path.join(REPO, "DESIGN.md"))
    ap.add_argument("--from-css", help="use this project's own :root tokens (live file) instead of a deck theme")
    ap.add_argument("--link", action="store_true", help="add a DESIGN.md pointer to the target project's CLAUDE.md")
    a = ap.parse_args(argv)
    text, values = render(a.theme, from_css=a.from_css)
    verify(text, values)
    out = os.path.abspath(os.path.expanduser(a.out))
    with open(out, "w") as fh:
        fh.write(text)
    msg = "wrote %s (%s, %d chars)" % (out, ("tokens from " + a.from_css) if a.from_css else "theme " + a.theme, len(text))
    if a.link:
        msg += "; CLAUDE.md pointer %s" % link(os.path.dirname(out))
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
