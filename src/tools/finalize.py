#!/usr/bin/env python
"""Make the built documentation reproducible.

    python tools/finalize.py

Two things in the generator's output change with the clock and nothing else: the
build-date comment at the end of the home page, and the sitemap with its
last-modified dates. Both are removed, so that a rebuild of unchanged sources
gives byte-identical files and a commit shows only real changes. The pages ask
not to be indexed, so the sitemap has no reader.
"""
from __future__ import annotations

import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[2] / "docs"


def main():
    home = DOCS / "index.html"
    html = home.read_text()
    cleaned = re.sub(r"\n*<!--\s*MkDocs version.*?-->\s*$", "\n", html, flags=re.S)
    if cleaned != html:
        home.write_text(cleaned)
    for name in ("sitemap.xml", "sitemap.xml.gz"):
        (DOCS / name).unlink(missing_ok=True)
    print("finalized: build date and sitemap removed")


if __name__ == "__main__":
    main()
