"""The vault checker has to be able to FAIL, or it is a banner, not a check."""
import shutil
import tempfile
import hashlib
import unittest
from pathlib import Path

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "tradingsignal" / "scripts"))
from vault_check import check

ANALYSIS = """---
analysis_id: aaaaaa
symbol: TEST
timeframe: 1d
as_of: 2026-09-04
methods: [td9]
bias: 看多
outcome: 待观察
image_archived: false
tags:
  - 市场/股票
---
body

图片未归档。
"""

ARCHIVED = """---
analysis_id: cccccc
symbol: TEST
timeframe: 1d
as_of: 2026-09-04
methods: [td9]
bias: 看多
outcome: 待观察
image_archived: true
image_sha256: {main}
image_sha256s:
  td9: {td9}
tags:
  - 市场/股票
---
body
"""

TEMPLATE = """---
analysis_id: 
symbol: 
timeframe: 
as_of: 
methods: []
bias: 
outcome: 
tags:
---
"""

SYMBOL_PAGE = """---
symbol: TEST
---
## 历史分析

- [[分析/2026-09-04-TEST-1d-aaaaaa|2026-09-04]]

```dataview
TABLE as_of AS 截至, methods AS 方法
FROM "分析"
```
"""

TAGS_PAGE = """# 标签

```
市场/股票   市场/加密
```
"""


class VaultCheck(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        for d in ("分析", "标的", "附件", "_模板"):
            (self.dir / d).mkdir()
        (self.dir / "_模板" / "分析.md").write_text(TEMPLATE, encoding="utf-8")
        (self.dir / "分析" / "2026-09-04-TEST-1d-aaaaaa.md").write_text(ANALYSIS, encoding="utf-8")
        (self.dir / "标的" / "TEST.md").write_text(SYMBOL_PAGE, encoding="utf-8")
        (self.dir / "标签.md").write_text(TAGS_PAGE, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_a_clean_vault_passes(self):
        self.assertEqual(check(self.dir), [])

    def test_the_drift_qa_found_fails(self):
        # A Dataview column no frontmatter field provides: `method` vs `methods`.
        page = self.dir / "标的" / "TEST.md"
        page.write_text(page.read_text(encoding="utf-8").replace("methods AS 方法", "method AS 方法"), encoding="utf-8")
        self.assertTrue(any("`method`" in p for p in check(self.dir)), check(self.dir))

    def test_a_missing_directory_fails(self):
        shutil.rmtree(self.dir / "附件")
        self.assertTrue(any("附件" in p for p in check(self.dir)))

    def test_an_analysis_missing_review_fields_fails(self):
        note = self.dir / "分析" / "2026-09-04-TEST-1d-aaaaaa.md"
        note.write_text(note.read_text(encoding="utf-8").replace("as_of: 2026-09-04\n", ""), encoding="utf-8")
        self.assertTrue(any("as_of" in p for p in check(self.dir)))

    def test_a_symbol_page_without_a_plain_link_fails(self):
        # Dataview is optional; the plain link is what a plugin-free vault shows.
        page = self.dir / "标的" / "TEST.md"
        page.write_text(page.read_text(encoding="utf-8").replace("- [[分析/2026-09-04-TEST-1d-aaaaaa|2026-09-04]]\n", ""), encoding="utf-8")
        self.assertTrue(any("plain-Markdown" in p for p in check(self.dir)))


class VaultCheckProcess(unittest.TestCase):
    """The rules added after the first real skill run drifted on all four."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        for d in ("分析", "标的", "附件", "_模板"):
            (self.dir / d).mkdir()
        (self.dir / "_模板" / "分析.md").write_text(TEMPLATE, encoding="utf-8")
        (self.dir / "分析" / "2026-09-04-TEST-1d-aaaaaa.md").write_text(ANALYSIS, encoding="utf-8")
        (self.dir / "标的" / "TEST.md").write_text(SYMBOL_PAGE, encoding="utf-8")
        (self.dir / "标签.md").write_text(TAGS_PAGE, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_the_eth_filename_shape_fails(self):
        # "多周期" is not a timeframe and the id is missing -- the real case.
        (self.dir / "分析" / "2026-09-07-ETHUSDT-多周期.md").write_text(ANALYSIS.replace("TEST", "ETHX"), encoding="utf-8")
        (self.dir / "标的" / "ETHX.md").write_text(SYMBOL_PAGE.replace("TEST", "ETHX").replace("2026-09-04-ETHX-1d-aaaaaa", "2026-09-07-ETHUSDT-多周期"), encoding="utf-8")
        self.assertTrue(any("unsortable" in p for p in check(self.dir)), check(self.dir))

    def test_an_analysis_without_a_hub_page_fails(self):
        # Leon's report: the ETH analysis landed and 标的/ gained nothing.
        (self.dir / "分析" / "2026-09-05-NEWX-1d-bbbbbb.md").write_text(ANALYSIS.replace("TEST", "NEWX"), encoding="utf-8")
        self.assertTrue(any("living layer is missing" in p for p in check(self.dir)))

    def test_a_hub_without_the_backlink_fails(self):
        page = self.dir / "标的" / "TEST.md"
        page.write_text(page.read_text(encoding="utf-8").replace("- [[分析/2026-09-04-TEST-1d-aaaaaa|2026-09-04]]\n", ""), encoding="utf-8")
        self.assertTrue(any("cannot find this analysis" in p for p in check(self.dir)))

    def test_a_tag_outside_the_vocabulary_fails(self):
        note = self.dir / "分析" / "2026-09-04-TEST-1d-aaaaaa.md"
        note.write_text(note.read_text(encoding="utf-8").replace("- 市场/股票", "- 状态/WATCH"), encoding="utf-8")
        self.assertTrue(any("状态/WATCH" in p for p in check(self.dir)))

    def test_a_doubled_hub_link_fails(self):
        # QA: re-saving the same analysis must be idempotent, one link not two.
        page = self.dir / "标的" / "TEST.md"
        s = page.read_text(encoding="utf-8")
        page.write_text(s.replace("- [[分析/2026-09-04-TEST-1d-aaaaaa|2026-09-04]]",
                                  "- [[分析/2026-09-04-TEST-1d-aaaaaa|2026-09-04]]\n- [[分析/2026-09-04-TEST-1d-aaaaaa|again]]"), encoding="utf-8")
        self.assertTrue(any("not idempotent" in p for p in check(self.dir)))

    def test_the_slash_and_venue_suffix_map_to_the_hub_name(self):
        # BTC/USDT lives at 标的/BTC-USDT.md and GBPUSD=X at 标的/GBPUSD.md.
        from vault_check import hub_name
        self.assertEqual(hub_name("BTC/USDT"), "BTC-USDT")
        self.assertEqual(hub_name("GBPUSD=X"), "GBPUSD")


class VaultCheckPostcondition(unittest.TestCase):
    """QA's three false closures: each arm of the image contract, the
    duplicated section, and the vocabulary failing OPEN when 标签.md is gone."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        for d in ("分析", "标的", "附件", "_模板"):
            (self.dir / d).mkdir()
        (self.dir / "_模板" / "分析.md").write_text(TEMPLATE, encoding="utf-8")
        (self.dir / "标的" / "TEST.md").write_text(
            SYMBOL_PAGE.replace("2026-09-04-TEST-1d-aaaaaa", "2026-09-04-TEST-1d-cccccc"), encoding="utf-8")
        (self.dir / "标签.md").write_text(TAGS_PAGE, encoding="utf-8")
        self.png = b"not really a png but bytes are bytes"
        (self.dir / "附件" / "cccccc-td9.png").write_bytes(self.png)
        self.hash = hashlib.sha256(self.png).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def note(self, main=None, td9=None):
        (self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md").write_text(
            ARCHIVED.format(main=main or self.hash, td9=td9 or self.hash), encoding="utf-8")

    def test_archived_with_matching_hashes_passes(self):
        self.note()
        self.assertEqual(check(self.dir), [])

    def test_archived_with_a_missing_attachment_fails(self):
        self.note()
        (self.dir / "附件" / "cccccc-td9.png").unlink()
        found = check(self.dir)
        self.assertTrue(any("does not exist" in p or "holds no" in p for p in found), found)

    def test_archived_with_a_wrong_hash_fails(self):
        # The image was replaced underneath its declaration.
        self.note(td9="0" * 64)
        self.assertTrue(any("replaced or corrupted" in p for p in check(self.dir)))

    def test_the_single_hash_must_name_a_real_attachment(self):
        self.note(main="1" * 64)
        self.assertTrue(any("matches none" in p for p in check(self.dir)))

    def test_unarchived_must_say_so_in_the_body(self):
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        note.write_text(ARCHIVED.format(main=self.hash, td9=self.hash)
                        .replace("image_archived: true", "image_archived: false")
                        .replace("image_sha256: " + self.hash, "image_sha256: null"), encoding="utf-8")
        self.assertTrue(any("未归档" in p for p in check(self.dir)))

    def test_a_duplicated_section_fails(self):
        # The real ETH case: a save appended a second `## 链接`.
        self.note()
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        note.write_text(note.read_text(encoding="utf-8") + "\n## 链接\n\na\n\n## 链接\n\nb\n", encoding="utf-8")
        self.assertTrue(any("one question, one section" in p for p in check(self.dir)))

    def test_an_app_link_without_a_tab_fails(self):
        # QA's NVDA case: a "view the VCP analysis" link that opens the
        # default view because it never named a tab.
        self.note()
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        note.write_text(note.read_text(encoding="utf-8")
                        + "\n[查看最新分析](https://tradingsignal.pro/app?symbol=TEST&timeframe=1d)\n", encoding="utf-8")
        self.assertTrue(any("not a deep link" in p for p in check(self.dir)))

    def test_an_app_link_with_an_unknown_tab_fails(self):
        self.note()
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        note.write_text(note.read_text(encoding="utf-8")
                        + "\n[查看](https://tradingsignal.pro/app?symbol=TEST&timeframe=1d&tab=demark)\n", encoding="utf-8")
        self.assertTrue(any("not a tab the product has" in p for p in check(self.dir)))

    def test_a_complete_deep_link_passes(self):
        self.note()
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        note.write_text(note.read_text(encoding="utf-8")
                        + "\n[查看 TEST 的最新 VCP 分析](https://tradingsignal.pro/app?market=stock&symbol=TEST&timeframe=1d&tab=vcp)\n", encoding="utf-8")
        self.assertEqual(check(self.dir), [])

    def test_a_missing_vocabulary_fails_closed(self):
        self.note()
        (self.dir / "标签.md").unlink()
        self.assertTrue(any("no 标签.md" in p for p in check(self.dir)))


if __name__ == "__main__":
    unittest.main()
