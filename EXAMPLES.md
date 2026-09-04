# TradingSignal Macro Opportunity Examples

These prompts are for users to copy. They demonstrate distinct decision workflows without adding recurring context to `SKILL.md`.

## 1. 多市场领头羊 / Cross-market leaders

中文：

```text
$tradingsignal-macro-opportunity 扫描 crypto、FX 和现货大宗商品的 1d、4h、1h，找出趋势最强且仍有合理风险收益比的 3 个领头羊。先给 action，再分别说明 regime、trigger、payoff；给出入场条件、失效位、目标和有效期，每条理由紧跟对应模块、同周期的图表链接。跨市场的相对强弱分数不要直接横向比较。
```

English:

```text
$tradingsignal-macro-opportunity Scan crypto, FX, and spot commodities on 1d, 4h, and 1h for the three strongest leaders that still offer defensible risk/reward. Lead with the action, then separate regime, trigger, and payoff. Give entry conditions, invalidation, targets, and expiry, with the matching same-timeframe module chart after every reason. Do not compare relative-strength percentiles across market cohorts as absolute scores.
```

## 2. 回调重启 / Pullback restart

中文：

```text
$tradingsignal-macro-opportunity 找出“1d 保持上升趋势、4h 有序回调但结构未破坏、1h 重新转强”的多头机会，并同时检查空头镜像。只保留结构清晰、失效位明确、目标前空间足够的标的；没有低周期重新确认时只能给 WATCH。每条依据附对应的趋势、结构或支撑阻力图。
```

English:

```text
$tradingsignal-macro-opportunity Find long setups where the 1d uptrend remains intact, 4h is in a controlled pullback without structural damage, and 1h has turned back up; also check the mirrored short setup. Keep only candidates with clear structure, explicit invalidation, and enough room to the next target. Without lower-timeframe confirmation, return WATCH. Attach the matching trend, structure, or levels chart to every reason.
```

## 3. 反转候选验证 / Reversal validation

中文：

```text
$tradingsignal-macro-opportunity 从 crypto、FX 和大宗商品里筛选潜在反转，但只有两个相互独立的结构方法同时支持、且高周期风险可被明确控制时才进入候选。区分“反转已确认”“等待下一根确认”和“只是超买超卖”；单一震荡指标或同一引擎派生的多个信号不算独立共振。输出最多 3 个候选及逐条模块图，没有合格标的就明确说没有。
```

English:

```text
$tradingsignal-macro-opportunity Screen crypto, FX, and commodities for possible reversals, but keep a candidate only when two independent structural methods agree and the higher-timeframe risk can be explicitly controlled. Distinguish confirmed reversal, waiting for next-bar confirmation, and mere overbought/oversold conditions. One oscillator, or multiple signals derived from the same engine, is not independent confluence. Return at most three candidates with a module-specific chart for every reason, or state clearly that none qualify.
```

## 4. 单标的交易计划 / Single-symbol trading plan

中文：

```text
$tradingsignal-macro-opportunity 为 XAUUSD=X 制定一个 1d、4h、1h 的条件式交易计划。不要用一体化摘要代替研究：分别调用最相关的结构方法和多周期支撑阻力，说明每个周期的角色。先给 ENTER_ON_PULLBACK、ENTER_ON_BREAKOUT、WATCH 或 AVOID，再给入场区或触发条件、失效位、两个目标、风险收益比和有效期；每个理由附该模块自己的图。如果没有可辩护的失效位，不得给 ENTER。
```

English:

```text
$tradingsignal-macro-opportunity Build a conditional 1d, 4h, and 1h trading plan for XAUUSD=X. Do not substitute an all-in-one summary for research: call the most relevant structural modules and multi-timeframe levels separately, and explain each timeframe's role. Lead with ENTER_ON_PULLBACK, ENTER_ON_BREAKOUT, WATCH, or AVOID, then give the entry zone or trigger, invalidation, two targets, risk/reward, and expiry. Attach each module's own chart to its reason. Do not return ENTER without a defensible invalidation.
```

## 5. 无机会与冲突 / No valid opportunity

中文：

```text
$tradingsignal-macro-opportunity 做一次风险优先的跨市场扫描。不要为了凑数给交易建议：如果数据过期、多周期或结构方法明显冲突、缺少有效图表验证，或者到下一阻力/支撑的风险收益比不足，就把标的放进 WATCH 或 AVOID。结论先说今天是否存在可执行机会，再列出最接近合格但被拒绝的标的、拒绝原因和需要发生什么才会升级；没有机会时明确输出“今天没有符合条件的交易”。
```

English:

```text
$tradingsignal-macro-opportunity Run a risk-first cross-market scan. Do not manufacture recommendations to fill a list: if data are stale, timeframes or structural methods materially conflict, chart verification is missing, or risk/reward to the next support or resistance is inadequate, place the candidate in WATCH or AVOID. Start by stating whether any executable opportunity exists today, then list the closest rejected candidates, why they failed, and what would upgrade them. If none qualify, explicitly say there is no valid trade today.
```
