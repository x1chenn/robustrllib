#!/usr/bin/env python
"""Keep the generated blocks of the landing page in step with the data files.

    python tools/sync_landing.py

Rewrites four blocks of ../index.html, each between a pair of HTML comment markers:

    algo-table    the table of robust methods by family, from data/algorithms.yaml
    shift-table   the six shift sources with their targets and mode names, from data/shifts.yaml
    task-cards    the task cards with their renders and filters, from data/tasks.yaml
    results-data  the leaderboard data as JSON, from data/results/*.csv (gen_results.py)

Everything else on the page is written by hand. The page has no script other than
results.js, which draws the leaderboard from the JSON block.
"""
from __future__ import annotations

import html as htmlmod
import json
import re
import sys
from pathlib import Path

import yaml

SRC = Path(__file__).resolve().parents[1]
LANDING = SRC.parent / "index.html"
TABLE = ("<!-- algo-table:start -->", "<!-- algo-table:end -->")
SHIFTS = ("<!-- shift-table:start -->", "<!-- shift-table:end -->")
TASKS = ("<!-- task-cards:start -->", "<!-- task-cards:end -->")
RESULTS = ("<!-- results-data:start -->", "<!-- results-data:end -->")

CLAIMED = {"dynamic": "Dynamic shift", "observation": "Observation shift", "semantics": "Semantic shift"}
# The table holds robust methods only, so the group follows from the setting.
GROUP = {"offline": "robust-offline", "online": "robust-online", "safe": "robust-safe"}
# (regime, group label, blurb, [(family key, family label, colour token)])
GROUPS = [
    ("online", "Robust online", "learns through continued environment interaction",
     [("learner", "Learner-centric", "learner-on"), ("environment", "Environment-centric", "env")]),
    ("offline", "Robust offline", "learns from a fixed dataset without environment interaction",
     [("learner", "Learner-centric", "learner-off"), ("data", "Data-centric", "data"),
      ("generative", "Data-centric · generative", "generative")]),
    ("safe", "Robust safe", "adds a cost constraint that must hold under shift",
     [("safe", "Robust safe", "safe")]),
]

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_results  # noqa: E402


def esc(text):
    return htmlmod.escape(str(text), quote=True)


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
        for fam, fam_label, colour in families:
            members = [a for a in spec["algorithms"]
                       if a["regime"] == regime and a["family"] == fam]
            for i, a in enumerate(members):
                t = a["traits"]
                head = (f'<td rowspan="{len(members)}" class="nw"><i class="chip chip-{colour}"></i>{fam_label}</td>'
                        if i == 0 else "")
                rows.append(
                    f'      <tr>{head}<td class="nw"><a href="docs/algorithms/{GROUP[a["regime"]]}/{a["slug"]}/">{a["name"]}</a></td>'
                    f'<td>{CLAIMED[a["claimed"]]}</td><td>{a["base"]}</td>'
                    f'{tick(t["rollout"])}{tick(t["adversary"])}{tick(t["model"])}</tr>')
    rows += ["    </tbody>", "  </table>", "</div>",
             '<p class="note">',
             "  <em>Shifted-env rollout</em>: rollouts collected from a deliberately perturbed environment.",
             "  <em>Adversarial network</em>: a learned adversary optimised against the policy.",
             "  <em>Learned model</em>: a trained next-state predictor used by the robustness mechanism.",
             "  The six standard references (IQL, TD3+BC, MOPO, SynthER, PPO, SAC) are on the "
             '<a href="docs/algorithms/">algorithm pages</a>.',
             "</p>"]
    return "\n".join("    " + r for r in rows)


def shifts_html(data):
    """One row per shift source: what it perturbs, the targets in code, the mode names."""
    rows = ['<div class="table-scroll">', '  <table class="data">', "    <thead>",
            "      <tr><th>Shift source</th><th>What it perturbs</th><th>Target</th><th>Mode names</th></tr>",
            "    </thead>", "    <tbody>"]
    targets = {"dynamic": "dynamics, transition", "observation": "observation", "action": "action",
               "reward-cost": "reward, cost", "latency": "latency", "semantic": "appearance"}
    for s in data["sources"]:
        names = []
        for mode in ("stochastic", "adversarial", "parametric"):
            entry = s["modes"].get(mode) or {}
            names += entry.get("names", [])
        seen, uniq = set(), []
        for n in names:
            if n not in seen:
                seen.add(n); uniq.append(n)
        codes = " ".join(f"<code>{esc(n)}</code>" for n in uniq)
        rows.append(f'      <tr><td class="nw"><i class="chip chip-src-{esc(s["key"])}"></i>'
                    f'<a href="{esc(s["page"])}">{esc(s["name"])}</a></td>'
                    f'<td>{esc(s["blurb"])}</td><td class="nw"><code>{esc(targets[s["key"]])}</code></td><td>{codes}</td></tr>')
    rows += ["    </tbody>", "  </table>", "</div>"]
    return "\n".join("    " + r for r in rows)


FAMILIES = ["Locomotion", "Manipulation", "Navigation", "Vehicle control", "Humanoid", "Vision-language-action"]


def task_card(task, sources):
    media = task["media"]
    if media.endswith((".mp4", ".webm")):
        poster = f' poster="{esc(task["poster"])}"' if task.get("poster") else ""
        fig = (f'<video src="{esc(media)}"{poster} autoplay muted loop playsinline preload="metadata" '
               f'aria-label="{esc(task["caption"])}"></video>')
    else:
        fig = f'<img src="{esc(media)}" alt="{esc(task["caption"])}" loading="lazy">'
    names = {s["key"]: s["name"] for s in sources}
    dots = "".join(f'<i class="dot dot-{k}" title="{esc(names[k])}"></i>' for k in task["shifts"])
    return (f'<article class="task" data-family="{esc(task["family"])}" data-regime="{esc(" ".join(task["regime"]))}">'
            f'<figure class="task-media">{fig}</figure>'
            f'<h4>{esc(task["name"])}</h4>'
            f'<p class="task-meta">{esc(task["family"])} · {esc(task["backend"])} · {esc(" / ".join(task["regime"]))}</p>'
            f'<p class="task-axes">{esc(", ".join(task["axes"]))}</p>'
            f'<p class="task-dots">{dots}</p>'
            f'</article>')


def tasks_html(tasks, sources):
    """The task cards with their looping renders, and two rows of filter buttons."""
    out = ['<div class="tasks" id="tasks">',
           '  <div class="filters">',
           '    <div class="filter-row"><span class="filter-label">Family</span><div class="filter-buttons" role="group" aria-label="Task family">',
           '      <button type="button" class="fbtn is-active" data-family="all">All</button>']
    for f in FAMILIES:
        out.append(f'      <button type="button" class="fbtn" data-family="{esc(f)}">{esc(f)}</button>')
    out.append('    </div></div>')
    out.append('    <div class="filter-row"><span class="filter-label">Regime</span><div class="filter-buttons" role="group" aria-label="Regime">')
    for key, label in (("all", "All"), ("online", "Online"), ("offline", "Offline")):
        out.append(f'      <button type="button" class="fbtn{" is-active" if key == "all" else ""}" data-regime="{key}">{label}</button>')
    out.append('    </div></div>')
    out.append('  </div>')
    out.append('  <div class="task-grid">')
    out.extend("    " + task_card(t, sources) for t in tasks)
    out.append('  </div>')
    out.append('  <p class="task-empty" hidden>No task matches this filter.</p>')
    legend = "".join(f'<li><i class="dot dot-{esc(s["key"])}"></i>{esc(s["name"])}</li>' for s in sources)
    out.append(f'  <ul class="legend task-legend">{legend}</ul>')
    out.append('</div>')
    return "\n".join("    " + line for line in out)


def replace(html, markers, body):
    start, end = markers
    block = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not block.search(html):
        sys.exit(f"markers {start} ... {end} not found in {LANDING.name}")
    return block.sub(lambda _m: f"{start}\n{body}\n{end}", html)


def main():
    spec = yaml.safe_load(open(SRC / "data" / "algorithms.yaml"))
    html = LANDING.read_text()
    html = replace(html, TABLE, table_html(spec))
    shifts = yaml.safe_load(open(SRC / "data" / "shifts.yaml"))
    html = replace(html, SHIFTS, shifts_html(shifts))
    tasks = yaml.safe_load(open(SRC / "data" / "tasks.yaml"))["tasks"]
    html = replace(html, TASKS, tasks_html(tasks, shifts["sources"]))
    results = gen_results.build()
    print(gen_results.check(results))
    payload = json.dumps(results, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = replace(html, RESULTS, '<script type="application/json" id="results-data">' + payload + "</script>")
    LANDING.write_text(html)
    print(f"synced algorithm table, shift table, task table and results in {LANDING.name}")


if __name__ == "__main__":
    main()
