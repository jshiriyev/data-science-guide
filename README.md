# data-science-guide

Cheat sheets across data science, published as a static site with GitHub Pages.

**<https://jshiriyev.github.io/data-science-guide/>**

One new sheet goes up each week.

## Subjects

| # | Subject | Folder |
|---|---------|--------|
| 1 | Data Science Overview | `data-science-overview/` |
| 2 | Probability and Statistics | `probability-and-statistics/` |
| 3 | Python Programming | `python-programming/` |
| 4 | Data Analytics Tools | `data-analytics-tools/` |
| 5 | Machine Learning Algorithms | `machine-learning-algorithms/` |
| 6 | Big Data Principles | `big-data-principles/` |
| 7 | Deep Learning Methods | `deep-learning-methods/` |

Each folder holds one `.html` file per topic — `data-analytics-tools/sql-cheat-sheet.html`,
`data-analytics-tools/matplotlib.html`, and so on. File names are free-form; the
landing page reads each sheet's `<title>`, not its filename.

## Adding a cheat sheet

Drop the `.html` file into the right subject folder, commit and push:

```bash
cp ~/Downloads/Pandas_Cheat_Sheet.html python-programming/
git add -A && git commit -m "Add pandas cheat sheet" && git push
```

That is enough. The deploy normalises the file, regenerates the index and
publishes it. A sheet keeps its own markup, styling and title — nothing has to
match a house style.

To preview before pushing, run the same steps locally:

```bash
python tools/adopt_sheet.py      # add doctype/charset/viewport if missing
python tools/build_catalog.py    # regenerate the landing page index
python tools/check_site.py       # links and structure
python -m http.server 8000       # preview at http://localhost:8000
```

Sheets written elsewhere often arrive as a fragment — no `<!DOCTYPE>`, no
`<head>`, no charset — which means quirks-mode rendering and mojibake wherever
the file uses an em dash or an arrow. `adopt_sheet.py` adds that scaffolding
without touching the page's own markup, and is safe to re-run.

The landing page card takes its name from the sheet's `<title>` and its summary
from `<meta name="description">`. A sheet with no description still publishes;
its card just has no summary line. To add one:

```bash
python tools/adopt_sheet.py python-programming/Pandas_Cheat_Sheet.html \
  --description "Selection, joins, groupby and reshaping."
```

There are no dependencies to install — plain Python 3, and plain HTML/CSS/JS.

## Repository layout

```
index.html              landing page, rendered from data/catalog.js
assets/css, assets/js   shared styles and behaviour for every sheet
data/catalog.js         generated index of the sheets on disk
templates/              starting point for a new sheet
tools/                  sheet adopter, catalog generator, site checker
.github/workflows/      GitHub Pages deployment
```

## Writing a sheet against the shared styles

Optional — a sheet is free to be entirely self-contained. But if you start from
`templates/cheatsheet.html`, then writing `<section class="section" id="...">`
with an `<h2>`, and `.card` blocks inside it, is enough to get a table of
contents, scroll tracking, a search filter (`/` to focus), copy buttons on code
blocks, a light/dark toggle and a print stylesheet, with no per-sheet wiring.
