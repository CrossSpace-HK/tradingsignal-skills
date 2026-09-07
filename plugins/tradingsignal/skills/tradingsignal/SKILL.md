---
name: tradingsignal
description: Use TradingSignal MCP for market screening, multi-timeframe opportunity discovery, single-symbol technical research, support/resistance analysis, and conditional trade planning across crypto, FX, commodities, and supported futures. Use when the user wants TradingSignal to find, validate, compare, or plan technical setups; not for macro news research, order execution, or position sizing without an explicit risk budget.
metadata:
  version: "0.1.14"
---

[English](SKILL.md) | [中文](SKILL.zh-CN.md)

# TradingSignal

Route the user's request to the narrowest TradingSignal workflow, load only the references that workflow needs, and lead with the decision.

## Choose the workflow

- Cross-market leaders or fresh strength: read the shared [market-screening playbook](references/opportunity-scan.md), then [cross-market leaders](references/cross-market-leaders.md).
- A higher-timeframe trend with a lower-timeframe pullback and restart: read the shared [market-screening playbook](references/opportunity-scan.md), then [pullback restart](references/pullback-restart.md).
- Reversal candidates or exhaustion: read the shared [market-screening playbook](references/opportunity-scan.md), then [reversal validation](references/reversal-validation.md).
- Deep research on one named symbol, one timeframe, or one technical method: read [single-symbol analysis](references/symbol-analysis.md).
- Entry zone, trigger, invalidation, targets, risk/reward, or a complete conditional plan: read [conditional trade plan](references/trade-plan.md). For a market-wide request, first use the relevant screening workflow.
- A risk-first review, conflicting evidence, or a request to state when nothing qualifies: read the shared [market-screening playbook](references/opportunity-scan.md), then [no-valid-opportunity review](references/no-trade-review.md).
- Saving an analysis for later review, or reviewing past analyses, in the user's own Obsidian vault: read [recording to Obsidian](references/obsidian-vault.md). It is opt-in and writes nothing without a vault path the user gave.
- If the request mixes these jobs, apply them in order: screen, analyze the shortlist with granular modules, then build plans only for candidates that survive validation.

Do not load every reference for a narrow request.

## Skill release check

Treat the frontmatter `metadata.version` as the installed Skill release. The repository release script keeps it synchronized with the Codex plugin manifest.

- The required `describe_capabilities` call may include `skillRelease.version`. Do not make an extra tool call only to check for updates.
- Compare valid semantic versions. Mention an update once, after the market answer, only when `skillRelease.version` is strictly newer than `metadata.version`.
- Only after that comparison is positive, call `get_methodology` with `topic: "skill-update"`. Give its update command for the active client; if the client is unknown, label both client commands instead of guessing.
- Say nothing about updates when the versions match, the published version is older, or either field is absent or invalid. An update check must never block the requested analysis.

## Shared rules

- Use `describe_capabilities` before assuming market, symbol, timeframe, freshness, or cohort coverage.
- Use the narrowest granular MCP tool that answers the question. Treat `analyze_symbol` as an optional quick overview, not the default research path or independent confirmation.
- Preserve `notApplicable` and “not computable” as distinct from neutral and from “no signal.”
- Higher timeframes set the backdrop; lower timeframes refine entries. Do not average away a deliberate `1d trend -> 4h pullback -> 1h restart` structure.
- Never compare relative-strength percentiles from different market cohorts as absolute cross-market scores.
- Never substitute a spot series for a futures ticker or silently splice data providers.
- FX has no consolidated volume. Do not support an FX action with volume-derived claims unless the response supplies a valid, labelled proxy.
- Fibonacci auto-detection is exploratory. Do not use it in screening weights, strong-confluence claims, or trading actions unless separately calibrated out of sample against nearby-anchor and ordinary support/resistance controls.
- Do not return an entry action without a concrete invalidation level. Do not invent position sizing without the user's portfolio size and risk budget.
- If data are stale, evidence conflicts materially, or a required chart is missing, downgrade to `WATCH` or `AVOID` and say why.

## Evidence contract

For every decision-relevant reason, return the claim, backing, why it matters, timeframe, module, evidence fields, analysis timestamp, and the matching module chart URL. Put the chart URL immediately after its reason.

Use the chart returned by `get_method_analysis` when available. Otherwise call `get_chart` with the same symbol and timeframe and the matching preset: `price`, `chan`, `td9`, `wyckoff`, or `vcp`. Say when a chart is contextual rather than a direct overlay of the numerical evidence.

Keep the answer conclusion-first. State explicitly when no setup qualifies; never manufacture actions to fill a list.

## Report shape

Lead with the conclusion: one sentence saying what to do, or that there is nothing to do. Then bullets, at most two sentences each, with the matching chart immediately after the bullet it supports:

1. **Entry** — the price or the condition that would trigger one.
2. **Exit** — the target, and the invalidation that ends the idea.
3. **Where it is** — which VCP stage, where in the Chan structure, or which independent methods agree.
4. **Risk** — the room above and below, taken from `riskReward` in `get_levels` and from nothing else.

Read `riskReward` as a whole, not as a single number. Report the distance both ways in percent AND in price, then weigh the support: `strength` is how much confluence formed it, and `levelsWithin` is how many levels hold up that area **including the nearest support itself** -- 1 means a lone line, 3 means it sits on a shelf. Do not describe it as levels *below* the support; that reads one too many. A thick shelf is worth more than one lone line at the same price.

**A large ratio usually means price is sitting on support, not that the trade is generous.** When `atLevel` is true, report that price is resting on the level instead of quoting the ratio as if it were an edge.

`atLevel` is an observation, never a verdict. It says price is near a level and nothing more. A small downside is therefore not automatically a defect -- but it is not automatically an opportunity either, because price sitting on a weak level that is about to give way looks identical in this field. Before calling it an entry, require: the level below is strong (`strength`) and not thin (`levelsWithin`), there is room above worth taking, some evidence price is actually holding rather than still falling, and a stated invalidation for when it breaks. Absent those, report the position and stop there.

Two rules on the risk bullet specifically, because real answers have broken both:

- **Never state an account percentage, a position size, or a risk budget** — not "risk 0.5–1% per trade", not any figure of that kind — unless the user has given their portfolio size and their own risk budget in this conversation. Those numbers are a common convention, not something we computed, and printing one turns a measurement into unauthorised advice.
- **The chart under this bullet must be the levels chart from `get_levels`.** If it is unavailable, say there is no matching chart. Never substitute a TD9, Chan or VCP image to satisfy the one-chart-per-bullet habit: a picture that does not show what the sentence claims is worse than no picture.
- **Only cite prices listed in `drawnLevels`.** That field names exactly what the attached chart contains. A price that is not in it cannot be checked against the picture, so do not present one as an entry, target, invalidation or bound -- and never compute your own "nearest" level: `riskReward` already reports the nearest on each side, and its bounds are guaranteed to be in `drawnLevels`.

That second rule applies to every bullet. Attach the chart that shows the thing being claimed; when there is none, say so rather than reaching for another module's image.

Write it so a reader understands it on first pass. Be precise, not ornamental, and avoid jargon labels such as `regime`, `trigger` or `payoff`.

**Never state a win rate, a confidence interval, or any probability of success.** These engines are rule-based and there is no backtest behind them, so such a number would be invented. `riskReward` measures distance to real levels and is not a probability: a ratio of 2 means twice the room, never a 2-in-3 chance. When `riskReward` returns null bounds, say the levels are too close to measure against rather than filling in a figure.
