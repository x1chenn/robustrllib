#!/usr/bin/env python
"""Keep the landing page's algorithm book in step with data/algorithms.yaml.

    python tools/sync_landing.py

Rewrites the block between the `algo-book` markers in ../index.html. The book is the
one of the All Methods page: the same generator writes it, and the same Markdown
extensions as in mkdocs.yml turn it into HTML. Only the addresses differ, because the
landing page sits one directory above the documentation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import markdown
import yaml

SRC = Path(__file__).resolve().parents[1]
LANDING = SRC.parent / "index.html"
START, END = "<!-- algo-book:start -->", "<!-- algo-book:end -->"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_algorithms import book  # noqa: E402


def extensions():
    """The Markdown extensions of the documentation, as (names, configurations)."""
    names, configs = [], {}
    for item in yaml.safe_load(open(SRC / "mkdocs.yml"))["markdown_extensions"]:
        if isinstance(item, dict):
            (name, config), = item.items()
            configs[name] = config or {}
        else:
            name = item
        if name != "toc":           # the book has no headings; permalinks are for pages
            names.append(name)
        else:
            configs.pop(name, None)
    return names, configs


def book_html(spec, refs):
    text = "\n".join(book(spec, refs, script=None,
                          page=lambda group, slug: f"docs/algorithms/{group}/{slug}/"))
    names, configs = extensions()
    html = markdown.markdown(text, extensions=names, extension_configs=configs)
    if "markdown=" in html or "```" in html:
        sys.exit("the book was not fully converted to HTML")
    return html


def main():
    spec = yaml.safe_load(open(SRC / "data" / "algorithms.yaml"))
    refs = yaml.safe_load(open(SRC / "data" / "references.yaml"))
    html = LANDING.read_text()
    block = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not block.search(html):
        sys.exit(f"markers {START} ... {END} not found in {LANDING.name}")
    # Not indented: the book holds <pre> blocks, where leading spaces would show.
    LANDING.write_text(block.sub(lambda _m: f"{START}\n{book_html(spec, refs)}\n{END}", html))
    print(f"synced algorithm book in {LANDING.name}")


if __name__ == "__main__":
    main()
