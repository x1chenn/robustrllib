#!/usr/bin/env python
"""Keep the landing page's algorithm book and table in step with data/algorithms.yaml.

    python tools/sync_landing.py

Rewrites two blocks of ../index.html: between the `algo-book` markers, the book of the
All Methods page (the same generator writes it, and the same Markdown extensions as in
mkdocs.yml turn it into HTML; only the addresses differ, because the landing page sits
one directory above the documentation), and between the `algo-table` markers, the
paper's structural comparison of the robust methods, one row per method.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import markdown
import yaml

SRC = Path(__file__).resolve().parents[1]
LANDING = SRC.parent / "index.html"
BOOK = ("<!-- algo-book:start -->", "<!-- algo-book:end -->")
TABLE = ("<!-- algo-table:start -->", "<!-- algo-table:end -->")

CLAIMED = {"dynamic": "Dynamic shift", "observation": "Observation shift", "semantics": "Semantic shift"}
# The table holds robust methods only, so the group follows from the setting.
GROUP = {"offline": "robust-offline", "online": "robust-online", "safe": "robust-safe"}
GROUPS = [
    ("offline", "Robust Offline", "learns from a fixed dataset without environment interaction",
     [("learner", "Learner-centric"), ("data", "Data-centric"), ("generative", "Data-centric · generative")]),
    ("online", "Robust Online", "learns through continued environment interaction",
     [("learner", "Learner-centric"), ("environment", "Environment-centric")]),
    ("safe", "Robust Safe", "adds a cost constraint that must hold under shift",
     [("safe", "Robust safe")]),
]

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


def tick(flag):
    return '<td class="c tick">✓</td>' if flag else '<td class="c"></td>'


def table_html(spec):
    rows = ['<div class="table-scroll">', '  <table class="data">', "    <thead>", "      <tr>",
            "        <th>Family</th><th>Method</th><th>Claimed<br>robustness</th><th>Base<br>algorithm</th>",
            '        <th class="c">Shifted-env<br>rollout</th><th class="c">Adversarial<br>network</th>'
            '<th class="c">Learned<br>model</th>',
            "      </tr>", "    </thead>", "    <tbody>"]
    for regime, label, blurb, families in GROUPS:
        rows.append(f'      <tr class="grp"><td colspan="7">{label} — {blurb}</td></tr>')
        for fam, fam_label in families:
            members = [a for a in spec["algorithms"]
                       if a["regime"] == regime and a["family"] == fam]
            for i, a in enumerate(members):
                t = a["traits"]
                head = (f'<td rowspan="{len(members)}" class="nw">{fam_label}</td>' if i == 0 else "")
                rows.append(
                    f'      <tr>{head}<td class="nw"><a href="docs/algorithms/{GROUP[a["regime"]]}/{a["slug"]}/"><b>{a["name"]}</b></a></td>'
                    f'<td>{CLAIMED[a["claimed"]]}</td><td>{a["base"]}</td>'
                    f'{tick(t["rollout"])}{tick(t["adversary"])}{tick(t["model"])}</tr>')
    rows += ["    </tbody>", "  </table>", "</div>",
             '<p class="tbl-note">',
             "  <em>Shifted-env rollout</em>: rollouts collected from a deliberately perturbed environment.",
             "  <em>Adversarial network</em>: a learned adversary optimised against the policy.",
             "  <em>Learned model</em>: a trained next-state predictor used by the robustness mechanism.",
             "  The six standard references are on the <a href=\"docs/algorithms/\">algorithm pages</a>.",
             "</p>"]
    return "\n".join("    " + r for r in rows)


def replace(html, markers, body):
    start, end = markers
    block = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not block.search(html):
        sys.exit(f"markers {start} ... {end} not found in {LANDING.name}")
    return block.sub(lambda _m: f"{start}\n{body}\n{end}", html)


def main():
    spec = yaml.safe_load(open(SRC / "data" / "algorithms.yaml"))
    refs = yaml.safe_load(open(SRC / "data" / "references.yaml"))
    html = LANDING.read_text()
    # The book is not indented: it holds <pre> blocks, where leading spaces would show.
    html = replace(html, BOOK, book_html(spec, refs))
    html = replace(html, TABLE, table_html(spec))
    LANDING.write_text(html)
    print(f"synced algorithm book and table in {LANDING.name}")


if __name__ == "__main__":
    main()
