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
        for name, needle in (("SKILL.md", "no backtest"), ("SKILL.zh-CN.md", "没有做过回测")):
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
        for name, needles in (
            ("SKILL.md", ("levels chart from `get_levels`", "no matching chart")),
            ("SKILL.zh-CN.md", ("支撑阻力图", "没有对应的图")),
        ):
            text = (SKILL / name).read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, f"{name} no longer binds the risk chart: {needle}")


    def test_prices_must_come_from_the_drawn_set(self):
        """A report cited 80,407 while its chart drew six other prices.

        The MCP now guarantees riskReward's bounds appear in `drawnLevels`, so
        the skill can be told to cite only from there instead of computing its
        own "nearest" level off a list the picture does not match.
        """
        for name, needles in (
            ("SKILL.md", ("drawnLevels", "never compute your own")),
            ("SKILL.zh-CN.md", ("drawnLevels", "不要自己算")),
        ):
            text = (SKILL / name).read_text(encoding="utf-8")
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
            ("SKILL.md", ("observation, never a verdict", "not automatically an opportunity")),
            ("SKILL.zh-CN.md", ("是一个观察，不是结论", "也不自动等于机会")),
        ):
            text = (SKILL / name).read_text(encoding="utf-8")
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
            ("SKILL.md", "including the nearest support itself"),
            ("SKILL.zh-CN.md", "含最近这条本身"),
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
            ("SKILL.md", "whose TEXT names the chart"),
            ("SKILL.zh-CN.md", "链接文字写明内容"),
        ):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)

    def test_naked_signed_urls_are_forbidden_in_both_languages(self):
        for name, needle in (
            ("SKILL.md", "never a naked signed URL"),
            ("SKILL.zh-CN.md", "不裸露签名长串"),
        ):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)

    def test_chart_and_method_page_urls_are_distinguished(self):
        for name, needles in (
            ("SKILL.md", ("chart URL", "method-page URL", "do not guess its parameters")),
            ("SKILL.zh-CN.md", ("图表 URL", "方法页 URL", "不要猜参数")),
        ):
            text = (SKILL / name).read_text(encoding="utf-8")
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
        for name, needle in (("SKILL.md", "never an inline image embed"), ("SKILL.zh-CN.md", "不用行内图片嵌入")):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)

    def test_the_vault_surface_REQUIRES_embeds(self):
        for name, needles in (
            ("references/obsidian-vault.md", ("Two surfaces, opposite rules", "EMBEDDED in the body", "Archiving is REQUIRED", "DEGRADED record")),
            ("references/obsidian-vault.zh-CN.md", ("两个界面，规则相反", "嵌在正文里", "归档是必须项", "降级记录")),
        ):
            text = (SKILL / name).read_text(encoding="utf-8")
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

    def test_the_in_session_menu_path_is_forbidden_unless_seen(self):
        for name, needle in (
            ("SKILL.md", "unless you have SEEN that server listed"),
            ("SKILL.zh-CN.md", "除非你在**本次会话里真的看到**"),
        ):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)

    def test_it_says_where_the_command_is_typed(self):
        for name, needle in (("SKILL.md", "in the terminal"), ("SKILL.zh-CN.md", "在终端里输入")):
            self.assertIn(needle, (SKILL / name).read_text(encoding="utf-8"), name)


if __name__ == "__main__":
    unittest.main()
