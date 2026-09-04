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


if __name__ == "__main__":
    unittest.main()
