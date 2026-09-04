[English](opportunity-scan.md) | [中文](opportunity-scan.zh-CN.md)

# Opportunity Scan

Use this workflow for cross-market discovery, leaders, fresh strength, pullback restarts, breakouts, reversals, and “is there a valid trade today?” requests.

## 1. Confirm the searchable universe

Call `describe_capabilities` and report requested markets or timeframes that are unavailable. Use precomputed `screen_market` results before live deep analysis. Request the full relevant cohort; never let a small default limit masquerade as a market-wide scan.

For crypto, FX, and spot commodities, compare the supported 1h, 4h, and 1d cohorts. Legacy `=F` futures are different instruments: screen their available daily rows and use live 1w/1mo analysis only after shortlisting when supported.

## 2. Generate candidates

Search for:

- `strong` and `fresh_strength` for leaders and newly aligned trends;
- `breakout` for continuation triggers;
- `near_cost` for strong instruments pulling back instead of requiring a chase;
- `div_bull`, `div_bear`, `td_buy`, `td_sell`, `chan_buy`, and `wyckoff_accum` for reversal or exhaustion watchlists.

Judge each candidate on three things, and report them separately:

1. **Where it stands** — higher-timeframe stage, trend, position against its moving averages, and how it ranks inside its own market cohort;
2. **What just happened** — fresh resonance, a breakout, a Chan point, TD9 maturity, a Wyckoff event, or a divergence;
3. **Room either way** — distance from entry to invalidation, and from entry to the next defensible target.

Write these in plain words. Do not label them `regime`, `trigger` or `payoff`: those are jargon to the person reading the report.

Never present this as a win probability. There is no backtest behind these engines, so a percentage would be invented.

## 3. Recognize valid multi-timeframe structures

Prefer:

- aligned continuation when 1d, 4h, and 1h point the same way;
- pullback restart when 1d defines the trend, 4h is a controlled countertrend pullback with structure intact, and 1h turns back with the higher-timeframe direction; mirror for shorts;
- reversal only when at least two independent structural methods agree and higher-timeframe risk is explicitly controlled.

A lone oscillator is not structural confirmation. Multiple outputs derived from one engine are not independent confluence.

## 4. Validate only the shortlist

Deep-dive the best 5–10 candidates using the narrowest modules:

- `get_method_analysis(engine="vcp")` for stage, trend-template criteria, pivot, and stop;
- `get_method_analysis(engine="chan")` for structural points, centers, confirmation, and invalidation;
- `get_method_analysis(engine="wyckoff")` for range, phase, events, entry, stop, and target;
- `get_method_analysis(engine="td9")` for count maturity, TDST, risk level, and next-bar confirmation;
- `get_levels` for multi-timeframe support, resistance, and clustering;
- `get_candles` or `run_engine` only when granular results lack required evidence or the user explicitly asks for raw/advanced output.

Confirmed, active, recent structure outranks stale or unconfirmed signals. If indicator snapshots matter, preserve every indicator's name/id, value, state, timeframe, and threshold or rule; a resonance summary does not replace its inputs.

## 5. Return the decision

Start by stating whether an executable opportunity exists. Then return at most 1–3 `topActions`, followed by `watchlist`, `avoided`, and `coverageGaps`.

Each candidate must have one of `ENTER_ON_PULLBACK`, `ENTER_ON_BREAKOUT`, `WATCH`, `REDUCE_OR_EXIT`, or `AVOID`, plus direction, horizon, entry condition, invalidation, targets, estimated risk/reward, expiry, conflicts, caveats, and chart-bound reasons.

When nothing qualifies, say so explicitly and show the closest rejected candidates, why they failed, and what would upgrade them.
