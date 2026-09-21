#!/usr/bin/env python3
"""Check the site for the mistakes that survive a casual look in the browser.

Run this before pushing a new cheat sheet:

    python tools/check_site.py

It verifies that every local href/src resolves to a file that exists, that the
metadata the landing page is generated from is present, that section ids are
unique (duplicates silently break the table of contents), and that no raw angle
bracket was left inside a code block.
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
PRE_RE = re.compile(r"<pre>(.*?)</pre>", re.S)
ENTITY_RE = re.compile(r"&(?:[a-zA-Z][a-zA-Z0-9]*|#\d+);")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
DESCRIPTION_RE = re.compile(
    r"""<meta\s[^>]*name=["']description["'][^>]*content=["']([^"']*)["']""", re.I
)

EXTERNAL_PREFIXES = ("http://", "https://", "//", "#", "data:", "mailto:", "javascript:")


def pages() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and "_site" not in path.parts
    )


def check(path: Path, problems: list[str]) -> None:
    rel = path.relative_to(ROOT).as_posix()
    raw = path.read_text(encoding="utf-8")
    # Comments hold instructions that legitimately contain markup, so the
    # structural checks below run against the document with comments removed.
    body = COMMENT_RE.sub("", raw)
    # Only cheat sheets -- the .html files sitting in a subject folder -- carry
    # the metadata the landing page is generated from.
    is_sheet = path.parent.name in SUBJECT_IDS

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
            problems.append(f"{rel}: link target missing -> {ref}")

    title = TITLE_RE.search(body)
    description = DESCRIPTION_RE.search(body)
    if not title:
        problems.append(f"{rel}: no <title> (the landing page needs it)")
    if not description or not description.group(1).strip():
        problems.append(f"{rel}: no <meta name=\"description\"> (the landing page needs it)")
    if title and is_sheet and "—" not in title.group(1):
        problems.append(
            f"{rel}: title should read \"Topic — Data Science Guide\", got {title.group(1)!r}"
        )

    ids = SECTION_ID_RE.findall(body)
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        problems.append(f"{rel}: duplicate section ids {duplicates}")

    for block in PRE_RE.findall(body):
        stripped = ENTITY_RE.sub("", block)
        if "<" in stripped or ">" in stripped:
            offenders = [
                line.strip()
                for line in block.splitlines()
                if "<" in ENTITY_RE.sub("", line) or ">" in ENTITY_RE.sub("", line)
            ]
            problems.append(
                f"{rel}: unescaped < or > in a code block -> {offenders[0][:60]!r}"
            )
            break


def check_catalog(problems: list[str]) -> None:
    """The landing page is generated, so verify it matches what is on disk."""
    catalog_path = ROOT / "data" / "catalog.js"
    if not catalog_path.exists():
        problems.append("data/catalog.js is missing -- run: python tools/build_catalog.py")
        return

    source = catalog_path.read_text(encoding="utf-8")
    match = re.search(r"window\.DSG_CATALOG\s*=\s*(\{.*\});", source, re.S)
    if not match:
        problems.append("data/catalog.js is not in the expected generated form")
        return

    try:
        catalog = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        problems.append(f"data/catalog.js does not parse as JSON: {error}")
        return

    listed = set()
    for subject in catalog.get("subjects", []):
        for sheet in subject.get("sheets", []):
            listed.add(sheet["href"])
            if not (ROOT / sheet["href"]).exists():
                problems.append(f"data/catalog.js lists a missing file: {sheet['href']}")

    on_disk = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*.html")
        if path.parent.name in SUBJECT_IDS
    }
    for href in sorted(on_disk - listed):
        problems.append(
            f"{href} is not in data/catalog.js -- run: python tools/build_catalog.py"
        )


def main() -> int:
    found = pages()
    if not found:
        print("no HTML pages found", file=sys.stderr)
        return 1

    problems: list[str] = []
    for path in found:
        check(path, problems)
    check_catalog(problems)

    print(f"checked {len(found)} page(s)")
    for problem in problems:
        print(f"  FAIL  {problem}")

    if problems:
        print(f"\n{len(problems)} problem(s)")
        return 1

    print("all good")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
