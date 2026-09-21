#!/usr/bin/env python3
"""Check the site for the mistakes that survive a casual look in the browser.

Run this before pushing a new cheat sheet:

    python tools/check_site.py

Sheets are written elsewhere and dropped into a subject folder, so this does not
police house style -- a sheet brings its own markup, its own CSS and its own
title. It checks the things that actually break a published page: a link that
goes nowhere, a missing charset turning an em dash into mojibake, a missing
doctype triggering quirks mode, or a sheet the landing page does not know about.

Failures block the deploy. Warnings are printed and do not.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_catalog import ROOT, SUBJECTS  # noqa: E402

SUBJECT_IDS = {subject["id"] for subject in SUBJECTS}

COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
REF_RE = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", re.I)
SECTION_ID_RE = re.compile(r'<section[^>]*class="[^"]*\bsection\b[^"]*"[^>]*id="([^"]+)"')
PRE_RE = re.compile(r"<pre\b[^>]*>(.*?)</pre>", re.S | re.I)
ENTITY_RE = re.compile(r"&(?:[a-zA-Z][a-zA-Z0-9]*|#\d+);")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
DESCRIPTION_RE = re.compile(
    r"""<meta\s[^>]*name=["']description["'][^>]*content=["']([^"']*)["']""", re.I
)
DOCTYPE_RE = re.compile(r"<!DOCTYPE\s+html", re.I)
CHARSET_RE = re.compile(r"""<meta\s[^>]*charset\s*=""", re.I)
VIEWPORT_RE = re.compile(r"""<meta\s[^>]*name=["']viewport["']""", re.I)

EXTERNAL_PREFIXES = ("http://", "https://", "//", "#", "data:", "mailto:", "javascript:")

ADOPT_HINT = "run: python tools/adopt_sheet.py"


def pages() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and "_site" not in path.parts
    )


def check_page(path: Path, failures: list[str], warnings: list[str]) -> None:
    rel = path.relative_to(ROOT).as_posix()
    raw = path.read_bytes().decode("utf-8", errors="replace")
    # Comments legitimately contain markup (the template documents itself), so
    # the structural checks run against the document without them.
    body = COMMENT_RE.sub("", raw)

    for ref in REF_RE.findall(body):
        if ref.startswith(EXTERNAL_PREFIXES):
            continue
        clean = ref.split("#")[0].split("?")[0]
        if not clean:
            continue
        target = path.parent / clean
        if clean.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            failures.append(f"{rel}: link target missing -> {ref}")

    # A page missing any of these renders wrong somewhere.
    if not DOCTYPE_RE.search(body):
        failures.append(f"{rel}: no <!DOCTYPE html> (quirks mode) -- {ADOPT_HINT}")
    if not CHARSET_RE.search(body):
        failures.append(f"{rel}: no <meta charset> (mojibake risk) -- {ADOPT_HINT}")
    if not VIEWPORT_RE.search(body):
        failures.append(f'{rel}: no <meta name="viewport"> (breaks on phones) -- {ADOPT_HINT}')

    title = TITLE_RE.search(body)
    if not title or not title.group(1).strip():
        failures.append(f"{rel}: no <title> -- the landing page takes the card name from it")

    description = DESCRIPTION_RE.search(body)
    if path.parent.name in SUBJECT_IDS and (not description or not description.group(1).strip()):
        warnings.append(f'{rel}: no <meta name="description"> -- its card will have no summary')

    ids = SECTION_ID_RE.findall(body)
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        failures.append(f"{rel}: duplicate section ids {duplicates}")

    for block in PRE_RE.findall(body):
        stripped = ENTITY_RE.sub("", block)
        if "<" in stripped or ">" in stripped:
            offender = next(
                line.strip()
                for line in block.splitlines()
                if "<" in ENTITY_RE.sub("", line) or ">" in ENTITY_RE.sub("", line)
            )
            warnings.append(f"{rel}: unescaped < or > in a code block -> {offender[:60]!r}")
            break


def check_catalog(failures: list[str]) -> None:
    """The landing page is generated, so verify it matches what is on disk."""
    catalog_path = ROOT / "data" / "catalog.js"
    if not catalog_path.exists():
        failures.append("data/catalog.js is missing -- run: python tools/build_catalog.py")
        return

    source = catalog_path.read_text(encoding="utf-8")
    match = re.search(r"window\.DSG_CATALOG\s*=\s*(\{.*\});", source, re.S)
    if not match:
        failures.append("data/catalog.js is not in the expected generated form")
        return

    try:
        catalog = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        failures.append(f"data/catalog.js does not parse as JSON: {error}")
        return

    listed = set()
    for subject in catalog.get("subjects", []):
        for sheet in subject.get("sheets", []):
            listed.add(sheet["href"])
            if not (ROOT / sheet["href"]).exists():
                failures.append(f"data/catalog.js lists a missing file: {sheet['href']}")

    on_disk = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*.html")
        if path.parent.name in SUBJECT_IDS
    }
    for href in sorted(on_disk - listed):
        failures.append(f"{href} is not in data/catalog.js -- run: python tools/build_catalog.py")


def main() -> int:
    found = pages()
    if not found:
        print("no HTML pages found", file=sys.stderr)
        return 1

    failures: list[str] = []
    warnings: list[str] = []
    for path in found:
        check_page(path, failures, warnings)
    check_catalog(failures)

    print(f"checked {len(found)} page(s)")
    for warning in warnings:
        print(f"  warn  {warning}")
    for failure in failures:
        print(f"  FAIL  {failure}")

    if failures:
        print(f"\n{len(failures)} problem(s)")
        return 1

    print("all good" + (f" ({len(warnings)} warning(s))" if warnings else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
