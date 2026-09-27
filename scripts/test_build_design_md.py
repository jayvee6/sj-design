import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_design_md as b  # noqa: E402


class Render(unittest.TestCase):
    def test_every_theme_renders_with_exact_token_values(self):
        tokens = b.load_tokens()
        for name in (k for k in tokens["theme"] if not k.startswith("$")):
            text, values = b.render(name)
            b.verify(text, values)
            for k in b.CONTRACT:
                self.assertEqual(values[k], tokens["theme"][name][k]["$value"])
            self.assertNotIn("{{", text)
            self.assertIn("`%s` (this project)" % name, text)

    def test_modes(self):
        self.assertEqual(b.mode(b.theme_values(b.load_tokens(), "dark")[0]), "dark")
        self.assertEqual(b.mode(b.theme_values(b.load_tokens(), "golden-hour")[0]), "light")

    def test_unknown_theme_fails_loudly(self):
        with self.assertRaises(SystemExit):
            b.render("not-a-theme")

    def test_verify_catches_tampering(self):
        text, values = b.render("dark")
        with self.assertRaises(SystemExit):
            b.verify(text.replace(values["accent"], "#123456"), values)


PROJECT_CSS = """
:root {
  /* comment */ --bg: #060608;
  --bg-g: radial-gradient(ellipse at 50% 0%, #122 0%, #060608 100%);
  --label-1: rgba(255,255,255,0.92);
  --accent: #2DD4BF;
  --accent-bg: rgba(45,212,191,0.12);
  --glass-shd: 0 8px 40px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08);
}
"""


class FromCss(unittest.TestCase):
    def render_css(self, css):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "site.css")
            with open(p, "w") as fh:
                fh.write(css)
            return b.render("dark", from_css=p)

    def test_project_tokens_verbatim_and_divergences(self):
        text, values = self.render_css(PROJECT_CSS)
        self.assertIsNone(values)
        self.assertIn("--accent: #2DD4BF;", text)
        self.assertNotIn("--accent: #0A84FF;", text)          # no deck-theme values leak in
        self.assertIn("Contract coverage: 4 of 13", text)
        self.assertIn("`--bg-gradient`", text)                 # reported missing
        self.assertIn("`--bg-g`", text)                        # reported as project-specific
        self.assertIn("has 2 layers (contract recipe: 5)", text)
        self.assertIn("Do not \"fix\" them", text)
        self.assertNotIn("(this project)", text)

    def test_no_root_block(self):
        text, _ = self.render_css("body { color: red; }")
        self.assertIn("No `:root` token block", text)
        self.assertIn("not tokenized yet", text)
        self.assertNotIn("are the truth for this repo", text)
        self.assertNotIn("divergences from the contract", text)

    def test_shadow_layers_ignores_commas_in_parens(self):
        self.assertEqual(b.shadow_layers("0 1px rgba(0,0,0,.5), inset 0 1px 0 rgba(1,2,3,.4)"), 2)


class Link(unittest.TestCase):
    def test_link_is_idempotent_and_preserves_existing(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "CLAUDE.md")
            with open(p, "w") as fh:
                fh.write("# Project\n\nExisting rules.\n")
            self.assertEqual(b.link(d), "updated")
            self.assertEqual(b.link(d), "unchanged")
            body = open(p).read()
            self.assertTrue(body.startswith("# Project\n\nExisting rules.\n"))
            self.assertEqual(body.count(b.LINK_BEGIN), 1)

    def test_link_creates_claude_md_when_absent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(b.link(d), "updated")
            self.assertIn("DESIGN.md", open(os.path.join(d, "CLAUDE.md")).read())


if __name__ == "__main__":
    unittest.main()
