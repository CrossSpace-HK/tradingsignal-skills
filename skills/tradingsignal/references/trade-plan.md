[English](trade-plan.md) | [中文](trade-plan.zh-CN.md)

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

Higher timeframes set the backdrop and the major invalidation; lower timeframes refine timing. Reject the setup when data are stale, methods materially conflict, invalidation is ambiguous, or there is too little room to the next support or resistance.

Do not turn a conditional setup into an unconditional forecast. State what must happen before entry and what would prove the thesis wrong. Do not provide position size unless the user supplies portfolio size and a risk budget.

## Response shape

Use the report shape in SKILL.md. Do not invent a different one here: when this
file and SKILL.md disagreed, the model followed neither and produced a table.

Lead with one action -- enter on a pullback, enter on a breakout, watch, reduce
or exit, or avoid -- in one sentence. Then exactly these four bullets, at most
two sentences each, with the matching chart immediately after the bullet it
supports:

1. **Entry** -- the price zone, or the condition that would trigger one.
2. **Exit** -- the targets, and the invalidation that ends the idea.
3. **Where it is** -- which VCP stage, where in the Chan structure, or which
   independent methods agree, and what each timeframe contributed.
4. **Risk** -- the room above and below, from `riskReward` in `get_levels`.
   Never a win rate or a confidence figure; when `riskReward` returns null
   bounds, say the levels are too close to measure against.

Return JSON only if the user asks for it. The default answer is the four
bullets, because a person is reading it.

If chart generation fails, keep the structured facts, cap the action at `WATCH`, and disclose the missing visual check.
