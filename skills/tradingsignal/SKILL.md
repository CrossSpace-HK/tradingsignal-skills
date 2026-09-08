---
name: tradingsignal
description: Use TradingSignal MCP for market screening, multi-timeframe opportunity discovery, single-symbol technical research, support/resistance analysis, and conditional trade planning across crypto, FX, commodities, and supported futures. Use when the user wants TradingSignal to find, validate, compare, or plan technical setups; not for macro news research, order execution, or position sizing without an explicit risk budget.
metadata:
  version: "0.1.50"
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

## When the MCP session has expired

An OAuth session lapses, and every tool call then fails. Say so plainly and
give the ONE command that fixes it for the client actually in use:

- **Codex** — in the terminal: `codex mcp login tradingsignal`; or in the
  desktop app, Settings → MCP servers → tradingsignal → Authenticate, then
  restart or open a new session.
- **Claude Code** — in the terminal: `claude mcp login tradingsignal`

`/mcp` is a VIEWER, not the authorise button: in Codex it lists the active
servers and nothing more, so "open `/mcp` → tradingsignal → Authenticate" is
a Claude Code idiom that sends a Codex user to a control their client does
not offer. Use it only to check whether the server appears at all. Say where
the command is typed -- the terminal, not the chat box -- and if the client
is unknown, give both labelled rather than guessing. From the user's side a
wrong instruction and a broken install look identical, so being wrong here
costs them the whole install.

Then stop and wait. Do not continue an analysis on data you could not fetch,
and do not fill the gap from memory.

## Shared rules

- Use `describe_capabilities` before assuming market, symbol, timeframe, freshness, or cohort coverage.
- Use the narrowest granular MCP tool that answers the question. Treat `analyze_symbol` as an optional quick overview, not the default research path or independent confirmation. **Never call it in the same turn as `get_indicators`** — the two return the same readings, and paying for both costs about 2,100 tokens for a second copy.
- **Ask `get_indicators` for `side: "decisive"` when researching.** The undecided readings are about a quarter of the response and `summary`/`resonance` still carry the full counts, so nothing is lost. Narrow with `categories` too when the question is about one family.
- **Issue independent calls together, not one after another.** `get_indicators`, `get_levels` and each `get_method_analysis` do not depend on each other; sent as one batch they cost one round trip instead of four, which is most of the wall-clock a user waits through.
- **Do not open `SKILL.zh-CN.md` or any `*.zh-CN.md` reference at runtime.** They are human reading copies of the English files, so loading one buys nothing and costs as much as the file it mirrors. Answer in the user's language from the English instructions.
- Preserve `notApplicable` and “not computable” as distinct from neutral and from “no signal.”
- Higher timeframes set the backdrop; lower timeframes refine entries. Do not average away a deliberate `1d trend -> 4h pullback -> 1h restart` structure.
- Never compare relative-strength percentiles from different market cohorts as absolute cross-market scores.
- Never substitute a spot series for a futures ticker or silently splice data providers.
- Currency pairs come back the way the market quotes them: USD/JPY, not JPY/USD. Ask for either spelling and the answer arrives in the conventional direction, with `quoteNotice` saying which way round it is. Report it as returned — do not invert prices, levels or targets to match how the user spelled the pair, and do not describe an inverted reading as if the product had produced one.
- FX has no consolidated volume. Do not support an FX action with volume-derived claims unless the response supplies a valid, labelled proxy.
- Fibonacci auto-detection is exploratory. Do not use it in screening weights, strong-confluence claims, or trading actions unless separately calibrated out of sample against nearby-anchor and ordinary support/resistance controls.
- Do not return an entry action without a concrete invalidation level. Do not invent position sizing without the user's portfolio size and risk budget.
- If data are stale, evidence conflicts materially, or a required chart is missing, downgrade to `WATCH` or `AVOID` and say why.

## Evidence contract

Rationale for every rule here, and the failures each one came from, is in [output contract](references/output-contract.md). Read it when a rule looks wrong for your case; the rules themselves are binding without it.

- Every decision-relevant reason returns: claim, backing, why it matters, timeframe, module, evidence fields, analysis timestamp, and that module's chart URL immediately after the reason.
- **Attaching a chart at all? Read [chart links](references/chart-links.md) first** — link form, chart URL versus method page, `conclusion`, presets, and which chart belongs under which bullet. Not optional when a chart is going into the answer.
- **Two charts lead.** `get_indicators` returns both: `chart` (均线/MACD/RSI pinned + up to three by `notability`, six overlays) and `trendChart` (composite 0-100 strength, signed, with the no-trend band). Both go above the method charts. The main chart narrows with `categories`/`side`; the trend chart never narrows. Both are drawn on the last closed bar and carry their own `barTs` — when it differs from the readings' `barTs`, the last bar is still forming, so name the bar you mean.
- **Drawn ≠ decisive.** 均线, MACD and RSI are pinned whatever they read. `notable` says what was drawn and marks pinned ones `core: true`; `signal` is what says bullish or bearish. Name the decisive ones explicitly.
- `get_indicators` returns `readings` columnar: `readings.fields` names the columns, each category holds rows in that order. A null `notability`/`barsSinceFlip` cell means the reading is not taking a side.
- **Rank by `notability`, not by reading order.** It combines recency of the last change of mind with how rarely that indicator takes this side.
- Conclusion-first, and the conclusion carries only what has a clear reading. A method whose engine has nothing to say gets no paragraph and no line saying it was omitted — see "When not to write about a method" in [obsidian vault](references/obsidian-vault.md). Answer in one clause only if asked about that method directly.
- State explicitly when no setup qualifies; never manufacture actions to fill a list.

## Report shape

Lead with the conclusion: one sentence saying what to do, or that there is nothing to do. Then bullets, at most two sentences each, each followed by the chart that shows what it claims:

1. **Signals** — trend strength (score, direction, whether it clears the no-trend threshold), the resonance count, and the decisive readings ranked by `notability`. Both lead charts go here.
2. **Entry** — the price or the condition that would trigger one.
3. **Exit** — the target, and the invalidation that ends the idea.
4. **Where it is** — VCP stage, position in the Chan structure, or which independent methods agree.
5. **Risk** — the room above and below, from `riskReward` in `get_levels` and nothing else.

On risk, all binding:

- Read `riskReward` whole: distance both ways in percent AND price, then `strength` (how much confluence formed the level) and `levelsWithin` (how many levels hold that area, **including the nearest one itself** — 1 is a lone line, 3 is a shelf).
- **A large ratio usually means price is sitting on support, not that the trade is generous.** When `atLevel` is true, say price is resting on the level instead of quoting the ratio as an edge.
- `atLevel` is an observation, never a verdict. Before calling it an entry, require all of: the level below is strong and not thin, room above worth taking, evidence price is holding rather than still falling, and a stated invalidation. Otherwise report the position and stop.
- **Never state an account percentage, position size, or risk budget** — not "risk 0.5–1% per trade", nothing of that kind — unless the user gave their portfolio size and risk budget in this conversation.
- The chart under this bullet, and only prices from `drawnLevels`: see [chart links](references/chart-links.md).

Write so a reader understands on first pass. Precise, not ornamental; avoid jargon labels such as `regime`, `trigger`, `payoff`.

**Never state a win rate, a confidence interval, or any probability of success.** These engines are rule-based with no backtest behind them, so such a number would be invented. `riskReward` is distance, not probability: a ratio of 2 means twice the room, never a 2-in-3 chance. When its bounds are null, say the levels are too close to measure.
