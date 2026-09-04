#!/usr/bin/env python3
"""Behavioral tests for the release synchronizer."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns(".git"))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_release(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "scripts/release.py", *args],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )

    def mutate_both_skill_copies(self) -> None:
        relative = Path("references/opportunity-scan.md")
        for base in (
            self.repo / "skills" / "tradingsignal",
            self.repo / "plugins" / "tradingsignal" / "skills" / "tradingsignal",
        ):
            with (base / relative).open("a", encoding="utf-8") as file:
                file.write("\nrelease mutation\n")

    def test_checked_release_passes(self) -> None:
        self.assertEqual(self.run_release("--check").returncode, 0)

    def test_changed_content_fails_digest_check(self) -> None:
        self.mutate_both_skill_copies()
        result = self.run_release("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("without a release version bump", result.stderr)

    def test_changed_content_cannot_reuse_version(self) -> None:
        source = self.repo / "skills" / "tradingsignal" / "references" / "opportunity-scan.md"
        with source.open("a", encoding="utf-8") as file:
            file.write("\nrelease mutation\n")
        result = self.run_release("--set", "0.1.2")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("choose a new version", result.stderr)

    def test_new_version_updates_every_release_surface(self) -> None:
        source = self.repo / "skills" / "tradingsignal" / "references" / "opportunity-scan.md"
        with source.open("a", encoding="utf-8") as file:
            file.write("\nrelease mutation\n")
        self.assertEqual(self.run_release("--set", "0.1.3").returncode, 0)
        self.assertEqual(self.run_release("--check").returncode, 0)
        plugin = json.loads(
            (self.repo / "plugins" / "tradingsignal" / ".codex-plugin" / "plugin.json").read_text()
        )
        release = json.loads((self.repo / "release.json").read_text())
        self.assertEqual(plugin["version"], "0.1.3")
        self.assertEqual(release["version"], "0.1.3")
        self.assertIn(
            'version: "0.1.3"',
            (self.repo / "skills" / "tradingsignal" / "SKILL.md").read_text(),
        )


if __name__ == "__main__":
    unittest.main()
