# Conditional Trade Plan

Use this workflow after a symbol has survived screening or when the user directly requests a plan for a named symbol.

## Build the plan from evidence

Use granular method outputs and `get_levels` to select the nearest defensible:

- entry zone or breakout trigger;
- confirmation condition;
- invalidation or stop;
- first and second targets;
- estimated risk/reward;
- expiry or event that makes the plan stale.

Higher timeframes define regime and major invalidation; lower timeframes refine timing. Reject the setup when data are stale, methods materially conflict, invalidation is ambiguous, or the next support/resistance leaves inadequate payoff.

Do not turn a conditional setup into an unconditional forecast. State what must happen before entry and what would prove the thesis wrong. Do not provide position size unless the user supplies portfolio size and a risk budget.

## Response shape

Lead with one action: `ENTER_ON_PULLBACK`, `ENTER_ON_BREAKOUT`, `WATCH`, `REDUCE_OR_EXIT`, or `AVOID`.

Then provide:

```json
{
  "symbol": "BTC/USDT",
  "direction": "LONG",
  "action": "ENTER_ON_PULLBACK",
  "horizon": "swing",
  "conclusion": "Wait for a pullback into the entry zone and renewed 4h strength.",
  "plan": {
    "entryZone": [0, 0],
    "trigger": "...",
    "invalidation": 0,
    "targets": [0, 0],
    "riskReward": 0,
    "validUntil": "..."
  },
  "reasons": [
    {
      "claim": "...",
      "backing": "...",
      "whyItMatters": "...",
      "timeframe": "4h",
      "module": "chan",
      "evidenceFields": ["..."],
      "asOf": "...",
      "chartUrl": "https://...png"
    }
  ],
  "conflicts": [],
  "caveats": []
}
```

If chart generation fails, keep the structured facts, cap the action at `WATCH`, and disclose the missing visual check.
