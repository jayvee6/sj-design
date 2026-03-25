#!/usr/bin/env python3
"""
Build a self-contained HTML presentation from a JSON spec.

Usage:
  python3 build_presentation.py spec.json
  python3 build_presentation.py spec.json -o ~/Desktop/my-deck.html
  cat spec.json | python3 build_presentation.py
  echo '{"title":"Demo","slides":[...]}' | python3 build_presentation.py
"""

import json
import sys
import re
import argparse
from pathlib import Path
from urllib.parse import urlparse, parse_qs

SCRIPT_DIR = Path(__file__).parent
TEMPLATE_PATH = SCRIPT_DIR.parent / "assets" / "template.html"


# ── YouTube helpers ────────────────────────────────────────────────────────────

def youtube_to_embed(url: str) -> str:
    """Convert any YouTube URL variant to an embed URL."""
    parsed = urlparse(url)
    video_id = None
    if parsed.hostname in ("youtu.be",):
        video_id = parsed.path.lstrip("/").split("?")[0]
    elif parsed.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/")[1].split("?")[0]
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/")[1].split("?")[0]
        else:
            qs = parse_qs(parsed.query)
            video_id = qs.get("v", [None])[0]
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
    return url


def detect_media_type(src: str) -> str:
    """Auto-detect media type from URL."""
    if not src:
        return "image"
    s = src.lower().split("?")[0]
    if "youtube.com" in s or "youtu.be" in s:
        return "youtube"
    if s.endswith((".mp4", ".webm", ".ogg", ".mov")):
        return "video"
    return "image"


# ── Slide renderers ────────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    """Minimal HTML escaping for text content."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_slide(slide: dict, index: int) -> str:
    slide_type = slide.get("type", "content")
    active_class = " active" if index == 0 else ""
    dispatch = {
        "title": _render_title,
        "content": _render_content,
        "quote": _render_quote,
        "two-column": _render_two_column,
        "media": _render_media,
        "closing": _render_closing,
    }
    renderer = dispatch.get(slide_type, _render_content)
    inner = renderer(slide)
    return f'<div class="slide slide-{slide_type}{active_class}" data-index="{index}">{inner}\n</div>'


def _eyebrow(slide: dict) -> str:
    v = slide.get("eyebrow", "")
    return f'<p class="eyebrow">{_esc(v)}</p>' if v else ""


def _render_title(slide: dict) -> str:
    icon = f'<p class="slide-icon">{slide["icon"]}</p>' if slide.get("icon") else ""
    sub = f'<p class="subheading">{_esc(slide["subheading"])}</p>' if slide.get("subheading") else ""
    return f"""
  <div class="slide-inner slide-inner--center">
    {icon}
    {_eyebrow(slide)}
    <h1 class="headline">{_esc(slide.get("heading", ""))}</h1>
    {sub}
  </div>"""


def _render_content(slide: dict) -> str:
    bullets = slide.get("bullets", [])
    items = "".join(f"<li>{_esc(b)}</li>" for b in bullets)
    bullets_html = f'<ul class="bullets">{items}</ul>' if bullets else ""
    note = f'<p class="slide-note">{_esc(slide["note"])}</p>' if slide.get("note") else ""
    return f"""
  <div class="slide-inner">
    {_eyebrow(slide)}
    <h2 class="headline">{_esc(slide.get("heading", ""))}</h2>
    {bullets_html}
    {note}
  </div>"""


def _render_quote(slide: dict) -> str:
    icon = f'<p class="slide-icon">{slide["icon"]}</p>' if slide.get("icon") else ""
    eyebrow = _eyebrow(slide)
    if not eyebrow and slide.get("heading"):
        eyebrow = f'<p class="eyebrow">{_esc(slide["heading"])}</p>'
    attr = f'<cite>&#8212;&nbsp;{_esc(slide["attribution"])}</cite>' if slide.get("attribution") else ""
    return f"""
  <div class="slide-inner slide-inner--center slide-inner--quote">
    <span class="quote-watermark">&ldquo;</span>
    {icon}
    {eyebrow}
    <blockquote>{_esc(slide.get("quote", ""))}</blockquote>
    {attr}
  </div>"""


def _render_two_column(slide: dict) -> str:
    def col(data: dict) -> str:
        title = f'<h3 class="col-title">{_esc(data.get("title", ""))}</h3>' if data.get("title") else ""
        items = data.get("items", data.get("bullets", []))
        text = data.get("text", "")
        lis = "".join(f"<li>{_esc(i)}</li>" for i in items)
        list_html = f'<ul class="bullets">{lis}</ul>' if lis else ""
        text_html = f'<p class="col-text">{_esc(text)}</p>' if text else ""
        return f'<div class="col">{title}{list_html}{text_html}</div>'

    left = slide.get("left", {})
    right = slide.get("right", {})
    return f"""
  <div class="slide-inner">
    {_eyebrow(slide)}
    <h2 class="headline">{_esc(slide.get("heading", ""))}</h2>
    <div class="two-col">{col(left)}{col(right)}</div>
  </div>"""


def _render_media(slide: dict) -> str:
    src = slide.get("src", "")
    media_type = slide.get("media_type", "auto")
    if media_type == "auto":
        media_type = detect_media_type(src)

    if media_type == "youtube":
        embed = youtube_to_embed(src)
        media_html = (
            f'<iframe src="{embed}" frameborder="0" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
            f'gyroscope; picture-in-picture" allowfullscreen></iframe>'
        )
    elif media_type == "video":
        media_html = f'<video src="{src}" controls></video>'
    else:
        alt = _esc(slide.get("caption", ""))
        media_html = f'<img src="{src}" alt="{alt}" loading="lazy">'

    heading = f'<h2 class="headline media-heading">{_esc(slide["heading"])}</h2>' if slide.get("heading") else ""
    caption = f'<p class="media-caption">{_esc(slide["caption"])}</p>' if slide.get("caption") else ""
    return f"""
  <div class="slide-inner slide-inner--center slide-inner--media">
    {heading}
    <div class="media-frame">{media_html}</div>
    {caption}
  </div>"""


def _render_closing(slide: dict) -> str:
    cta = f'<p class="cta">{_esc(slide["cta"])}</p>' if slide.get("cta") else ""
    contact = f'<p class="contact">{_esc(slide["contact"])}</p>' if slide.get("contact") else ""
    return f"""
  <div class="slide-inner slide-inner--center">
    <h1 class="headline closing-headline">{_esc(slide.get("heading", ""))}</h1>
    {cta}
    {contact}
  </div>"""


# ── Builder ────────────────────────────────────────────────────────────────────

def build(spec: dict, output_path: str) -> None:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Template not found: {TEMPLATE_PATH}\n"
            f"Make sure assets/template.html is in the skill directory."
        )

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    slides = spec.get("slides", [])
    if not slides:
        raise ValueError("Spec has no slides.")

    slides_html = "\n".join(render_slide(s, i) for i, s in enumerate(slides))
    title = spec.get("title", "Presentation")
    theme = spec.get("theme", "dark")
    slide_count = len(slides)

    html = template
    html = html.replace("{{TITLE}}", _esc(title))
    html = html.replace("{{THEME}}", theme if theme in ("dark", "light") else "dark")
    html = html.replace("{{SLIDES}}", slides_html)
    html = html.replace("{{SLIDE_COUNT}}", str(slide_count))

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"✓ Generated: {out.resolve()}")


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s[:60] or "presentation"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an HTML presentation from a JSON spec.")
    parser.add_argument("spec", nargs="?", help="Path to JSON spec file (omit to read from stdin)")
    parser.add_argument("-o", "--output", help="Output .html path (default: /tmp/<title>.html)")
    args = parser.parse_args()

    if args.spec and args.spec != "-":
        raw = Path(args.spec).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    spec = json.loads(raw)

    output = args.output or f"/tmp/{slugify(spec.get('title', 'presentation'))}.html"
    build(spec, output)


if __name__ == "__main__":
    main()
