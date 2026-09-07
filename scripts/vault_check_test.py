"""The vault checker has to be able to FAIL, or it is a banner, not a check."""
import shutil
import tempfile
import unittest
from pathlib import Path

from vault_check import check

ANALYSIS = """---
analysis_id: aaaaaa
symbol: TEST
timeframe: 1d
as_of: 2026-09-04
methods: [td9]
bias: 看多
outcome: 待观察
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


class VaultCheck(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        for d in ("分析", "标的", "附件", "_模板"):
            (self.dir / d).mkdir()
        (self.dir / "_模板" / "分析.md").write_text(TEMPLATE, encoding="utf-8")
        (self.dir / "分析" / "2026-09-04-TEST-1d-aaaaaa.md").write_text(ANALYSIS, encoding="utf-8")
        (self.dir / "标的" / "TEST.md").write_text(SYMBOL_PAGE, encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
