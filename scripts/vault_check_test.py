"""The vault checker has to be able to FAIL, or it is a banner, not a check."""
import shutil
import tempfile
import hashlib
import unittest
from pathlib import Path

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "tradingsignal" / "scripts"))
from vault_check import check, check_methods

ANALYSIS = """---
analysis_id: aaaaaa
symbol: TEST
market: stock
timeframe: 1d
skill_version: 0.1.30
as_of: 2026-09-04
methods: [td9]
bias: 看多
outcome: 待观察
image_archived: true
image_sha256s:
  td9: {td9}
tags:
  - 市场/股票
---
body

![[附件/aaaaaa-td9.png]]

[查看 TEST 的最新 TD9 分析](https://tradingsignal.pro/app?market=stock&symbol=TEST&timeframe=1d&tab=td9)
"""

ARCHIVED = """---
analysis_id: cccccc
symbol: TEST
market: stock
timeframe: 1d
skill_version: 0.1.30
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

![[附件/cccccc-td9.png]]

[查看 TEST 的最新 TD9 分析](https://tradingsignal.pro/app?market=stock&symbol=TEST&timeframe=1d&tab=td9)
"""

TEMPLATE = """---
analysis_id: 
symbol: 
timeframe: 
as_of: 
skill_version: 
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
        png = b"a png, for hashing purposes"
        (self.dir / "附件" / "aaaaaa-td9.png").write_bytes(png)
        (self.dir / "分析" / "2026-09-04-TEST-1d-aaaaaa.md").write_text(
            ANALYSIS.format(td9=hashlib.sha256(png).hexdigest()), encoding="utf-8")
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

    def test_an_analysis_without_a_skill_version_fails(self):
        # QA: without it the note cannot select the methodology it used.
        note = self.dir / "分析" / "2026-09-04-TEST-1d-aaaaaa.md"
        note.write_text(note.read_text(encoding="utf-8").replace("skill_version: 0.1.30\n", ""), encoding="utf-8")
        self.assertTrue(any("skill_version" in p for p in check(self.dir)))

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
        (self.dir / "分析" / "2026-09-04-TEST-1d-aaaaaa.md").write_text(ANALYSIS.format(td9="0" * 64), encoding="utf-8")
        (self.dir / "标的" / "TEST.md").write_text(SYMBOL_PAGE, encoding="utf-8")
        (self.dir / "标签.md").write_text(TAGS_PAGE, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_the_eth_filename_shape_fails(self):
        # "多周期" is not a timeframe and the id is missing -- the real case.
        (self.dir / "分析" / "2026-09-07-ETHUSDT-多周期.md").write_text(ANALYSIS.format(td9="0" * 64).replace("TEST", "ETHX"), encoding="utf-8")
        (self.dir / "标的" / "ETHX.md").write_text(SYMBOL_PAGE.replace("TEST", "ETHX").replace("2026-09-04-ETHX-1d-aaaaaa", "2026-09-07-ETHUSDT-多周期"), encoding="utf-8")
        self.assertTrue(any("unsortable" in p for p in check(self.dir)), check(self.dir))

    def test_an_analysis_without_a_hub_page_fails(self):
        # Leon's report: the ETH analysis landed and 标的/ gained nothing.
        (self.dir / "分析" / "2026-09-05-NEWX-1d-bbbbbb.md").write_text(ANALYSIS.format(td9="0" * 64).replace("TEST", "NEWX"), encoding="utf-8")
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
                        + "\n[查看](https://tradingsignal.pro/app?market=stock&symbol=TEST&timeframe=1d&tab=demark)\n", encoding="utf-8")
        self.assertTrue(any("not a tab the product has" in p for p in check(self.dir)))

    def test_a_complete_deep_link_passes(self):
        self.note()
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        note.write_text(note.read_text(encoding="utf-8")
                        + "\n[查看 TEST 的最新 TD9 分析](https://tradingsignal.pro/app?market=stock&symbol=TEST&timeframe=1d&tab=td9)\n", encoding="utf-8")
        self.assertEqual(check(self.dir), [])

    def link(self, url, label="查看"):
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        note.write_text(note.read_text(encoding="utf-8") + f"\n[{label}]({url})\n", encoding="utf-8")

    APP = "https://tradingsignal.pro/app?market=stock&symbol=TEST&timeframe=1d&tab=td9"

    def test_a_link_to_ANOTHER_symbol_fails(self):
        # The worst kind: complete parameters, wrong instrument. A shape
        # check passes it and the reader is shown a different chart.
        self.note()
        self.link(self.APP.replace("symbol=TEST", "symbol=AAPL"))
        self.assertTrue(any("opens AAPL" in p for p in check(self.dir)))

    def test_a_link_to_ANOTHER_timeframe_fails_unless_declared(self):
        self.note()
        self.link(self.APP.replace("timeframe=1d", "timeframe=4h"))
        self.assertTrue(any("opens 4h" in p for p in check(self.dir)))

    def test_a_declared_context_timeframe_is_allowed(self):
        # A multi-timeframe study may link its background timeframe -- but
        # only one it named in front matter.
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        self.note()
        note.write_text(note.read_text(encoding="utf-8").replace("timeframe: 1d", "timeframe: 1d\ncontext_timeframes: [4h]"), encoding="utf-8")
        self.link(self.APP.replace("timeframe=1d", "timeframe=4h"))
        self.assertEqual(check(self.dir), [])

    def test_a_missing_market_fails(self):
        self.note()
        self.link(self.APP.replace("market=stock&", ""))
        self.assertTrue(any("missing market" in p for p in check(self.dir)))

    def test_a_WRONG_market_fails(self):
        self.note()
        self.link(self.APP.replace("market=stock", "market=crypto"))
        self.assertTrue(any("market=crypto" in p for p in check(self.dir)))

    def test_link_text_promising_one_method_with_another_tab_fails(self):
        # The text is what the reader trusts; the tab is what opens.
        self.note()
        self.link(self.APP.replace("tab=td9", "tab=vcp"), label="查看 TEST 的最新 TD9 分析")
        found = check(self.dir)
        self.assertTrue(any("promises td9" in p for p in found), found)

    def test_a_method_tab_this_analysis_never_ran_fails(self):
        self.note()
        self.link(self.APP.replace("tab=td9", "tab=wyckoff"))
        self.assertTrue(any("not among this analysis's methods" in p for p in check(self.dir)))

    def test_a_correct_deep_link_passes(self):
        self.note()
        self.link(self.APP, label="查看 TEST 的最新 TD9 分析")
        self.assertEqual(check(self.dir), [])

    def test_an_unarchived_note_is_reported_as_an_incomplete_save(self):
        # Stating the gap makes the record honest; it does not make the
        # save complete. QA's rule after the Owner saw a note with no image.
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        note.write_text(ARCHIVED.format(main=self.hash, td9=self.hash)
                        .replace("image_archived: true", "image_archived: false") + "\n未归档。\n", encoding="utf-8")
        self.assertTrue(any("未完整保存" in p for p in check(self.dir)))

    def test_an_archived_image_that_is_never_embedded_fails(self):
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        self.note()
        note.write_text(note.read_text(encoding="utf-8").replace("![[附件/cccccc-td9.png]]", ""), encoding="utf-8")
        self.assertTrue(any("never embedded" in p for p in check(self.dir)))

    def test_an_embedded_image_without_a_link_beneath_it_fails(self):
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        self.note()
        text = note.read_text(encoding="utf-8")
        note.write_text(text.replace("[查看 TEST 的最新 TD9 分析](https://tradingsignal.pro/app?market=stock&symbol=TEST&timeframe=1d&tab=td9)", ""), encoding="utf-8")
        self.assertTrue(any("no method link directly beneath" in p for p in check(self.dir)))

    def test_the_link_under_an_image_must_open_that_image_method(self):
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        self.note()
        text = note.read_text(encoding="utf-8").replace("tab=td9)", "tab=vcp)").replace("最新 TD9 分析", "最新 VCP 分析")
        note.write_text(text.replace("methods: [td9]", "methods: [td9, vcp]"), encoding="utf-8")
        self.assertTrue(any("but the image draws td9" in p for p in check(self.dir)))

    def test_a_4h_caption_may_not_carry_a_1d_link(self):
        # QA: each chart link matches its OWN slot and caption.
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        self.note()
        text = note.read_text(encoding="utf-8").replace(
            "![[附件/cccccc-td9.png]]", "![[附件/cccccc-td9.png|TEST 4h TD9]]")
        note.write_text(text.replace("timeframe: 1d", "timeframe: 1d\ncontext_timeframes: [4h]"), encoding="utf-8")
        self.assertTrue(any("caption says 4h" in p for p in check(self.dir)))

    def slot(self, slot_name, tab, methods="td9"):
        """One archived image under `slot_name`, linked to `tab`."""
        png = b"another png"
        (self.dir / "附件" / f"cccccc-{slot_name}.png").write_bytes(png)
        import hashlib as _h
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        base = (ARCHIVED.format(main=_h.sha256(png).hexdigest(), td9=_h.sha256(png).hexdigest())
                .replace("  td9: ", f"  {slot_name}: ")
                .replace("methods: [td9]", f"methods: [{methods}]"))
        # Drop the base fixture's own image and link: this note has ONE
        # image, the slot under test, or the leftover td9 link fails a rule
        # that has nothing to do with what is being tested.
        base = base.split("body")[0] + "body\n"
        note.write_text(
            base + f"\n![[附件/cccccc-{slot_name}.png]]\n\n[查看](https://tradingsignal.pro/app?market=stock&symbol=TEST&timeframe=1d&tab={tab})\n",
            encoding="utf-8")
        (self.dir / "附件" / "cccccc-td9.png").unlink(missing_ok=True)

    def test_a_trend_image_linked_to_another_tab_fails(self):
        # `trend` is a real product tab; the first slot map left it unguarded.
        self.slot("trend", "vcp", methods="trend, vcp")
        self.assertTrue(any("the image draws trend" in p for p in check(self.dir)))

    def test_an_indicators_image_linked_to_another_tab_fails(self):
        self.slot("indicators", "levels", methods="indicators, levels")
        self.assertTrue(any("the image draws indicators" in p for p in check(self.dir)))

    def test_an_unknown_slot_without_a_binding_fails_closed(self):
        # `main` names no method, so it may not pass on any tab at all.
        self.slot("main", "vcp", methods="vcp")
        self.assertTrue(any("names no method" in p for p in check(self.dir)))

    def test_an_unknown_slot_WITH_a_binding_is_checked_against_it(self):
        self.slot("main", "vcp", methods="vcp, indicators")
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        text = note.read_text(encoding="utf-8").replace("image_archived: true", "image_archived: true\nprimary_method: indicators")
        note.write_text(text, encoding="utf-8")
        # Bound to indicators, linked to vcp -> caught.
        self.assertTrue(any("the image draws indicators" in p for p in check(self.dir)))
        note.write_text(text.replace("tab=vcp", "tab=indicators"), encoding="utf-8")
        self.assertEqual(check(self.dir), [])

    def test_an_image_pooled_under_the_links_section_fails(self):
        # The Owner's point: one analysis may hold several charts, each
        # sitting with the method it belongs to -- not collected at the end.
        self.note()
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        text = note.read_text(encoding="utf-8").replace("![[附件/cccccc-td9.png]]", "")
        note.write_text(text + "\n## 链接\n\n![[附件/cccccc-td9.png]]\n\n[查看](https://tradingsignal.pro/app?market=stock&symbol=TEST&timeframe=1d&tab=td9)\n", encoding="utf-8")
        self.assertTrue(any("pooled with the links" in p for p in check(self.dir)))

    def test_a_td9_image_under_a_VCP_section_fails(self):
        # QA's counterexample: correct slot, correct link, wrong section --
        # the previous rule only forbade the 链接 section, so this passed.
        self.note()
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        text = note.read_text(encoding="utf-8").replace(
            "![[附件/cccccc-td9.png]]", "## VCP 形态\n\n![[附件/cccccc-td9.png]]")
        note.write_text(text.replace("methods: [td9]", "methods: [td9, vcp]"), encoding="utf-8")
        found = check(self.dir)
        self.assertTrue(any("sits under" in p for p in found), found)

    def test_a_td9_image_under_a_TD9_section_passes(self):
        self.note()
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        note.write_text(note.read_text(encoding="utf-8").replace(
            "![[附件/cccccc-td9.png]]", "## TD9 序列\n\n![[附件/cccccc-td9.png]]"), encoding="utf-8")
        self.assertEqual(check(self.dir), [])

    def test_an_image_under_a_section_naming_no_method_is_allowed(self):
        # `## 结论` reasons about the whole analysis; a chart there is fine.
        self.note()
        note = self.dir / "分析" / "2026-09-04-TEST-1d-cccccc.md"
        note.write_text(note.read_text(encoding="utf-8").replace(
            "![[附件/cccccc-td9.png]]", "## 结论\n\n![[附件/cccccc-td9.png]]"), encoding="utf-8")
        self.assertEqual(check(self.dir), [])

    def test_a_version_with_no_index_entry_is_reported_as_unresolvable(self):
        # Present but meaningless: the note names a release the methodology
        # index has never seen, so no definition can be selected for it.
        self.note()
        (self.dir / "方法").mkdir(exist_ok=True)
        (self.dir / "方法" / "版本索引.json").write_text(
            '{"td9": {"0.1.29": "TD9.md"}}', encoding="utf-8")
        found = check(self.dir)
        self.assertTrue(any("has no entry for" in p for p in found), found)

    def test_a_version_the_index_knows_resolves_cleanly(self):
        self.note()
        (self.dir / "方法").mkdir(exist_ok=True)
        (self.dir / "方法" / "版本索引.json").write_text(
            '{"td9": {"0.1.30": "TD9.md"}}', encoding="utf-8")
        self.assertEqual(check(self.dir), [])

    def test_a_missing_vocabulary_fails_closed(self):
        self.note()
        (self.dir / "标签.md").unlink()
        self.assertTrue(any("no 标签.md" in p for p in check(self.dir)))



class VaultCheckMethodology(unittest.TestCase):
    """`方法/` is a synced copy, so it must say which release wrote it."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        for d in ("分析", "标的", "附件", "_模板", "方法"):
            (self.dir / d).mkdir()
        (self.dir / "_模板" / "分析.md").write_text(TEMPLATE, encoding="utf-8")
        (self.dir / "标签.md").write_text(TAGS_PAGE, encoding="utf-8")
        from vault_check import packaged_skill_version
        self.version = packaged_skill_version()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def note(self, name, topic, version):
        (self.dir / "方法" / name).write_text(
            f"---\ntopic: {topic}\nskill_version: {version}\n---\n\nverbatim methodology text\n", encoding="utf-8")

    def test_a_current_methodology_note_passes(self):
        self.note("VCP.md", "vcp", self.version)
        self.assertEqual(check_methods(self.dir), [])

    def test_a_note_from_an_older_release_is_reported_as_stale(self):
        # The Owner's ask: check the version every time, update when newer.
        self.note("VCP.md", "vcp", "0.0.1")
        self.assertTrue(any("re-download this topic" in p for p in check_methods(self.dir)))

    def test_a_note_that_cannot_say_its_version_fails(self):
        (self.dir / "方法" / "VCP.md").write_text("---\ntopic: vcp\n---\n\ntext\n", encoding="utf-8")
        self.assertTrue(any("no `skill_version`" in p for p in check_methods(self.dir)))

    def test_a_topic_the_skill_does_not_serve_fails(self):
        self.note("Astrology.md", "astrology", self.version)
        self.assertTrue(any("is not one the skill serves" in p for p in check_methods(self.dir)))

    def test_a_directory_README_is_not_a_topic_note(self):
        (self.dir / "方法" / "README.md").write_text("# 方法\n\nthis layer is synced\n", encoding="utf-8")
        self.assertEqual(check_methods(self.dir), [])

    def test_a_vault_with_no_methods_directory_is_not_an_error(self):
        shutil.rmtree(self.dir / "方法")
        self.assertEqual(check_methods(self.dir), [])


if __name__ == "__main__":
    unittest.main()
