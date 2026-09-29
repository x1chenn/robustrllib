#!/usr/bin/env python
"""Keep the landing page's algorithm table in step with data/algorithms.yaml.

    python tools/sync_landing.py

Rewrites the block between the `algo-table` markers in ../index.html. The table is
the paper's structural comparison: robust methods only, one row per method, every
method name linking to its documentation page.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

SRC = Path(__file__).resolve().parents[1]
LANDING = SRC.parent / "index.html"
START, END = "<!-- algo-table:start -->", "<!-- algo-table:end -->"

CLAIMED = {"dynamic": "Dynamic", "observation": "Observation", "semantics": "Semantics"}
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


def tick(flag):
    return '<td class="c tick">✓</td>' if flag else '<td class="c"></td>'


def table(spec):
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
                head = (f'<td rowspan="{len(members)}" style="white-space:nowrap">{fam_label}</td>'
                        if i == 0 else "")
                rows.append(
                    f'      <tr>{head}<td style="white-space:nowrap"><a href="docs/algorithms/{GROUP[a["regime"]]}/{a["slug"]}/"><b>{a["name"]}</b></a></td>'
                    f'<td>{CLAIMED[a["claimed"]]}</td><td>{a["base"]}</td>'
                    f'{tick(t["rollout"])}{tick(t["adversary"])}{tick(t["model"])}</tr>')
    rows += ["    </tbody>", "  </table>", "</div>",
             '<p class="tbl-note">',
             "  <b>Structural comparison of the robust methods in the library.</b>",
             "  <em>Shifted-env rollout</em> marks rollouts collected from a deliberately perturbed",
             "  environment; <em>adversarial network</em> marks a learned adversary optimised against the",
             "  policy; <em>learned model</em> marks a trained next-state predictor used by the robustness",
             "  mechanism; <em>claimed robustness</em> records the intended shift target. The six standard",
             '  references are documented with the other methods on the',
             '  <a href="docs/algorithms/">algorithm pages</a>.',
             "</p>"]
    return "\n".join("    " + r for r in rows)


def main():
    spec = yaml.safe_load(open(SRC / "data" / "algorithms.yaml"))
    html = LANDING.read_text()
    block = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not block.search(html):
        sys.exit(f"markers {START} ... {END} not found in {LANDING.name}")
    LANDING.write_text(block.sub(lambda _m: f"{START}\n{table(spec)}\n    {END}", html))
    print(f"synced algorithm table in {LANDING.name}")


if __name__ == "__main__":
    main()
