#!/usr/bin/env python3
"""Does a technical-analysis vault still have the shape the skill writes?

QA-AIP3's finding, which is the reason this exists: the symbol-page Dataview
query read a column called `method` while every analysis note's frontmatter
carried `methods`. Both files looked fine alone; the drift was only visible
by reading them TOGETHER, and its symptom -- an empty column -- looks exactly
like "no analyses yet". So the check that matters is cross-file: any column a
Dataview block asks for must exist as a frontmatter field in the analysis
template.

Checks, each cheap and each with a real failure mode behind it:
  1. The three writable directories exist.
  2. Every 分析/ note carries the frontmatter keys review queries filter on.
  3. Dataview columns resolve against the analysis template's frontmatter.
  4. Every symbol page offers a plain-Markdown history link, so a vault
     without the (optional) Dataview plugin still demonstrates review.

Usage: vault_check.py <vault-path>   (exit 0 clean, 1 problems, 2 not a vault)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_DIRS = ["分析", "标的", "附件"]
REQUIRED_ANALYSIS_KEYS = ["analysis_id", "symbol", "timeframe", "as_of", "bias", "outcome", "tags"]
ANALYSIS_TEMPLATE = Path("_模板") / "分析.md"
DATAVIEW_BLOCK = re.compile(r"```dataview\n(.*?)```", re.S)
TABLE_LINE = re.compile(r"^\s*TABLE\s+(.+)$", re.M | re.I)


def frontmatter_keys(text: str) -> set[str]:
    parts = text.split("---", 2)
    if len(parts) < 3:
        return set()
    keys = set()
    for line in parts[1].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", line)
        if m:
            keys.add(m.group(1))
    return keys


def dataview_columns(text: str) -> list[str]:
    cols: list[str] = []
    for block in DATAVIEW_BLOCK.findall(text):
        for line in TABLE_LINE.findall(block):
            for piece in line.split(","):
                # `as_of AS 截至` names the field before AS; bare `bias` is itself.
                field = piece.strip().split()[0] if piece.strip() else ""
                if field and not field.startswith('"'):
                    cols.append(field)
    return cols


def check(vault: Path) -> list[str]:
    problems: list[str] = []
    for d in REQUIRED_DIRS:
        if not (vault / d).is_dir():
            problems.append(f"missing directory: {d}/")
    if problems:
        return problems

    template = vault / ANALYSIS_TEMPLATE
    template_keys = frontmatter_keys(template.read_text(encoding="utf-8")) if template.exists() else set()
    if not template_keys:
        problems.append(f"no analysis template at {ANALYSIS_TEMPLATE}, so Dataview columns cannot be validated")

    for note in sorted((vault / "分析").glob("*.md")):
        keys = frontmatter_keys(note.read_text(encoding="utf-8"))
        missing = [k for k in REQUIRED_ANALYSIS_KEYS if k not in keys]
        if missing:
            problems.append(f"分析/{note.name}: frontmatter is missing {', '.join(missing)}")

    known = {"file", "date"} | template_keys  # Dataview's own implicit fields stay legal
    for page in sorted(list((vault / "标的").glob("*.md")) + list((vault / "_模板").glob("*.md"))):
        text = page.read_text(encoding="utf-8")
        for col in dataview_columns(text):
            if col not in known:
                problems.append(
                    f"{page.parent.name}/{page.name}: Dataview asks for `{col}`, which no analysis "
                    f"frontmatter field provides -- the column will render empty and look like missing data"
                )
        if page.parent.name == "标的" and "## 历史分析" in text and "[[分析/" not in text:
            problems.append(f"标的/{page.name}: no plain-Markdown history link; without the optional Dataview plugin the history section is blank")
    return problems


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: vault_check.py <vault-path>", file=sys.stderr)
        return 2
    vault = Path(sys.argv[1])
    if not vault.is_dir():
        print(f"not a directory: {vault}", file=sys.stderr)
        return 2
    problems = check(vault)
    for p in problems:
        print(f"PROBLEM {p}")
    print("clean" if not problems else f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
