# Third-Party Notices

This project includes copies of the following third-party software, each the
property of its respective author(s) and used under the terms of its own
license. This is in addition to the project's own MIT `LICENSE`.

## LiquidGlass

- **Author:** ybouane
- **License:** MIT
- **Source:** https://github.com/ybouane/liquidglass
- **Bundled at:** `lib/liquidglass.js` (minified/built bundle)
- **Used for:** liquid-glass refraction / blur / chromatic-aberration UI effect.
- **Note:** This bundle transitively includes **html-to-image**
  (author: bubkoo, MIT — https://github.com/bubkoo/html-to-image), used to
  rasterize non-glass children via SVG `foreignObject`.

## Bundled fonts

Open-source fonts (EB Garamond, Inter, JetBrains Mono) are documented and
licensed separately under `fonts/README.md` and `fonts/OFL.txt`.

---

## First-party code (not third-party)

`lib/canvas-size.js`, `lib/envelopes.js`, `lib/synthetic-pulse.js`, and
`lib/webgpu-bootstrap.js` are this author's own code, covered by this
repository's `LICENSE`.
