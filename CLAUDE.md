# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static site of data-science cheat sheets, published to GitHub Pages at
<https://jshiriyev.github.io/data-science-guide/>. One sheet is added per week.

No framework, no package manager, no dependencies. Plain HTML/CSS/JS, plus three
Python 3 scripts in `tools/` that need only the standard library.

## Commands

```bash
python tools/adopt_sheet.py             # give dropped-in sheets their document scaffolding
python tools/adopt_sheet.py --check     # exit 1 if any sheet still needs it
python tools/build_catalog.py           # regenerate data/catalog.js from the sheets on disk
python tools/build_catalog.py --check   # exit 1 if catalog.js is stale (no write)
python tools/check_site.py              # links, structure, catalog consistency
python -m http.server 8000              # preview at http://localhost:8000
```

`check_site.py` is the closest thing to a test suite here; run it after touching
any `.html`. CI runs adopt, build and check in that order before deploying.

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

## Sheets arrive from outside

**The owner writes cheat sheets elsewhere and drops the `.html` file into a
subject folder.** They are self-contained pages with their own CSS, their own
title and their own behaviour — they do not use `assets/` and are not expected
to. Do not rewrite a sheet to match house style, and do not add conventions to
the tooling that an externally authored file would fail.

Such files usually arrive as a *fragment*: styles and markup with no
`<!DOCTYPE>`, no `<html>`, no `<head>`, no charset and no viewport. That means
quirks-mode rendering, and mojibake for any non-ASCII character as soon as the
server does not supply a charset. `tools/adopt_sheet.py` wraps the fragment,
splitting it at the last head-legal element (`<title>`, `<meta>`, `<link>`,
`<style>`, comments) and putting everything after it in `<body>`. It is
idempotent and preserves the file's original line endings — an earlier version
did not, and rewrote every line of a 163 KB file.

`check_site.py` therefore splits its output: **failures** are things that break
a published page (dead local link, missing doctype/charset/viewport, no title,
duplicate `.section` ids, catalog out of sync) and block the deploy;
**warnings** are cosmetic (no description, unescaped `<`/`>` in a `<pre>`) and
do not. Keep that split — turning a warning into a failure would block the
owner's weekly push over something that renders fine.

### If you do write a sheet against the shared styles

Start from `templates/cheatsheet.html`. It assumes exactly one level of nesting,
so its `../assets/...` paths only work from a subject folder. Section `id`s must
be unique or the table of contents breaks, and inside `<pre>` write `<` `>` `&`
as entities.

## Deployment

`.github/workflows/pages.yml` runs on every push to `main`: adopt any fragment
sheets, rebuild the catalog, run the checker, rsync everything except `.git`,
`.github`, `tools`, `templates`, `README.md` and `CLAUDE.md` into `_site`, then
upload and deploy. Adopt and build both run in CI so that pushing a raw
drop-in publishes correctly even when the local steps were skipped.

Pages source is set to "GitHub Actions" in repository settings. The workflow
also passes `enablement: true`, but the workflow token could not create the
Pages site on a repository that had never had one — it took a manual enable.

Pages deploys from the workflow artifact, not from a branch, so `.nojekyll` is
not strictly load-bearing today — it is kept so that switching to a branch-based
deploy later does not silently start stripping files.

## Gotchas

- `templates/cheatsheet.html` is excluded from the published site and, because
  it does not sit in a subject folder, is not picked up by the catalog either.
- `data-analytics-tools/` holds two SQL sheets on purpose: `SQL_Cheat_Sheet.html`
  (the owner's interactive review console) and `sql-quick-reference.html` (a
  lookup reference built on the shared styles).
- Writing these HTML files with shell heredocs is painful — the markup collides
  with shell quoting. Use the Write tool.
