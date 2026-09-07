#!/usr/bin/env python3
"""Bring `方法/` up to the installed release, keeping what older notes meant.

The model's only job is to call `get_methodology(topic=…)` for the topics
this script asks for and hand back the text. Everything that DECIDES
anything is here, so the sync is executable and has criteria -- rather than
a list of steps a model may or may not have followed.

The rule that makes review possible:

  - `方法/<TOPIC>.md` mirrors the INSTALLED release.
  - When a topic's text CHANGES, the outgoing note is copied to
    `方法/历史/<TOPIC>-<its version>.md` before being replaced. That file is
    never rewritten, so an analysis carrying `skill_version: 0.1.12` can be
    read against the definition that release actually used.
  - When the text is unchanged, no snapshot is written -- only the version
    is bumped. A snapshot per release regardless of content would fill the
    vault with identical files and make "did the methodology change?"
    unanswerable by looking.

Usage:
    sync_methodology.py <vault> <version> <fetched.json>
where fetched.json is {"vcp": "...text...", "chan": "...", ...}. Topics the
file does not carry are left alone; `--needed` prints which topics are
missing or stale so only those need fetching.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TOPICS = ("vcp", "chan", "td9", "wyckoff", "levels", "fib")
FILENAME = {"vcp": "VCP", "chan": "缠论", "td9": "TD9", "wyckoff": "威科夫", "levels": "支撑阻力", "fib": "斐波那契"}


def _front(text: str, key: str) -> str | None:
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    m = re.search(rf"^{key}:\s*(.+?)\s*$", parts[1], re.M)
    return re.sub(r"\s+#.*$", "", m.group(1)).strip() if m else None


def _body(text: str) -> str:
    parts = text.split("---", 2)
    return parts[2].strip() if len(parts) >= 3 else text.strip()


def note_path(vault: Path, topic: str) -> Path:
    return vault / "方法" / f"{FILENAME[topic]}.md"


def index_path(vault: Path) -> Path:
    return vault / "方法" / "版本索引.json"


def load_index(vault: Path) -> dict[str, dict[str, str]]:
    p = index_path(vault)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_index(vault: Path, idx: dict[str, dict[str, str]]) -> None:
    index_path(vault).write_text(json.dumps(idx, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve(vault: Path, topic: str, version: str) -> Path | None:
    """Which file holds what `version` meant by `topic`?

    EVERY release the sync has seen gets an entry, including releases whose
    text was identical to the one before. Without that, the chain QA found
    breaks: V1 creates, V2 bumps with no snapshot, V3 changes and snapshots
    the outgoing file as `TOPIC-V2.md` -- and an analysis stamped V1 resolves
    to nothing, even though V1's definition is preserved inside that very
    file. Identical text is still a distinct release identity.
    """
    target = load_index(vault).get(topic, {}).get(version)
    if not target:
        return None
    p = vault / "方法" / target
    return p if p.exists() else None


def needed(vault: Path, version: str) -> list[str]:
    """Topics whose note is missing or written by another release."""
    out = []
    for t in TOPICS:
        p = note_path(vault, t)
        if not p.exists() or _front(p.read_text(encoding="utf-8"), "skill_version") != version:
            out.append(t)
    return out


def render(topic: str, version: str, body: str, updated: str) -> str:
    return (
        "---\n"
        f"topic: {topic}\n"
        f"skill_version: {version}\n"
        f"updated: {updated}\n"
        "source: get_methodology\n"
        "---\n\n"
        "> 由 skill 自动同步，请勿手改。改动会在下次同步时被覆盖。\n\n"
        f"{body.strip()}\n"
    )


def sync(vault: Path, version: str, fetched: dict[str, str], updated: str) -> dict[str, str]:
    """Apply the fetched texts. Returns what happened, per topic."""
    (vault / "方法").mkdir(parents=True, exist_ok=True)
    idx = load_index(vault)
    result: dict[str, str] = {}
    for topic, body in fetched.items():
        if topic not in TOPICS:
            result[topic] = "refused: not a topic this skill serves"
            continue
        p = note_path(vault, topic)
        here = idx.setdefault(topic, {})
        current_name = f"{FILENAME[topic]}.md"
        if not p.exists():
            p.write_text(render(topic, version, body, updated), encoding="utf-8")
            here[version] = current_name
            result[topic] = "created"
            continue
        old = p.read_text(encoding="utf-8")
        old_version = _front(old, "skill_version") or "unknown"
        if _body(old).split("\n\n", 1)[-1].strip() == body.strip():
            # Same definition under a new release: bump, do not snapshot --
            # but the release still gets an index entry, pointing at the same
            # file, so it stays addressable.
            p.write_text(render(topic, version, body, updated), encoding="utf-8")
            here[version] = current_name
            result[topic] = "unchanged (version bumped)"
            continue
        hist = vault / "方法" / "历史"
        hist.mkdir(exist_ok=True)
        snap = hist / f"{FILENAME[topic]}-{old_version}.md"
        if not snap.exists():                       # immutable once written
            snap.write_text(old, encoding="utf-8")
        # Every release that pointed at the CURRENT file was pointing at the
        # text now frozen in this snapshot, so they all follow it. This is
        # what keeps an older, identical release resolvable.
        for v, target in list(here.items()):
            if target == current_name:
                here[v] = f"历史/{snap.name}"
        here[version] = current_name
        p.write_text(render(topic, version, body, updated), encoding="utf-8")
        result[topic] = f"changed (snapshot {snap.name})"
    save_index(vault, idx)
    return result


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[2] == "--needed":
        vault = Path(sys.argv[1])
        version = sys.argv[3] if len(sys.argv) > 3 else ""
        print(json.dumps(needed(vault, version)))
        return 0
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    vault, version, fetched_file = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    from datetime import date
    out = sync(vault, version, json.loads(fetched_file.read_text(encoding="utf-8")), date.today().isoformat())
    for topic, what in sorted(out.items()):
        print(f"{topic}: {what}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
