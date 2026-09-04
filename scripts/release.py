#!/usr/bin/env python3
"""Synchronize and verify the TradingSignal Skill release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "tradingsignal"
PLUGIN_SKILL = ROOT / "plugins" / "tradingsignal" / "skills" / "tradingsignal"
PLUGIN_MANIFEST = ROOT / "plugins" / "tradingsignal" / ".codex-plugin" / "plugin.json"
CLAUDE_PLUGIN_MANIFEST = ROOT / "plugins" / "tradingsignal" / ".claude-plugin" / "plugin.json"
RELEASE_MANIFEST = ROOT / "release.json"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
VERSION_LINE = re.compile(r'(?m)^([ \t]*version:[ \t]*)["\']?([^"\'\s]+)["\']?[ \t]*$')


def skill_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"invalid frontmatter in {path.relative_to(ROOT)}")
    match = VERSION_LINE.search(parts[1])
    if not match:
        raise ValueError(f"missing metadata.version in {path.relative_to(ROOT)}")
    return match.group(2)


def set_skill_version(path: Path, version: str) -> None:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"invalid frontmatter in {path.relative_to(ROOT)}")
    if not VERSION_LINE.search(parts[1]):
        raise ValueError(f"missing metadata.version in {path.relative_to(ROOT)}")
    parts[1] = VERSION_LINE.sub(lambda m: f'{m.group(1)}"{version}"', parts[1], count=1)
    path.write_text("---".join(parts), encoding="utf-8")


def tree_entries(path: Path) -> list[tuple[str, str]]:
    return [
        (str(file.relative_to(path)), hashlib.sha256(file.read_bytes()).hexdigest())
        for file in sorted(path.rglob("*"))
        if file.is_file()
    ]


def tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for relative, file_hash in tree_entries(path):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def set_release(version: str) -> None:
    if not SEMVER.fullmatch(version):
        raise ValueError(f"invalid semantic version: {version}")

    if RELEASE_MANIFEST.exists():
        previous = json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))
        if previous.get("version") == version:
            if previous.get("skillDigest") != tree_digest(SOURCE):
                raise ValueError("Skill content changed; choose a new version instead of reusing the published one")
            if "packageDigest" in previous and previous.get("packageDigest") != tree_digest(
                ROOT / "plugins" / "tradingsignal"
            ):
                raise ValueError("Plugin package changed; choose a new version instead of reusing the published one")

    set_skill_version(SOURCE / "SKILL.md", version)
    if PLUGIN_SKILL.exists():
        shutil.rmtree(PLUGIN_SKILL)
    shutil.copytree(SOURCE, PLUGIN_SKILL)

    plugin = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    plugin["version"] = version
    write_json(PLUGIN_MANIFEST, plugin)
    claude_plugin = json.loads(CLAUDE_PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    claude_plugin["version"] = version
    write_json(CLAUDE_PLUGIN_MANIFEST, claude_plugin)
    write_json(
        RELEASE_MANIFEST,
        {
            "name": "tradingsignal",
            "version": version,
            "skillDigest": tree_digest(SOURCE),
            "packageDigest": tree_digest(ROOT / "plugins" / "tradingsignal"),
        },
    )


def check_release() -> None:
    plugin = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    claude_plugin = json.loads(CLAUDE_PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    release = json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))
    versions = {
        "source Skill": skill_version(SOURCE / "SKILL.md"),
        "plugin Skill": skill_version(PLUGIN_SKILL / "SKILL.md"),
        "plugin manifest": plugin.get("version"),
        "Claude plugin manifest": claude_plugin.get("version"),
        "release manifest": release.get("version"),
    }
    if len(set(versions.values())) != 1:
        raise ValueError(f"release versions differ: {versions}")
    version = next(iter(versions.values()))
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        raise ValueError(f"invalid semantic version: {version}")
    if tree_entries(SOURCE) != tree_entries(PLUGIN_SKILL):
        raise ValueError("source Skill and packaged plugin Skill differ")
    actual_digest = tree_digest(SOURCE)
    if release.get("skillDigest") != actual_digest:
        raise ValueError("Skill content changed without a release version bump")
    actual_package_digest = tree_digest(ROOT / "plugins" / "tradingsignal")
    if release.get("packageDigest") != actual_package_digest:
        raise ValueError("Plugin package changed without a release version bump")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--set", metavar="VERSION", dest="version")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.version:
            set_release(args.version)
        check_release()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"release check failed: {exc}", file=sys.stderr)
        return 1
    print(f"TradingSignal Skill release {skill_version(SOURCE / 'SKILL.md')} is synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
