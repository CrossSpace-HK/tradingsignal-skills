[English](reversal-validation.md) | [中文](reversal-validation.zh-CN.md)

# Reversal Validation

Use this workflow to distinguish a structurally credible reversal from an oscillator extreme or an unconfirmed exhaustion signal.

## Candidate generation

Use `div_bull`, `div_bear`, `td_buy`, `td_sell`, `chan_buy`, and `wyckoff_accum` to create a watchlist. These tags are candidates, not reversal proof.

## Confirmation standard

- Require agreement from at least two independent structural methods before calling a reversal confirmed.
- Multiple signals from one engine are one evidence family, not independent confluence.
- Distinguish `confirmed reversal`, `waiting for next-bar confirmation`, and `overbought/oversold only`.
- Control higher-timeframe risk explicitly. A lower-timeframe reversal trigger against a strong higher-timeframe trend normally remains `WATCH`.
- Identify the price or structure that invalidates the reversal and the next confirmation event that would upgrade it.

Return at most three candidates. Attach each method's own chart to its reason, and state clearly when no candidate reaches the confirmation standard.
