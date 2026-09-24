"""One output contract, defined once.

QA-CEA's finding: SKILL.md said four bullets while references/trade-plan.md
still demanded a JSON schema. Faced with two contracts the model followed
neither and produced a third format -- a table by timeframe. A keyword check
("does the text mention entry?") passes in exactly that situation, which is
why these assert the SHAPE OF THE CONTRACT rather than its vocabulary.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "tradingsignal"
REFS = SKILL / "references"


def flat(name):
    """A carrier file's text with every run of whitespace made one space.

    Progressive disclosure moved many rules into wrapped reference prose, so a
    phrase can straddle a line break; the rule is the words, not the wrap.
    """
    return re.sub(r"\s+", " ", (SKILL / name).read_text(encoding="utf-8"))

# A reference may describe WHAT to look for. It may not define its own answer
# format, because SKILL.md already does and the model cannot obey both.
COMPETING = [
    (re.compile(r"^```json", re.M), "declares a JSON response schema"),
    (re.compile(r"ENTER_ON_PULLBACK"), "declares its own action enum"),
]


class ReportShape(unittest.TestCase):
    def test_skill_defines_the_shape_once(self):
        for name in ("SKILL.md", "SKILL.zh-CN.md"):
            text = (SKILL / name).read_text(encoding="utf-8")
            self.assertRegex(text, r"(Report shape|报告结构)", name)

    def test_no_reference_defines_a_competing_format(self):
        for path in sorted(REFS.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for pattern, why in COMPETING:
                self.assertIsNone(
                    pattern.search(text),
                    f"{path.name} {why}; SKILL.md already defines the shape and "
                    f"two contracts make the model invent a third",
                )

    def test_shape_carries_all_four_bullets(self):
        # Named in both languages, so a translation cannot quietly drop one.
        for name, needles in (
            ("SKILL.md", ("Entry", "Exit", "Where it is", "Risk")),
            ("SKILL.zh-CN.md", ("入场点", "计划出场", "它现在在哪", "风险")),
        ):
            text = (SKILL / name).read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, f"{name} is missing '{needle}'")

    def test_forbids_invented_probabilities(self):
        # The one instruction a model drops when it wants to sound useful.
        for name, needle in (("SKILL.md", "no backtest"), ("SKILL.zh-CN.md", "背后没有回测")):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)

    def test_rejected_jargon_survives_only_as_a_prohibition(self):
        for path in list(REFS.glob("*.md")) + [SKILL / "SKILL.md", SKILL / "SKILL.zh-CN.md"]:
            for line in path.read_text(encoding="utf-8").splitlines():
                if "regime" in line or "payoff" in line:
                    low = line.lower()
                    self.assertTrue(
                        any(k in low for k in ("不要用", "do not label", "avoid jargon")),
                        f"{path.name}: still uses the rejected vocabulary: {line.strip()[:80]}",
                    )


    def test_risk_bullet_forbids_invented_position_sizing(self):
        """A real answer printed "risk 0.5-1% per trade" with no risk budget given.

        That is a convention, not something we computed, and printing it turns a
        measurement into unauthorised advice. Asserted as the PRESENCE of the
        prohibition -- asserting the absence of "0.5%" would fail on the very
        sentence that bans it.
        """
        for name, needles in (
            ("SKILL.md", ("account percentage", "position size", "portfolio size")),
            ("SKILL.zh-CN.md", ("账户百分比", "仓位大小", "风险预算")),
        ):
            text = (SKILL / name).read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, f"{name} no longer forbids '{needle}'")

    def test_risk_bullet_is_bound_to_the_levels_chart(self):
        """The same answer attached a 1h TD9 chart to a support/resistance claim.

        Padding "one chart per bullet" with whatever image is to hand makes the
        picture contradict the sentence, which is worse than no picture.
        """
        # The rule lives in the chart reference; SKILL.md's risk bullet must
        # still send the reader there, or the rule is never loaded.
        for name, needles in (
            ("references/chart-links.md", (
                "The risk bullet's chart must be the `get_levels` chart specifically",
                "Where there is none, say so rather than reaching for another module's image")),
            ("references/chart-links.zh-CN.md", (
                "风险那一条的图必须是 `get_levels` 的图",
                "没有就说没有，绝不拿别的模块的图来凑")),
            ("SKILL.md", ("The chart under this bullet, and only prices from `drawnLevels`: see [chart links](references/chart-links.md)",)),
            ("SKILL.zh-CN.md", ("这一条下面的图，以及只能引用 `drawnLevels` 里的价格：见[附图的规矩](references/chart-links.zh-CN.md)",)),
        ):
            text = flat(name)
            for needle in needles:
                self.assertIn(needle, text, f"{name} no longer binds the risk chart: {needle}")


    def test_prices_must_come_from_the_drawn_set(self):
        """A report cited 80,407 while its chart drew six other prices.

        The MCP now guarantees riskReward's bounds appear in `drawnLevels`, so
        the skill can be told to cite only from there instead of computing its
        own "nearest" level off a list the picture does not match.
        """
        for name, needles in (
            ("references/chart-links.md", ("only prices listed in `drawnLevels` may be cited",)),
            ("references/chart-links.zh-CN.md", ("只能引用 `drawnLevels` 里的价格",)),
            ("SKILL.md", ("only prices from `drawnLevels`",)),
            ("SKILL.zh-CN.md", ("只能引用 `drawnLevels` 里的价格",)),
        ):
            text = flat(name)
            for needle in needles:
                self.assertIn(needle, text, f"{name} no longer binds prices to the drawn set: {needle}")


    def test_at_level_is_not_treated_as_a_buy_signal(self):
        """`atLevel` says price is NEAR a level. It does not say the level holds.

        @QA-CEA: price sitting on a weak support about to break looks identical
        in this field, so wording it as "often a good entry" reads a failing
        setup as a positive one. Leon's point stands -- a small downside is not
        automatically a defect -- but it is not automatically an opportunity.
        """
        for name, needles in (
            ("SKILL.md", ("`atLevel` is an observation, never a verdict", "Before calling it an entry, require all of")),
            ("SKILL.zh-CN.md", ("`atLevel` 只是观察，不是结论", "要叫它入场，必须同时满足")),
        ):
            text = flat(name)
            for needle in needles:
                self.assertIn(needle, text, f"{name} treats atLevel as sufficient: {needle}")
        # And the earlier over-claim must not come back.
        self.assertNotIn(
            "往往是好的入场位置",
            (SKILL / "SKILL.zh-CN.md").read_text(encoding="utf-8"),
        )


    def test_levels_within_is_described_as_inclusive(self):
        """A real report said "4 more levels below" when there were 3.

        `levelsWithin` counts the nearest support itself. Describing it as
        levels BENEATH that support reads one too many, and this number is the
        density signal -- the difference between a shelf and a single line.
        """
        for name, needle in (
            ("SKILL.md", "including the nearest one itself"),
            ("SKILL.zh-CN.md", "含最近那一条本身"),
        ):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)
        # The wording that caused it must not return -- checked line by line,
        # because the file now contains that phrase inside the instruction NOT
        # to use it. A flat assertNotIn fails on the prohibition itself, which
        # is a mistake I have now made three times in one session.
        for line in (SKILL / "SKILL.zh-CN.md").read_text(encoding="utf-8").splitlines():
            if "下方另有" in line:
                self.assertIn("不要", line, f"reintroduces the miscount: {line.strip()[:70]}")


class ChartLinksAreReadable(unittest.TestCase):
    """The Owner's contract: a chart travels as a NAMED link, and the chart
    URL is never conflated with the method-page URL."""

    def test_the_named_link_form_is_mandated_in_both_languages(self):
        for name, needle in (
            ("references/chart-links.md", "Charts are markdown links whose TEXT names symbol, timeframe and method"),
            ("references/chart-links.zh-CN.md", "链接文字要写明标的、周期、方法"),
            # ...and every session that attaches a chart is sent there first.
            ("SKILL.md", "Read [chart links](references/chart-links.md) first"),
            ("SKILL.zh-CN.md", "先读[附图的规矩](references/chart-links.zh-CN.md)"),
        ):
            self.assertIn(needle, flat(name), name)

    def test_naked_signed_urls_are_forbidden_in_both_languages(self):
        for name, needle in (
            ("references/chart-links.md", "Never a naked URL"),
            ("references/chart-links.zh-CN.md", "不许裸 URL"),
        ):
            self.assertIn(needle, flat(name), name)

    def test_chart_and_method_page_urls_are_distinguished(self):
        for name, needles in (
            ("references/chart-links.md", ("Chart URL ≠ method-page URL", "Never build the method-page link yourself")),
            ("references/chart-links.zh-CN.md", ("图链接 ≠ 方法页链接", "方法页链接绝不能自己拼")),
        ):
            text = flat(name)
            for needle in needles:
                self.assertIn(needle, text, f"{name} is missing '{needle}'")

    def test_the_vault_reference_links_frozen_record_to_living_view(self):
        for name, needle in (
            ("references/obsidian-vault.md", "LATEST analysis for the same symbol, timeframe and method"),
            ("references/obsidian-vault.zh-CN.md", "同标的/同周期/同方法的最新分析"),
        ):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)


class TwoSurfacesForCharts(unittest.TestCase):
    """The Owner drew the line himself: links in chat, embedded images in
    Obsidian. Stating one rule without the other is how the last version
    produced a note with no pictures in it."""

    def test_the_chat_surface_forbids_embeds(self):
        for name, needle in (
            ("references/chart-links.md", "never an image embed"),
            ("references/chart-links.zh-CN.md", "不许内嵌图片"),
        ):
            self.assertIn(needle, flat(name), name)

    def test_the_vault_surface_REQUIRES_embeds(self):
        for name, needles in (
            ("references/obsidian-vault.md", ("This surface is the opposite of a chat reply", "decided by surface and not by habit", "EMBEDDED in the body", "Archiving is REQUIRED", "DEGRADED record")),
            ("references/obsidian-vault.zh-CN.md", ("这个界面和聊天回复恰好相反", "按界面判断，不按习惯判断", "嵌在正文里", "归档是必须项", "降级记录")),
        ):
            text = flat(name)
            for needle in needles:
                self.assertIn(needle, text, f"{name} is missing '{needle}'")


class ExpiredSessionGuidance(unittest.TestCase):
    """The Owner's screenshot: inside Codex, the model told him to open
    `/mcp` and pick tradingsignal. Codex's list does not contain it -- that
    is Claude Code's idiom, emitted for the wrong client."""

    def test_the_terminal_command_is_given_per_client(self):
        for name, needles in (
            ("SKILL.md", ("codex mcp login tradingsignal", "claude mcp login tradingsignal")),
            ("SKILL.zh-CN.md", ("codex mcp login tradingsignal", "claude mcp login tradingsignal")),
        ):
            text = (SKILL / name).read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, f"{name} is missing '{needle}'")

    def test_mcp_is_described_as_a_viewer_not_an_authorise_button(self):
        for name, needle in (
            ("SKILL.md", "`/mcp` is a VIEWER, not the authorise button"),
            ("SKILL.zh-CN.md", "**`/mcp` 是查看器，不是授权按钮**"),
        ):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)

    def test_the_desktop_path_is_the_verified_one(self):
        # Settings -> MCP servers -> Authenticate, confirmed against the CLI
        # and OpenAI's own documentation. Not /mcp.
        for name, needle in (
            ("SKILL.md", "Settings → MCP servers → tradingsignal → Authenticate"),
            ("SKILL.zh-CN.md", "Settings → MCP servers → tradingsignal → Authenticate"),
        ):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)

    def test_it_says_where_the_command_is_typed(self):
        for name, needle in (("SKILL.md", "in the terminal"), ("SKILL.zh-CN.md", "在终端里输入")):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)


class ShippedToolContract(unittest.TestCase):
    """0.1.51: what production (TradingSignal b6be4092) already returns.

    @QA-CEA: `get_td9_read` reads a DIFFERENT set of timeframes for a
    daily-only name (`pulseTimeframes(timeframesForSymbol(...))`), so a skill
    that promises 5m-1d everywhere teaches the model to expect rows that do
    not exist. Both branches are pinned, in both languages.
    """

    CARRIERS = (
        ("SKILL.md", "references/symbol-analysis.md"),
        ("SKILL.zh-CN.md", "references/symbol-analysis.zh-CN.md"),
    )

    def test_td9_read_names_both_timeframe_sets(self):
        for pair in self.CARRIERS:
            for name in pair:
                text = flat(name)
                self.assertIn("`get_td9_read`", text, name)
                self.assertIn("5m/15m/1h/4h/1d", text, f"{name}: intraday set")
                self.assertIn("1d/1w/1mo", text, f"{name}: daily-only set")

    def test_td9_read_is_answered_from_structured_and_dated_by_freshness(self):
        for name, needles in (
            ("SKILL.md", ("Answer from `structured`", "date the paragraph only", "`freshness[timeframe]`",
                          "name a stale timeframe", "`get_method_analysis(engine=\"td9\")`")),
            ("SKILL.zh-CN.md", ("依据 `structured` 作答", "只说明这段文字的时间", "`freshness[周期]`",
                                "过期的周期要点名", "`get_method_analysis(engine=\"td9\")`")),
        ):
            text = flat(name)
            for needle in needles:
                self.assertIn(needle, text, f"{name} is missing '{needle}'")

    def test_trend_strength_fields_match_production(self):
        # Field names are production's (lib/trendStrengthOverlay.ts); the five
        # section ids are TREND_CATEGORY_ORDER, in that order.
        for name in ("SKILL.md", "references/symbol-analysis.md"):
            text = flat(name)
            for needle in ("`trendStrength`", "`sections`", "`series`", "`seriesBars`", "`indicators`",
                           "120 closed bars", "oldest first"):
                self.assertIn(needle, text, f"{name} is missing '{needle}'")
        self.assertIn("(trend, momentum, volume, volatility, pattern — ", flat("SKILL.md"))
        self.assertIn("`trend`, `momentum`, `volume`, `volatility`, `pattern`",
                      flat("references/symbol-analysis.md"))
        for name in ("SKILL.zh-CN.md", "references/symbol-analysis.zh-CN.md"):
            text = flat(name)
            for needle in ("`trendStrength`", "`sections`", "`series`", "`seriesBars`", "120 根已收盘"):
                self.assertIn(needle, text, f"{name} is missing '{needle}'")

    def test_no_unshipped_live_settled_fields(self):
        # The live/settled schema is a contract under review, not a release.
        # Describing it before it ships teaches the model fields that 404.
        for path in [SKILL / "SKILL.md", SKILL / "SKILL.zh-CN.md"] + sorted(REFS.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for word in ("settled", "observedAt", "servedAt", "live.", "provisional"):
                self.assertNotIn(word, text, f"{path.name} describes unshipped field '{word}'")

    def test_vault_doc_agrees_with_the_checker_on_market(self):
        # vault_check.py (3de7b65) lets `market` be absent and rejects a wrong
        # one; the reference used to say a missing market was "a guess". The
        # doc, the checker and its tests must say the same thing.
        for name, needles, stale in (
            ("references/obsidian-vault.md",
             ("A link missing any of symbol, timeframe or tab is not a deep link", "`market` may be left out",
              "must carry the right one"),
             "missing any of market"),
            ("references/obsidian-vault.zh-CN.md",
             ("缺 symbol、timeframe、tab 任何一项的链接不是深链", "`market` 可以省略", "就必须写对"),
             "缺 market"),
        ):
            text = flat(name)
            for needle in needles:
                self.assertIn(needle, text, f"{name} is missing '{needle}'")
            self.assertNotIn(stale, text, f"{name} still calls a market-less link a guess")



class ChartSurfacesAgreeAcrossFiles(unittest.TestCase):
    """@QA-CEA: chart-links said chat never embeds while obsidian-vault said a
    chat box that renders remote images should embed. Each file was pinned
    green on its own, which proved nothing about the two loaded together.
    One contract: chat -> named links only; vault -> local archived file only."""

    VAULT = ("references/obsidian-vault.md", "references/obsidian-vault.zh-CN.md")

    def test_chat_never_embeds(self):
        for name, needle in (("references/chart-links.md", "never an image embed"),
                             ("references/chart-links.zh-CN.md", "不许内嵌图片")):
            self.assertIn(needle, flat(name), name)

    def test_vault_embeds_only_the_local_archive(self):
        for name, needles in (
            ("references/obsidian-vault.md", ("embeds only the LOCAL archived file", "`![[附件/<analysis_id>-<slot>.png]]`",
                                              "Never embed a remote URL in a note")),
            ("references/obsidian-vault.zh-CN.md", ("只嵌本地已归档的文件", "`![[附件/<analysis_id>-<slot>.png]]`",
                                                    "笔记里绝不嵌远程 URL")),
        ):
            text = flat(name)
            for needle in needles:
                self.assertIn(needle, text, f"{name} is missing '{needle}'")

    def test_vault_doc_restates_rather_than_overrides_the_chat_rule(self):
        for name, needle in (("references/obsidian-vault.md", "A chat reply never embeds a chart"),
                             ("references/obsidian-vault.zh-CN.md", "聊天回复一律不嵌图")):
            self.assertIn(needle, flat(name), name)
        # The instruction that contradicted chart-links must not come back.
        for name in self.VAULT:
            text = flat(name)
            for stale in ("chat box that displays remote", "能显示远程图片的对话框",
                          "The snapshot URL already IS a PNG", "快照链接本身就是一张"):
                self.assertNotIn(stale, text, f"{name} tells chat to embed again: {stale}")



class NoRawBarTool(unittest.TestCase):
    """Leon (msg b7cb9302): agents read computed numbers, never raw bars.
    get_candles was removed from the MCP (TradingSignal task #177); a skill
    that still routes to it teaches the model to call a tool that is gone."""

    def test_no_skill_file_names_get_candles(self):
        root = ROOT / "skills"
        for path in sorted(root.rglob("*.md")):
            self.assertNotIn("get_candles", path.read_text(encoding="utf-8"), str(path.relative_to(ROOT)))

    def test_the_rule_is_stated_where_the_escape_hatch_is(self):
        for name, needle in (
            ("references/symbol-analysis.md", "There is no raw-bar tool"),
            ("references/symbol-analysis.zh-CN.md", "没有给 Agent 读原始 K 线的工具"),
            ("references/opportunity-scan.md", "There is no raw-bar tool"),
            ("references/opportunity-scan.zh-CN.md", "没有给 Agent 读原始 K 线的工具"),
        ):
            self.assertIn(needle, flat(name), name)


if __name__ == "__main__":
    unittest.main()
