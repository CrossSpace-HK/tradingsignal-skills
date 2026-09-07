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

import hashlib
import re
import sys
from pathlib import Path

REQUIRED_DIRS = ["分析", "标的", "附件"]
REQUIRED_ANALYSIS_KEYS = ["analysis_id", "symbol", "timeframe", "as_of", "bias", "outcome", "tags"]
ANALYSIS_TEMPLATE = Path("_模板") / "分析.md"
DATAVIEW_BLOCK = re.compile(r"```dataview\n(.*?)```", re.S)
TABLE_LINE = re.compile(r"^\s*TABLE\s+(.+)$", re.M | re.I)

# One analysis, one name: date, symbol (letters/digits only), the DECISION
# timeframe, and the analysis id. A multi-timeframe study still decides on
# one timeframe, and that one goes in the name; "多周期" is not a timeframe
# and cannot be sorted, filtered or joined against anything.
ANALYSIS_FILENAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[A-Za-z0-9]+-[A-Za-z0-9]+-[0-9a-f]{6}\.md$")


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


def frontmatter_value(text: str, key: str) -> str | None:
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    m = re.search(rf"^{key}:\s*(.+?)\s*$", parts[1], re.M)
    return m.group(1).strip("\"'") if m else None


def frontmatter_tags(text: str) -> list[str]:
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    out: list[str] = []
    in_tags = False
    for line in parts[1].splitlines():
        if re.match(r"^tags:", line):
            in_tags = True
            continue
        if in_tags:
            m = re.match(r"^\s+-\s+(\S+)", line)
            if m:
                out.append(m.group(1))
            elif re.match(r"^\S", line):
                in_tags = False
    return out


def allowed_tags(vault: Path) -> set[str]:
    """The controlled vocabulary is 标签.md's code blocks, nothing else."""
    f = vault / "标签.md"
    if not f.exists():
        return set()
    tags: set[str] = set()
    for block in re.findall(r"```\n(.*?)```", f.read_text(encoding="utf-8"), re.S):
        if "dataview" in block or "TABLE" in block:
            continue
        tags.update(re.findall(r"[\w\u4e00-\u9fff]+/[\w\u4e00-\u9fff]+", block))
    return tags


def hub_name(symbol: str) -> str:
    """标的/<this>.md for a symbol: strip the =X venue suffix, / becomes -."""
    return symbol.replace("=X", "").replace("/", "-")


def declared_hashes(text: str) -> dict[str, str]:
    """Every SHA-256 the frontmatter declares: the single value and the map."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    out: dict[str, str] = {}
    single = frontmatter_value(text, "image_sha256")
    if single and re.fullmatch(r"[0-9a-f]{64}", single):
        out["image_sha256"] = single
    in_map = False
    for line in parts[1].splitlines():
        if re.match(r"^image_sha256s:", line):
            in_map = True
            continue
        if in_map:
            m = re.match(r"^\s+(\w+):\s*([0-9a-f]{64})\s*$", line)
            if m:
                out[m.group(1)] = m.group(2)
            elif re.match(r"^\S", line):
                in_map = False
    return out


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

    # FAIL CLOSED on a missing vocabulary: with no 标签.md every tag would
    # pass, which reads as "all tags are fine" when the truth is "nothing
    # was checked" (QA's finding on the first version of this rule).
    if not (vault / "标签.md").exists():
        problems.append("no 标签.md: the tag vocabulary cannot be enforced, so no tag can be trusted")

    template = vault / ANALYSIS_TEMPLATE
    template_keys = frontmatter_keys(template.read_text(encoding="utf-8")) if template.exists() else set()
    if not template_keys:
        problems.append(f"no analysis template at {ANALYSIS_TEMPLATE}, so Dataview columns cannot be validated")

    vocabulary = allowed_tags(vault)
    for note in sorted((vault / "分析").glob("*.md")):
        text = note.read_text(encoding="utf-8")
        keys = frontmatter_keys(text)
        missing = [k for k in REQUIRED_ANALYSIS_KEYS if k not in keys]
        if missing:
            problems.append(f"分析/{note.name}: frontmatter is missing {', '.join(missing)}")

        if not ANALYSIS_FILENAME.match(note.name):
            problems.append(
                f"分析/{note.name}: the name is not <date>-<SYMBOL>-<timeframe>-<id>.md; "
                f"an unsortable name cannot be filtered or joined at review time"
            )

        # The two-layer model is only a model if BOTH layers exist: an
        # analysis whose symbol has no hub page answers "what did I think
        # that day" while "what do I think now" silently has nowhere to live.
        symbol = frontmatter_value(text, "symbol")
        if symbol:
            hub = vault / "标的" / f"{hub_name(symbol)}.md"
            if not hub.exists():
                problems.append(f"分析/{note.name}: no hub page 标的/{hub_name(symbol)}.md for {symbol}; the living layer is missing")
            else:
                links = hub.read_text(encoding="utf-8").count(f"[[分析/{note.stem}")
                if links == 0:
                    problems.append(f"标的/{hub_name(symbol)}.md: no history link to 分析/{note.stem}; the hub cannot find this analysis")
                elif links > 1:
                    problems.append(f"标的/{hub_name(symbol)}.md: {links} links to 分析/{note.stem}; the upsert is not idempotent")

        # Free-form tags are worthless a year later; only 标签.md counts.
        if vocabulary:
            for tag in frontmatter_tags(text):
                if tag not in vocabulary:
                    problems.append(f"分析/{note.name}: tag `{tag}` is not in 标签.md's controlled vocabulary")

        # No section title twice. The real case: a save appended a second
        # `## 链接`, and each half then told a different story about the
        # same question.
        heads = re.findall(r"^## .+$", text, re.M)
        for h in sorted({h for h in heads if heads.count(h) > 1}):
            problems.append(f"分析/{note.name}: the section `{h.strip()}` appears {heads.count(h)} times; one question, one section")

        # The image contract is CONDITIONAL, and both arms are checked --
        # `image_archived: true` with no attachment check was a postcondition
        # in name only (QA's finding).
        archived = frontmatter_value(text, "image_archived")
        aid = frontmatter_value(text, "analysis_id")
        if archived == "true" and aid:
            files = {f.name: f for f in (vault / "附件").glob(f"{aid}-*.png")}
            if not files:
                problems.append(f"分析/{note.name}: image_archived is true but 附件/ holds no {aid}-*.png")
            actual = {name: hashlib.sha256(f.read_bytes()).hexdigest() for name, f in files.items()}
            for slot, want in declared_hashes(text).items():
                if slot == "image_sha256":
                    # The single hash names the PRIMARY image; it must be one
                    # of this analysis's real files, whichever slot it is.
                    if want not in actual.values():
                        problems.append(f"分析/{note.name}: image_sha256 matches none of this analysis's attachments")
                    continue
                f = f"{aid}-{slot}.png"
                if f not in actual:
                    problems.append(f"分析/{note.name}: image_sha256s declares `{slot}` but 附件/{f} does not exist")
                elif actual[f] != want:
                    problems.append(f"分析/{note.name}: 附件/{f} does not match its declared SHA-256; the image has been replaced or corrupted")
        elif archived == "false":
            if "未归档" not in text:
                problems.append(f"分析/{note.name}: image_archived is false but the body never says 未归档; the evidence gap must be stated, not implied")

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
