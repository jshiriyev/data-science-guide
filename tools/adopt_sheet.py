#!/usr/bin/env python3
"""Normalise an externally authored cheat sheet into a valid standalone page.

Sheets are written elsewhere and dropped into a subject folder, so they often
arrive as a bare fragment: styles and markup with no <!DOCTYPE>, no <html>, and
no <head>. Browsers then render them in quirks mode, and any page holding a
character outside ASCII -- an em dash, an arrow -- turns to mojibake as soon as
the server does not happen to send a charset.

This adds the document scaffolding without touching the page's own markup or
design. It is idempotent, so running it over every sheet is safe.

    python tools/adopt_sheet.py                       # every sheet that needs it
    python tools/adopt_sheet.py path/to/sheet.html    # just this one
    python tools/adopt_sheet.py sheet.html --description "One line summary."
    python tools/adopt_sheet.py --check               # report, change nothing
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_catalog import ROOT, SUBJECTS  # noqa: E402

SUBJECT_IDS = {subject["id"] for subject in SUBJECTS}

DOCTYPE_RE = re.compile(r"<!DOCTYPE\s+html", re.I)
HTML_OPEN_RE = re.compile(r"<html\b[^>]*>", re.I)
HEAD_OPEN_RE = re.compile(r"<head\b[^>]*>", re.I)
CHARSET_RE = re.compile(r"""<meta\s[^>]*charset\s*=""", re.I)
VIEWPORT_RE = re.compile(r"""<meta\s[^>]*name=["']viewport["']""", re.I)
DESCRIPTION_RE = re.compile(r"""<meta\s[^>]*name=["']description["']""", re.I)
LANG_RE = re.compile(r"<html\b[^>]*\blang\s*=", re.I)

# Elements that may legally sit in <head>. A fragment usually opens with a run
# of exactly these before its first piece of visible markup.
HEAD_ELEMENT_RE = re.compile(
    r"""\s*(?:
          <!--.*?-->
        | <title\b[^>]*>.*?</title\s*>
        | <style\b[^>]*>.*?</style\s*>
        | <(?:meta|link|base)\b[^>]*/?>
    )""",
    re.I | re.S | re.X,
)

CHARSET_TAG = '<meta charset="utf-8">'
VIEWPORT_TAG = '<meta name="viewport" content="width=device-width, initial-scale=1">'


def read_source(path: Path) -> tuple[str, str]:
    """Read a sheet, returning LF-normalised text plus its original line ending.

    Sheets are authored on other machines, so rewriting their line endings would
    turn an eleven-line insertion into a diff touching every line of the file.
    """
    text = path.read_bytes().decode("utf-8")
    crlf = text.count("\r\n")
    newline = "\r\n" if crlf and crlf >= text.count("\n") - crlf else "\n"
    return text.replace("\r\n", "\n"), newline


def write_source(path: Path, text: str, newline: str) -> None:
    if newline != "\n":
        text = text.replace("\n", newline)
    path.write_bytes(text.encode("utf-8"))


def split_fragment(text: str) -> tuple[str, str]:
    """Return (head_part, body_part) for a document with no <html> wrapper."""
    position = 0
    while True:
        match = HEAD_ELEMENT_RE.match(text, position)
        if not match:
            break
        position = match.end()
    return text[:position].strip("\n"), text[position:].lstrip("\n")


def escape_attribute(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def normalise(text: str, description: str | None) -> tuple[str, list[str]]:
    """Return the rewritten document and a list of what changed."""
    changes: list[str] = []
    has_html = bool(HTML_OPEN_RE.search(text))

    if not has_html:
        head_part, body_part = split_fragment(text)

        head_lines = [CHARSET_TAG, VIEWPORT_TAG]
        changes.append("added <!DOCTYPE html>, <html lang>, <head> and <body>")
        changes.append("added charset and viewport")

        if description and not DESCRIPTION_RE.search(head_part):
            head_lines.append(f'<meta name="description" content="{escape_attribute(description)}">')
            changes.append("added description")

        rebuilt = "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        rebuilt += "\n".join(head_lines) + "\n"
        if head_part:
            rebuilt += head_part + "\n"
        rebuilt += "</head>\n<body>\n"
        rebuilt += body_part.rstrip() + "\n"
        rebuilt += "</body>\n</html>\n"
        return rebuilt, changes

    # Already a full document: fill in only what is missing.
    result = text

    head_match = HEAD_OPEN_RE.search(result)
    insert_at = head_match.end() if head_match else None

    if not CHARSET_RE.search(result) and insert_at is not None:
        result = result[:insert_at] + "\n" + CHARSET_TAG + result[insert_at:]
        changes.append("added charset")
        insert_at = HEAD_OPEN_RE.search(result).end()

    if not VIEWPORT_RE.search(result) and insert_at is not None:
        result = result[:insert_at] + "\n" + VIEWPORT_TAG + result[insert_at:]
        changes.append("added viewport")
        insert_at = HEAD_OPEN_RE.search(result).end()

    if description and not DESCRIPTION_RE.search(result) and insert_at is not None:
        tag = f'<meta name="description" content="{escape_attribute(description)}">'
        result = result[:insert_at] + "\n" + tag + result[insert_at:]
        changes.append("added description")

    if not DOCTYPE_RE.search(result):
        result = "<!DOCTYPE html>\n" + result.lstrip()
        changes.append("added <!DOCTYPE html>")

    if not LANG_RE.search(result):
        result = HTML_OPEN_RE.sub(lambda m: m.group(0)[:-1] + ' lang="en">', result, count=1)
        changes.append('added lang="en"')

    return result, changes


def sheets() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if path.parent.name in SUBJECT_IDS and "_site" not in path.parts
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="sheets to adopt (default: all)")
    parser.add_argument("--description", help="summary for the landing page card")
    parser.add_argument("--check", action="store_true", help="report only, write nothing")
    args = parser.parse_args()

    if args.description and len(args.paths) != 1:
        parser.error("--description applies to a single file")

    targets = args.paths or sheets()
    if not targets:
        print("no sheets found")
        return 0

    touched = 0
    for path in targets:
        if not path.exists():
            print(f"  MISSING  {path}")
            return 1

        original, newline = read_source(path)
        rewritten, changes = normalise(original, args.description)
        rel = path.relative_to(ROOT).as_posix() if path.is_absolute() else path.as_posix()

        if rewritten == original:
            print(f"  ok       {rel}")
            continue

        touched += 1
        verb = "would fix" if args.check else "fixed"
        print(f"  {verb:<8} {rel}: {'; '.join(changes)}")
        if not args.check:
            write_source(path, rewritten, newline)

    if args.check and touched:
        print(f"\n{touched} sheet(s) need adopting -- run: python tools/adopt_sheet.py")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
