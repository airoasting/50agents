"""For PPT cases, fetch the slide_library template HTML and inject BLACK content.

Strategy:
1. Pull template HTML from index.json url field.
2. Parse with BeautifulSoup, locate the slide content container (the
   slide_library convention is a wrapping element with class 'slides' or a
   data-role='slides' attribute).
3. Replace inner content with BLACK output Markdown converted to HTML slides.
4. Write the merged HTML to output.html.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class SlideTemplate:
    id: str
    name: str
    url: str
    color: str
    formality: str


def load_template_meta(index_json: Path, template_id: str) -> SlideTemplate:
    items = json.loads(index_json.read_text(encoding="utf-8"))
    for it in items:
        if it["id"] == template_id:
            return SlideTemplate(
                id=it["id"], name=it["name"], url=it["url"],
                color=it["color"], formality=it["formality"],
            )
    raise KeyError(f"template {template_id} not in {index_json}")


def fetch_template_html(template: SlideTemplate) -> str:
    resp = requests.get(template.url, timeout=30)
    resp.raise_for_status()
    return resp.text


def black_md_to_slide_blocks(black_md: str) -> list[str]:
    """Split BLACK Markdown by H1 (or H2 fallback) into one slide per heading."""
    sections = re.split(r"(?m)^# ", black_md)
    if len(sections) <= 1:
        sections = re.split(r"(?m)^## ", black_md)
    blocks: list[str] = []
    for s in sections:
        s = s.strip()
        if not s:
            continue
        # First line = title, rest = body.
        lines = s.split("\n", 1)
        title = lines[0].strip()
        body_md = lines[1].strip() if len(lines) > 1 else ""
        blocks.append(f"<section><h1>{_escape(title)}</h1>{_md_to_html(body_md)}</section>")
    return blocks


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _md_to_html(md: str) -> str:
    """Minimal Markdown → HTML for v0.1. Handles paragraphs, ul, headings.

    For richer rendering, swap to a real Markdown lib in v0.2.
    """
    out: list[str] = []
    in_ul = False
    for line in md.splitlines():
        stripped = line.strip()
        if not stripped:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            continue
        if stripped.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_escape(stripped[2:])}</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<p>{_escape(stripped)}</p>")
    if in_ul:
        out.append("</ul>")
    return "".join(out)


def inject_slides(template_html: str, slide_blocks: list[str]) -> str:
    soup = BeautifulSoup(template_html, "html.parser")
    container = (
        soup.select_one("[data-role='slides']")
        or soup.select_one(".slides")
        or soup.select_one(".deck")
        or soup.select_one("main")
        or soup.body
    )
    assert container is not None, "no slide container found in template"
    # Clear existing slides.
    for child in list(container.children):
        if isinstance(child, Tag):
            child.decompose()
    container.append(BeautifulSoup("".join(slide_blocks), "html.parser"))
    return str(soup)


def build(index_json: Path, template_id: str, black_md: str, output_html: Path) -> Path:
    tpl = load_template_meta(index_json, template_id)
    template_html = fetch_template_html(tpl)
    blocks = black_md_to_slide_blocks(black_md)
    merged = inject_slides(template_html, blocks)
    output_html.write_text(merged, encoding="utf-8")
    return output_html
