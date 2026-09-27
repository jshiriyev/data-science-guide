# Prompt: build a cheat sheet from the materials in this folder

Copy everything below the line into the agent. Run it from inside the folder that
holds the source material. Fill in the two bracketed values in the first
paragraph if you know them; otherwise leave them and let the agent decide.

---

You are in a folder of study material for one subject — most likely PDFs,
PowerPoint decks, Jupyter notebooks, and possibly `.docx`, `.md`, `.sql`, `.csv`
or screenshots. Your job is to read **all** of it and produce **one
self-contained HTML cheat sheet** that teaches the subject the way
`data-analytics-tools/sql-cheat-sheet.html` in the `data-science-guide` repo
teaches SQL. Target subject: [SUBJECT — leave blank to infer from the files].
Destination subject folder in the repo: [one of `data-science-overview`,
`probability-and-statistics`, `machine-learning-algorithms`,
`deep-learning-methods`, `big-data-principles`, `data-analytics-tools`,
`python-programming` — leave blank to infer].

Work in four phases. Do not start writing HTML until phase 3 is done.

## Phase 1 — inventory

List the folder recursively, including sizes and extensions. Build a table of
every file: path, type, size, page/slide/cell count, and a one-line guess at what
it contains. Put this table in a working notes file in your scratchpad directory,
not in the repo.

Flag anything you cannot read (encrypted PDF, video, proprietary format) and say
so explicitly at the end. Never silently skip a file.

## Phase 2 — extract

Read every file. Use the cheapest method that gives you the actual text:

- **PDF** — `pdftotext -layout` if available; otherwise `pypdf`/`PyMuPDF`;
  otherwise the `Read` tool with the `pages` parameter (max 20 pages per call).
  For scanned PDFs with no text layer, OCR or read the pages as images. Keep
  page numbers as you go — you will cite them.
- **PPTX** — a `.pptx` is a zip. With no dependencies:
  `python -c "import zipfile,re,glob; ..."` over `ppt/slides/slide*.xml`,
  stripping tags, is enough for text and is fast. Use `python-pptx` if it is
  installed and you also want speaker notes. Keep slide numbers.
- **Notebooks** — `.ipynb` is JSON. Walk `cells[]`, joining `source` and keeping
  `cell_type`; read outputs too, because a wrong output is a correction worth
  recording. Keep cell indices.
- **DOCX** — zip again: `word/document.xml`.
- **Text-ish** (`.md`, `.sql`, `.py`, `.csv`, `.txt`) — read directly. For large
  CSVs, header plus a few rows is enough; you want the schema, not the data.
- **Images/screenshots** — read them with the `Read` tool. Handwritten or
  circled exam answers are gold: they are the source of the "common mistakes"
  section.

Write the extracted text into per-file plain-text dumps in your scratchpad so
you can grep across the whole corpus afterwards. Then grep for the things that
structure a sheet: definitions, formulas, "note that", "common mistake",
"remember", exam questions, homework prompts, and any worked solutions.

Establish a short citation code for each source while you extract — `W1`, `W2`
for weekly PDFs, `Deck 3` for a presentation, `LC cell 22` for a notebook cell,
`Final_Exam.sql Q3` for a file-and-question. Every claim in the finished sheet
carries one of these codes.

## Phase 3 — design the sheet before writing it

Produce a plan (in your notes, and summarised to the user in a few lines) that
fixes:

1. **The spine.** One sentence that names the single idea the subject keeps
   returning to. In the SQL sheet it is *"Every SQL question is a question about
   grain, order and NULLs."* Find the equivalent. Everything else hangs off it.
2. **The pipeline / mental model.** 6–10 ordered stages the learner should be
   able to recite — the logical order of operations, the stages of a training
   run, the steps of a hypothesis test, whatever this subject's ordered skeleton
   is. Each stage gets a paragraph explaining what happens there *and* which
   classic error comes from misplacing work in it.
3. **The topic list.** 25–45 topics, numbered, each mapped to: a phase (`P1`
   core / `P2` / `P3` advanced), a category (2–5 verbs such as
   Present / Combine / Extend / Operate), and the sources that back it.
   Topics must partition the material: every substantial chunk of every file
   lands in at least one topic, and you must be able to say which.
4. **A coverage check.** Explicitly list any file or chapter that ended up in no
   topic, and either add a topic or justify the omission.
5. **Corrections.** Every error you found in the material's own answers,
   notebooks or marked exams, each tied to the topic it belongs to.
6. **Study order and role focus.** Phases that group topics into a sequence, and
   3–6 reader roles with the topic subset each one needs.
7. **Readiness checks.** 8–12 capability statements — "can do X, evidenced by
   Y" — each pointing at a topic number.
8. **Interactive labs**, if and only if the subject has 2–5 ideas that a tiny
   deterministic widget makes obvious (join semantics, three-valued logic,
   a window frame sliding, a bias/variance tradeoff, gradient steps, a
   confusion matrix at varying thresholds). Hand-computed in JS over a small
   fixed dataset, ~10 rows, no libraries. If nothing qualifies, omit the labs
   section rather than inventing a weak one.

## Phase 4 — write the file

One file. No build step, no framework, no bundler, no external JavaScript.
The only permitted remote resource is a Google Fonts stylesheet.

### Required document shell

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="One sentence. This becomes the blurb on the site index.">
<title>Short Sheet Name</title>
```

`<title>` and `<meta name="description">` are load-bearing: the repo's
`tools/build_catalog.py` reads exactly these two tags to generate the landing
page. Nothing else about the file is read by the tooling, and
`data/catalog.js` must never be hand-edited.

### Required CSS contract

Define all colour, type and radius values as tokens on `:root`, then redefine
them twice — under `@media (prefers-color-scheme: dark)` guarded by
`:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]` for
the explicit toggle. Give `body` an explicit background from a token. Never
hard-code a hex value outside the token blocks.

Pick your own palette rather than copying the SQL sheet's green — each sheet
looks like itself. Keep it accessible in both themes: body text ≥ 4.5:1 against
its surface, and never encode meaning in hue alone (a trap card is marked by its
label and its border, not only by being orange).

Layout: a sticky top bar (title, search input, theme button, optional extras), a
`max-width: ~1280px` grid shell of a sticky left rail plus the main column,
collapsing to a single column under ~920px with the rail going static. 16px side
gutters, no horizontal page scroll at phone width. `scroll-margin-top` on
sections so anchor jumps clear the sticky bar.

### Required page anatomy

Sections, each with a unique `id` (duplicates break the table of contents and
fail the repo's checker):

- **Hero / mental model** — the spine sentence as an `<h2>`, a lede paragraph, a
  row of stat pills (topic count, pattern count, correction count), and the
  pipeline as clickable stages that swap an explanatory note below.
- **Topics** — the numbered topic cards, collapsible, with a live count, expand
  and collapse all, and filtering by search text, phase chip, category chip and
  role.
- **Labs** — tabbed widgets, if phase 3 kept them.
- **Patterns** — 6–12 reusable worked solutions, each with a "why this shape"
  paragraph and the code.
- **Corrections** — each item stating source, the wrong claim, and the fix, with
  the fix hidden until revealed so the reader can self-test.
- **Study order** — the phases, then the role selector wired to the topic filter.
- **Readiness check** — the capability statements as a checklist.
- A footer naming the material the sheet was built from and any caveat about
  dialect, library version or scope.

Left rail: table of contents linking every section, plus a self-scoring ring —
each topic scored 0–3 by the reader, total shown as a percentage, persisted in
`localStorage`, with a reset button and a "weak topics only" filter.

### Required data-driven structure

Do **not** hand-write repeated markup. Declare the content as JS arrays near the
top of one `<script>` and render from them, mirroring the reference's shapes:

```js
const TOPICS = [{
  n: 1,                       // number, also the anchor id (t1) and score key
  p: "P1", pf: "P1",          // phase, and phase used for filtering
  c: "Extend",                // category
  t: "Topic title",
  sum: "One sentence a reader could repeat from memory.",
  src: "W1 pp. 6-21 · Deck 11-16",   // citations, always present
  tags: "space separated search terms including synonyms and function names",
  keys: [ /* 4-6 sentences that each carry one idea */ ],
  code: [{ lab: "What this demonstrates", sql: `...` }],  // rename the field to
                                                          // suit the language
  traps: [["Short trap name", "Why it bites and what to do instead."]],
  practice: "A task from the material, restated.",
  approach: "How to reason about it — prose, not just an answer.",
  mastery: "The check that proves the topic is understood.",
  lab: "join"                 // optional, links a topic to a lab tab
}];

const STAGES   = [{ k: "Stage name", s: "1", d: "What happens, and the error." }];
const PATTERNS = [{ id: "A", t: "Title", why: "Why this shape", sql: `...` }];
const FIXES    = [{ s: "Source", t: 8, b: "The wrong claim", f: "The fix" }];
const PHASES   = [{ n: "Phase 1", t: "Name", d: "Goal", ts: [1,2,3] }];
const ROLES    = [{ r: "Role name", ts: [8,9], note: "What they need and why" }];
const READY    = [{ c: "Capability", e: "Evidence", t: 11 }];
```

Then: small `$`/`$$`/`esc` helpers; a regex syntax highlighter over a keyword
list for whatever language the sheet teaches (skip it if there is no code); a
`CODE_STORE` keyed by an incrementing id so each code block's copy button copies
the raw source rather than the highlighted DOM; render functions per section; a
single delegated `click` listener on `document` rather than per-element handlers;
and a keyboard-dismissible, focus-restoring modal if you add a drill mode.

### Hard requirements

- **Namespace your `localStorage` keys** to this sheet (`"<slug>.scores"`,
  `"<slug>.theme"`) and wrap every read and write in `try`/`catch` — it throws in
  private windows. The page must render correctly when storage is empty or
  unavailable.
- Inside template literals, an unescaped backtick or `${` breaks the file; inside
  `<pre>`/`<code>` written as markup, write `<` `>` `&` as entities. Render
  user-visible strings through `esc()`.
- Every interactive control is a real `<button>`, `<input>` or `<select>` with an
  accessible name, `aria-pressed` on toggles, `role="tablist"`/`aria-selected` on
  tabs, and a visible `:focus-visible` outline.
- No claim without a source. If you must add something the material does not
  cover because the topic would otherwise be incoherent, say so in the text
  ("not in the course material, but needed to make sense of the above") rather
  than presenting it as taught content.
- Content voice: plain declarative prose, one idea per sentence, no filler, no
  "it is important to note". Prefer the concrete failure over the abstract rule
  — "`x NOT IN (1, NULL)` is never TRUE" beats "be careful with NULLs".
- Keep the file under ~16MB. Do not inline images as data URIs; draw diagrams as
  inline SVG that uses the same CSS tokens so they work in both themes.

## Phase 5 — install and verify

Save the file as `<subject-folder>/<kebab-case-name>.html` in the
`data-science-guide` repo, then from the repo root:

```bash
python tools/build_catalog.py     # regenerates data/catalog.js from your meta tags
python tools/check_site.py        # failures block deploy; warnings do not
python -m http.server 8000        # open the sheet and click through it
```

`check_site.py` **failures** — dead local link, missing doctype/charset/viewport,
no title, duplicate `.section` ids, catalog out of sync — must be zero. Fix the
warnings too if they are yours.

Then verify by hand, and report the result honestly:

- opens from `file://` with no console errors;
- light and dark both readable, and the theme button overrides the OS setting and
  survives a reload;
- search, every chip, the role selector and the score ring all work, and the
  empty-result state appears when nothing matches;
- copy buttons copy the raw source;
- usable at 380px wide with no horizontal scroll;
- `Tab` reaches every control and `Esc` closes the modal.

Finish with: the topic count, what each source file contributed, anything you
could not read, and anything you added that the material did not cover.
