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

Each folder holds one `.html` file per topic — `data-analytics-tools/sql.html`,
`data-analytics-tools/matplotlib.html`, and so on.

## Adding a cheat sheet

```bash
cp templates/cheatsheet.html data-analytics-tools/pandas.html
# edit it: <title>, <meta name="description">, and the sections

python tools/build_catalog.py    # regenerate the landing page index
python tools/check_site.py       # links, metadata, markup

python -m http.server 8000       # preview at http://localhost:8000

git add -A && git commit -m "Add pandas cheat sheet" && git push
```

Pushing to `main` deploys. There is no build step beyond the catalog generator,
and no dependencies to install — the tooling is plain Python 3 and the site is
plain HTML, CSS and JavaScript.

The landing page is generated from each sheet's `<title>` and
`<meta name="description">`, so those two tags are the only place a sheet's name
and summary are written down.

## Repository layout

```
index.html              landing page, rendered from data/catalog.js
assets/css, assets/js   shared styles and behaviour for every sheet
data/catalog.js         generated index of the sheets on disk
templates/              starting point for a new sheet
tools/                  catalog generator and site checker
.github/workflows/      GitHub Pages deployment
```

## What a sheet gets for free

Writing `<section class="section" id="...">` with an `<h2>`, and `.card` blocks
inside it, is enough to get a table of contents, scroll tracking, a search
filter (`/` to focus), copy buttons on code blocks, a light/dark toggle and a
print stylesheet. None of it is configured per sheet.
