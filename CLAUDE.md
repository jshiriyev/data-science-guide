# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static site of data-science cheat sheets, published to GitHub Pages at
<https://jshiriyev.github.io/data-science-guide/>. One sheet is added per week.

No framework, no package manager, no dependencies. Plain HTML/CSS/JS, plus two
Python 3 scripts that need only the standard library.

## Commands

```bash
python tools/build_catalog.py           # regenerate data/catalog.js from the sheets on disk
python tools/build_catalog.py --check   # exit 1 if catalog.js is stale (no write)
python tools/check_site.py              # links, metadata, duplicate ids, unescaped markup
python -m http.server 8000              # preview at http://localhost:8000
```

`check_site.py` is the closest thing to a test suite here; run it after editing
any `.html`. It exits non-zero on failure and CI runs it before deploying.

## Architecture

**The landing page is generated, not written.** `index.html` contains no list of
sheets. At load it reads `window.DSG_CATALOG` from `data/catalog.js` and
`assets/js/home.js` builds the subject sections from it.

`data/catalog.js` is produced by `tools/build_catalog.py`, which walks the seven
subject folders, globs `*.html`, and pulls each sheet's name and summary out of
its `<title>` and `<meta name="description">` tags. So:

- A sheet's title and blurb live **only** in its own two meta tags. Editing
  `data/catalog.js` by hand is pointless — it is regenerated and overwritten.
- The subject list, their order, and their blurbs live **only** in the
  `SUBJECTS` constant in `tools/build_catalog.py`. Adding an eighth subject
  means adding an entry there and creating the matching folder; the folder name
  must equal the entry's `id`.
- The generated file is committed so that opening the site from disk works, but
  the deploy workflow regenerates it, so the published index always reflects
  what is actually in the repo.

**Sheets are declarative.** `assets/js/sheet.js` derives everything from markup,
with no per-sheet configuration: each `<section class="section" id="...">` with
an `<h2>` becomes a table-of-contents entry with scroll tracking, each `.card`
becomes a unit the search box filters (it caches the text once, so do not expect
it to notice DOM you inject later), and each `.code` block gets a copy button.
A new sheet that follows `templates/cheatsheet.html` inherits all of it.

**Theming.** `assets/css/base.css` defines tokens on `:root`, redefines them
under `@media (prefers-color-scheme: dark)` guarded by
`:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]` for
the explicit toggle. `assets/js/theme.js` must stay a synchronous `<head>`
script — it applies the saved theme before first paint, and deferring it brings
back the flash of the wrong palette.

## Conventions for a new sheet

Copy `templates/cheatsheet.html` into the subject folder. It assumes exactly one
level of nesting, so its `../assets/...` paths only work from a subject folder.

- Title must read `Topic — Data Science Guide` (em dash); `build_catalog.py`
  splits on it and `check_site.py` enforces it.
- `<meta name="description">` is required — it becomes the blurb on the landing
  page.
- Section `id`s must be unique within the page or the table of contents breaks.
- Inside `<pre>`, write `<` `>` `&` as entities. `check_site.py` catches misses.

## Deployment

`.github/workflows/pages.yml` runs on every push to `main`: rebuild the catalog,
run the checker, rsync everything except `.git`, `.github`, `tools`,
`templates`, `README.md` and `CLAUDE.md` into `_site`, then upload and deploy.

`actions/configure-pages` runs with `enablement: true`, so the workflow turns
Pages on itself rather than depending on a manual setting.

Pages deploys from the workflow artifact, not from a branch, so `.nojekyll` is
not strictly load-bearing today — it is kept so that switching to a branch-based
deploy later does not silently start stripping files.

## Gotchas

- `templates/cheatsheet.html` is excluded from the published site and, because
  it does not sit in a subject folder, is not picked up by the catalog either.
- Writing these HTML files with shell heredocs is painful — the markup collides
  with shell quoting. Use the Write tool.
