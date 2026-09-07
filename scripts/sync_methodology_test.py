"""The sync's closed loop: fetch -> write -> the checker turns green.

QA's finding: the previous version was model instructions plus a stale
detector, so nothing proved a stale vault actually becomes current. These
drive the real sync function with a fake source and then assert the real
checker's verdict.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "tradingsignal" / "scripts"))
from sync_methodology import TOPICS, needed, note_path, sync  # noqa: E402
from vault_check import check_methods, packaged_skill_version  # noqa: E402

V1, V2 = "0.1.31", "0.1.32"


class MethodologySync(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / "方法").mkdir()
        self.texts = {t: f"definition of {t}, release one" for t in TOPICS}

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_an_empty_vault_needs_every_topic_and_the_sync_fills_it(self):
        self.assertEqual(needed(self.dir, V1), list(TOPICS))
        out = sync(self.dir, V1, self.texts, "2026-09-07")
        self.assertTrue(all(v == "created" for v in out.values()), out)
        self.assertEqual(needed(self.dir, V1), [])

    def test_a_stale_vault_becomes_current_and_the_checker_agrees(self):
        """The end-to-end QA asked for: stale -> sync -> checker green."""
        sync(self.dir, "0.0.9", self.texts, "2026-09-01")
        # The checker compares against the PACKAGED release, so use it.
        current = packaged_skill_version()
        self.assertTrue(any("re-download" in p for p in check_methods(self.dir)))
        self.assertEqual(needed(self.dir, current), list(TOPICS))
        sync(self.dir, current, self.texts, "2026-09-07")
        self.assertEqual(check_methods(self.dir), [])

    def test_unchanged_text_bumps_the_version_without_a_snapshot(self):
        sync(self.dir, V1, self.texts, "2026-09-01")
        out = sync(self.dir, V2, self.texts, "2026-09-07")
        self.assertTrue(all("unchanged" in v for v in out.values()), out)
        self.assertFalse((self.dir / "方法" / "历史").exists(),
                         "an identical definition must not spawn a snapshot per release")

    def test_changed_text_snapshots_the_OLD_definition_before_replacing_it(self):
        # The semantic break QA caught: without this, an analysis written
        # under V1 would read V2's definition and nobody could tell.
        sync(self.dir, V1, self.texts, "2026-09-01")
        changed = dict(self.texts, vcp="definition of vcp, RELEASE TWO")
        out = sync(self.dir, V2, changed, "2026-09-07")
        self.assertIn("snapshot", out["vcp"])
        snap = self.dir / "方法" / "历史" / f"VCP-{V1}.md"
        self.assertTrue(snap.exists(), "the outgoing definition was not preserved")
        self.assertIn("release one", snap.read_text(encoding="utf-8"))
        self.assertIn("RELEASE TWO", note_path(self.dir, "vcp").read_text(encoding="utf-8"))
        # Topics that did not change get no snapshot.
        self.assertFalse((self.dir / "方法" / "历史" / f"缠论-{V1}.md").exists())

    def test_a_snapshot_is_never_rewritten(self):
        sync(self.dir, V1, self.texts, "2026-09-01")
        sync(self.dir, V2, dict(self.texts, vcp="two"), "2026-09-07")
        snap = self.dir / "方法" / "历史" / f"VCP-{V1}.md"
        before = snap.read_text(encoding="utf-8")
        # A later run that somehow re-reports V1 must not overwrite history.
        sync(self.dir, V1, dict(self.texts, vcp="three"), "2026-09-08")
        sync(self.dir, V2, dict(self.texts, vcp="four"), "2026-09-09")
        self.assertEqual(snap.read_text(encoding="utf-8"), before)

    def test_a_topic_the_skill_does_not_serve_is_refused(self):
        out = sync(self.dir, V1, {"astrology": "no"}, "2026-09-07")
        self.assertIn("refused", out["astrology"])
        self.assertFalse((self.dir / "方法" / "astrology.md").exists())

    def test_needed_asks_only_for_what_is_missing_or_stale(self):
        sync(self.dir, V1, self.texts, "2026-09-01")
        self.assertEqual(needed(self.dir, V1), [])
        note_path(self.dir, "chan").unlink()
        self.assertEqual(needed(self.dir, V1), ["chan"])


if __name__ == "__main__":
    unittest.main()
