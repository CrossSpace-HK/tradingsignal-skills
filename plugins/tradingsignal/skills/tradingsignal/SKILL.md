---
name: tradingsignal
description: Use TradingSignal MCP for market screening, multi-timeframe opportunity discovery, single-symbol technical research, support/resistance analysis, and conditional trade planning across crypto, FX, commodities, and supported futures. Use when the user wants TradingSignal to find, validate, compare, or plan technical setups; not for macro news research, order execution, or position sizing without an explicit risk budget.
metadata:
  version: "0.1.4"
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
- Higher timeframes define regime; lower timeframes refine entries. Do not average away a deliberate `1d trend -> 4h pullback -> 1h restart` structure.
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
