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
from urllib.parse import parse_qs, unquote, urlparse

REQUIRED_DIRS = ["分析", "标的", "附件"]
# `skill_version` is required: without it an analysis cannot choose which
# methodology definition it was made under, which is the whole point of
# keeping the history (QA's finding).
REQUIRED_ANALYSIS_KEYS = ["analysis_id", "symbol", "timeframe", "as_of", "bias", "outcome", "tags", "skill_version"]
ANALYSIS_TEMPLATE = Path("_模板") / "分析.md"
DATAVIEW_BLOCK = re.compile(r"```dataview\n(.*?)```", re.S)
TABLE_LINE = re.compile(r"^\s*TABLE\s+(.+)$", re.M | re.I)

# One analysis, one name: date, symbol (letters/digits only), the DECISION
# timeframe, and the analysis id. A multi-timeframe study still decides on
# one timeframe, and that one goes in the name; "多周期" is not a timeframe
# and cannot be sorted, filtered or joined against anything.
ANALYSIS_FILENAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[A-Za-z0-9]+-[A-Za-z0-9]+-[0-9a-f]{6}\.md$")

# The product's method-page URL contract, live since task #45 shipped: an
# /app link names its chart completely or it is not a deep link. A link
# without `tab=` opens whatever the default is -- which is how the first
# Codex run produced a "view the VCP analysis" link that did not open VCP.
APP_TABS = {"indicators", "levels", "trend", "fib", "chan", "td9", "vcp", "wyckoff"}
# A link is markdown, so its TEXT is available and is what the reader trusts.
APP_LINK = re.compile(r"\[([^\]]*)\]\((https?://[^\s)]*?/app\?[^\s)]*)\)|(?<![\(\[])(https?://[^\s)\]>]*?/app\?[^\s)\]>]*)")

# What a method is called, in either language, and the tab that shows it.
# The link text promises a method; the tab decides what opens. When they
# disagree the text is a lie the reader cannot see (QA's NVDA case, one
# level deeper).
METHOD_WORDS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bVCP\b", re.I), "vcp"),
    (re.compile(r"\bTD ?9\b|\bDeMark\b|TD ?序列", re.I), "td9"),
    (re.compile(r"\bChan\b|缠论", re.I), "chan"),
    (re.compile(r"\bWyckoff\b|威科夫", re.I), "wyckoff"),
    (re.compile(r"支撑阻力|\blevels?\b|\bsupport\b", re.I), "levels"),
    (re.compile(r"斐波那契|\bfibonacci\b|\bfib\b", re.I), "fib"),
]

# Which markets each asset class may name, so a link cannot open the right
# symbol under the wrong tab group.
# An Obsidian save SHOWS its evidence. `![[附件/x.png]]` is the embed; the
# link that must sit under it names the same method the image draws.
EMBED = re.compile(r"!\[\[附件/([^\]|]+?)(?:\|[^\]]*)?\]\]")
METHOD_TABS = {"vcp", "td9", "chan", "wyckoff", "levels", "fib"}

# Every slot a note may archive, and the tab its link must open. A CLOSED
# set: a slot outside it has no implied method, so it cannot be checked by
# guessing -- the note must bind it with `primary_method` or the save fails.
# The first version only listed the six method slots, which left `trend`,
# `indicators` and `main` free to carry any tab at all.
SLOT_TAB = {
    "levels": "levels", "vcp": "vcp", "chan": "chan", "td9": "td9",
    "wyckoff": "wyckoff", "fib": "fib", "trend": "trend", "indicators": "indicators",
}
TF_WORDS = re.compile(r"\b(1m|5m|15m|30m|1h|2h|4h|1d|1w|1mo)\b|(\d+)\s*小时|日线|周线|月线")
TF_ZH = {"日线": "1d", "周线": "1w", "月线": "1mo"}

# The engines whose methodology the vault keeps. `get_methodology(topic=…)`
# returns each one verbatim; the vault stores what it returned, not a
# paraphrase, because analyses cite these notes as the definition they used.
METHOD_TOPICS = ("vcp", "chan", "td9", "wyckoff", "levels", "fib")

MARKET_FOR_CLASS = {
    "equity_us": "stock", "equity_intl": "stock", "crypto": "crypto",
    "fx": "forex", "commodity_spot": "commodity", "commodity_future": "commodity",
    "index": "stock", "futures": "commodity",
}


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
    if not m:
        return None
    # A trailing YAML comment is not part of the value. Without this the
    # comment travelled into the comparison and a correctly-bound field read
    # as an unknown tab.
    return re.sub(r"\s+#.*$", "", m.group(1)).strip().strip("\"'")


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


def packaged_skill_version() -> str | None:
    """This checker ships INSIDE the skill, so it can read its own release.

    That is what makes "is the methodology current?" answerable offline: the
    version beside the script is the version whose methodology the vault
    should be holding.
    """
    skill = Path(__file__).resolve().parent.parent / "SKILL.md"
    if not skill.exists():
        return None
    m = re.search(r"^\s*version:\s*[\"']?([0-9]+\.[0-9]+\.[0-9]+)", skill.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def check_methods(vault: Path) -> list[str]:
    """`方法/` holds the methodology, pinned to the release that produced it.

    A note with no version cannot be told apart from a current one, and a
    stale note silently redefines what an old analysis meant by "VCP".
    An ABSENT 方法/ directory is not an error -- a vault gains it the first
    time methodology is downloaded.
    """
    problems: list[str] = []
    d = vault / "方法"
    if not d.is_dir():
        return problems
    current = packaged_skill_version()
    # `方法/历史/` holds outgoing definitions, pinned to the release that
    # wrote them. They are SUPPOSED to be old -- checking them against the
    # installed release would report every snapshot as stale, which is the
    # opposite of what they are for.
    for snap in sorted((d / "历史").glob("*.md")) if (d / "历史").is_dir() else []:
        text = snap.read_text(encoding="utf-8")
        version = frontmatter_value(text, "skill_version")
        stem_version = snap.stem.rsplit("-", 1)[-1]
        if not version:
            problems.append(f"方法/历史/{snap.name}: no `skill_version`; a snapshot that cannot say which release it froze is not evidence")
        elif version != stem_version:
            problems.append(f"方法/历史/{snap.name}: frontmatter says {version} but the filename says {stem_version}")
        elif current and version == current:
            problems.append(f"方法/历史/{snap.name}: snapshots the INSTALLED release; history is for definitions that have been replaced")
    for note in sorted(d.glob("*.md")):
        # A directory README explains the directory; it is not a synced
        # topic note and has no release to be current with.
        if note.stem.upper() == "README":
            continue
        text = note.read_text(encoding="utf-8")
        topic = frontmatter_value(text, "topic")
        version = frontmatter_value(text, "skill_version")
        if not topic:
            problems.append(f"方法/{note.name}: no `topic`; the note cannot be matched to a get_methodology topic")
        elif topic not in METHOD_TOPICS:
            problems.append(f"方法/{note.name}: topic `{topic}` is not one the skill serves ({', '.join(METHOD_TOPICS)})")
        if not version:
            problems.append(f"方法/{note.name}: no `skill_version`; a methodology note that cannot say which release wrote it cannot be told from a current one")
        elif current and version != current:
            problems.append(f"方法/{note.name}: written by skill {version}, the installed skill is {current}; re-download this topic")
    return problems


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
        # Every /app link is judged against the LIVE URL contract: symbol,
        # timeframe and a tab from the closed set, or it silently opens some
        # other view while its text promises a method (QA's NVDA case).
        note_tf = frontmatter_value(text, "timeframe")
        note_market = frontmatter_value(text, "market")
        note_class = frontmatter_value(text, "asset_class")
        context_tfs = {t.strip() for t in (frontmatter_value(text, "context_timeframes") or "").strip("[]").split(",") if t.strip()}
        note_methods = {m.strip() for m in (frontmatter_value(text, "methods") or "").strip("[]").split(",") if m.strip()}

        # The version must RESOLVE, not merely be present. Only once the
        # vault has an index -- before the first methodology sync there is
        # nothing to resolve against, and demanding it would be noise.
        note_version = frontmatter_value(text, "skill_version")
        idx_file = vault / "方法" / "版本索引.json"
        if note_version and note_version != "null" and idx_file.exists():
            import json as _json
            idx = _json.loads(idx_file.read_text(encoding="utf-8"))
            for topic in sorted(note_methods):
                if topic in idx and note_version not in idx[topic]:
                    problems.append(
                        f"分析/{note.name}: skill_version {note_version} has no entry for `{topic}`;"
                        f" this analysis cannot be read against the definition it used"
                    )


        for label, url, bare in APP_LINK.findall(text):
            link, why_text = (url, label) if url else (bare, "")
            q = parse_qs(urlparse(link).query)
            missing_q = [k for k in ("market", "symbol", "timeframe", "tab") if k not in q]
            if missing_q:
                problems.append(f"分析/{note.name}: /app link missing {', '.join(missing_q)}; without them it is not a deep link, it is a guess")
                continue
            tab = q["tab"][0]
            if tab not in APP_TABS:
                problems.append(f"分析/{note.name}: /app link tab `{tab}` is not a tab the product has")

            # The link must open THIS note's instrument. A complete-looking
            # link to another symbol is the worst kind: it passes a shape
            # check and shows the reader a different chart.
            if symbol and unquote(q["symbol"][0]) != symbol:
                problems.append(f"分析/{note.name}: /app link opens {unquote(q['symbol'][0])}, but this analysis is about {symbol}")
            if note_market and q["market"][0] != note_market:
                problems.append(f"分析/{note.name}: /app link says market={q['market'][0]}, the note says {note_market}")
            elif note_class and MARKET_FOR_CLASS.get(note_class) and q["market"][0] != MARKET_FOR_CLASS[note_class]:
                problems.append(f"分析/{note.name}: /app link says market={q['market'][0]}, but asset_class {note_class} belongs to {MARKET_FOR_CLASS[note_class]}")

            # The decision timeframe, or one this note DECLARES as context.
            # A multi-timeframe study legitimately links its background
            # timeframe -- but it has to have said so in front matter.
            if note_tf and q["timeframe"][0] != note_tf and q["timeframe"][0] not in context_tfs:
                problems.append(
                    f"分析/{note.name}: /app link opens {q['timeframe'][0]}, but this analysis is about {note_tf}"
                    + (" and declares no other timeframe in context_timeframes" if not context_tfs else f" (context: {', '.join(sorted(context_tfs))})")
                )

            # The text promises a method; the tab must be that method's.
            for pattern, want_tab in METHOD_WORDS:
                if pattern.search(why_text):
                    if tab != want_tab:
                        problems.append(f"分析/{note.name}: the link text promises {want_tab} but tab={tab}; the reader cannot see the difference")
                    break
            # A method tab must be a method this analysis actually ran.
            if tab in {"vcp", "td9", "chan", "wyckoff", "levels", "fib"} and note_methods and tab not in note_methods:
                problems.append(f"分析/{note.name}: /app link opens {tab}, which is not among this analysis's methods ({', '.join(sorted(note_methods))})")

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
            # An archived image must be SHOWN, and the link under it must
            # open the method that image draws. A picture the reader has to
            # go looking for is not evidence in a note.
            embedded = {m for m in EMBED.findall(text)}
            declared_files = {f"{aid}-{slot}.png" for slot in declared_hashes(text) if slot != "image_sha256"}
            for name in sorted(files):
                if name in declared_files and name not in embedded:
                    problems.append(f"分析/{note.name}: 附件/{name} is declared and archived but never embedded; an Obsidian note shows its evidence")
                elif name not in declared_files and name not in embedded:
                    # Neither declared nor shown: a leftover from an earlier
                    # save. Named rather than deleted -- this vault is not
                    # versioned, so removing evidence is not mine to do.
                    problems.append(f"分析/{note.name}: 附件/{name} is in the vault but this note neither declares nor embeds it; declare it or remove it")
            lines = text.splitlines()
            # Where does the links section start? Images belong with the
            # reason they support; a picture filed under 链接 is a picture
            # nobody reads next to the sentence it proves.
            link_section = next((i for i, l in enumerate(lines) if l.strip().startswith("## 链接")), len(lines))
            for i, line in enumerate(lines):
                m = EMBED.search(line)
                if not m:
                    continue
                if i > link_section:
                    problems.append(f"分析/{note.name}: {m.group(1)} is embedded under 链接; an image belongs at the reason it supports, not pooled with the links")
                    continue
                # The nearest heading above it IS the reason it supports. If
                # that heading names a method, it must be this image's own:
                # "not under 链接" was satisfied by every other section, so a
                # TD9 chart could sit under `## VCP` and pass (QA's case).
                head = next((lines[j] for j in range(i, -1, -1) if lines[j].startswith("## ")), "")
                head_method = next((tab for pat, tab in METHOD_WORDS if pat.search(head)), None)
                img_method = SLOT_TAB.get(m.group(1).rsplit("-", 1)[-1].removesuffix(".png"))
                if head_method and img_method and head_method != img_method:
                    problems.append(
                        f"分析/{note.name}: {m.group(1)} draws {img_method} but sits under `{head.strip()}`;"
                        f" an image belongs in the section that reasons about it"
                    )
                    continue
                slot = m.group(1).rsplit("-", 1)[-1].removesuffix(".png")
                near = " ".join(lines[i + 1:i + 4])
                links = [u or b for _, u, b in APP_LINK.findall(near)]
                if not links:
                    problems.append(f"分析/{note.name}: the image {m.group(1)} has no method link directly beneath it")
                    continue
                q = parse_qs(urlparse(links[0]).query)
                # What method does THIS image draw? From the closed slot map,
                # or -- for a slot the map does not name, `main` included --
                # from an explicit `primary_method`. No binding, no pass.
                want_tab = SLOT_TAB.get(slot)
                if want_tab is None:
                    want_tab = frontmatter_value(text, "primary_method")
                    if not want_tab:
                        problems.append(
                            f"分析/{note.name}: {m.group(1)} uses slot `{slot}`, which names no method; "
                            f"bind it with primary_method or rename the file to a known slot ({', '.join(sorted(SLOT_TAB))})"
                        )
                        continue
                    if want_tab not in APP_TABS:
                        problems.append(f"分析/{note.name}: primary_method `{want_tab}` is not a tab the product has")
                        continue
                if q.get("tab", [""])[0] != want_tab:
                    problems.append(f"分析/{note.name}: the link under {m.group(1)} opens tab={q.get('tab', [''])[0]}, but the image draws {want_tab}")
                # A caption naming a timeframe binds the link to it: a 4h
                # image may not carry a 1d link.
                cap = TF_WORDS.search(line)
                if cap and q.get("timeframe"):
                    want = cap.group(1) or (f"{cap.group(2)}h" if cap.group(2) else TF_ZH.get(cap.group(0), ""))
                    if want and q["timeframe"][0] != want:
                        problems.append(f"分析/{note.name}: the image caption says {want} but its link opens {q['timeframe'][0]}")
        elif archived == "false":
            if "未归档" not in text:
                problems.append(f"分析/{note.name}: image_archived is false but the body never says 未归档; the evidence gap must be stated, not implied")
            # Stating the gap makes the record HONEST; it does not make the
            # save complete. A vault write the user asked for owes at least
            # one archived, embedded, linked chart.
            problems.append(f"分析/{note.name}: 未完整保存 — no chart archived; an Obsidian save owes at least one embedded, hash-verified image with its method link")

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
    problems.extend(check_methods(vault))
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
