# RobustRLlib — Project Site (Anonymous)

Static site for the anonymous submission
*RobustRLlib: A Unified Library and Benchmark for Robust Reinforcement Learning Algorithms*.

The site has two parts that share one colour system:

| Part | URL | Source | Build |
|---|---|---|---|
| Landing page | `/` | `index.html`, `assets/` | none, hand-written |
| Documentation | `/docs/` | `src/` | MkDocs, output committed to `docs/` |

## Structure

```
├── index.html                # landing page
├── 404.html                  # BUILT: copy of the documentation's not-found page
├── assets/                   # landing page style and figures
├── docs/                     # BUILT documentation. Never edit by hand.
└── src/
    ├── mkdocs.yml            # navigation and theme (Read the Docs theme)
    ├── requirements.txt
    ├── content/              # Markdown pages
    │   ├── index.md              # documentation home
    │   ├── getting-started/      # overview, quick start
    │   ├── algorithms/
    │   │   ├── index.md          # GENERATED: all methods
    │   │   ├── standard/ robust-online/ robust-offline/ robust-safe/
    │   │   │                     # GENERATED: one overview and one page per method
    │   │   ├── run-a-method.md
    │   │   └── add-an-algorithm.md
    │   ├── shifts/
    │   │   ├── index.md          # shift sources and modes
    │   │   ├── sources/          # one page per shift source (six)
    │   │   ├── modes/            # one page per mode (five)
    │   │   └── add-a-backend.md
    │   ├── evaluation/protocol.md
    │   └── assets/               # stylesheets and figures
    ├── data/
    │   ├── algorithms.yaml   # one record per algorithm: the single source of truth
    │   ├── references.yaml   # original papers
    │   └── results/          # frozen result table that every number is computed from
    ├── theme/                # template overrides: footer, noindex
    └── tools/
        ├── gen_algorithms.py # data -> method pages and group overviews
        ├── sync_landing.py   # data -> algorithm table on the landing page
        ├── finalize.py       # makes the built output reproducible
        ├── check_site.py     # pre-publish scan
        ├── make_preview.py   # a copy of the site that opens from disk
        └── build.sh          # generate, sync, build, scan
```

## Page form

- Names follow the paper: the six shift sources are Dynamic shift, Observation shift, Action
  shift, Reward/cost shift, Latency shift and Semantic shift; the five modes are Stochastic,
  Adversarial, Parametric, Non-stationary and Composition.
- A topic page has a noun-phrase title, an opening of at most three sentences, a first
  section **At a glance** (a two-column table) and a closing list of rules. A section is one
  or two sentences followed by a code block or a table.
- No formulas. No warning or important callouts: a caveat goes into the running text with
  its key clause in bold.
- The documentation explains how to use the library. It does not discuss results. A method
  page carries two tables of numbers, the library-wide grid and its breakdown by task.

## Branches

| Branch | Holds | Updated by |
|---|---|---|
| `main` | Everything: landing page, sources, built documentation, tools | Commits |
| `gh-pages` | The built site only, adapted to the address of a project page | A script, as a whole. Never edit it by hand |

## Build

```bash
python -m venv .venv
.venv/bin/pip install -r src/requirements.txt
PY=.venv/bin/python src/tools/build.sh
```

`build.sh` regenerates the algorithm pages, syncs the landing page table, builds
`docs/` in strict mode, removes what changes with the clock, and runs the pre-publish scan. It stops at the first failure.

## Preview

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Common changes

| To | Edit | Then |
|---|---|---|
| Add or change an algorithm | `src/data/algorithms.yaml`, and `nav` in `src/mkdocs.yml` for a new one | `build.sh` |
| Update the numbers | replace the table in `src/data/results/` | `build.sh` |
| Add a topic page | new file under `src/content/`, and `nav` in `src/mkdocs.yml` | `build.sh` |
| Change the landing page | `index.html`, `assets/style.css` | `src/tools/check_site.py` |

Numbers are never typed into a page. `gen_algorithms.py` computes them from
`src/data/results/` and refuses to write pages when the headline numbers of the
paper can no longer be reproduced from those tables.

## Anonymity

Everything in this repository is served publicly. Before every push, run

```bash
PY=.venv/bin/python; $PY src/tools/check_site.py
```

and publish only when it reports `clean`. The scan covers identity terms, machine
paths, author metadata in figures and external URLs. The documentation configuration
must not gain a repository link, an edit link, an author or copyright line, analytics,
or any plugin that reads version-control history.
