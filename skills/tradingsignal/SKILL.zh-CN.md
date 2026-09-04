[English](SKILL.md) | [中文](SKILL.zh-CN.md)

# TradingSignal

这是总 Skill 的中文阅读版。运行时以 [SKILL.md](SKILL.md) 的英文指令为准。

根据用户的问题选择最窄的 TradingSignal 工作流，只加载当前工作流需要的 reference，并先给出决策结论。

## 选择工作流

- 多市场领头羊或新近转强：先读共享的[市场筛选基础流程](references/opportunity-scan.zh-CN.md)，再读[多市场领头羊](references/cross-market-leaders.zh-CN.md)。
- 高周期趋势、中周期回调、低周期重启：先读共享的[市场筛选基础流程](references/opportunity-scan.zh-CN.md)，再读[回调重启](references/pullback-restart.zh-CN.md)。
- 反转或衰竭候选：先读共享的[市场筛选基础流程](references/opportunity-scan.zh-CN.md)，再读[反转验证](references/reversal-validation.zh-CN.md)。
- 研究单个标的、周期或技术方法：读[单标的分析](references/symbol-analysis.zh-CN.md)。
- 入场区、触发条件、失效位、目标、风险收益比或完整计划：读[条件式交易计划](references/trade-plan.zh-CN.md)。市场级请求应先使用对应的筛选工作流。
- 风险优先审查、证据冲突或明确判断“今天没有机会”：先读共享的[市场筛选基础流程](references/opportunity-scan.zh-CN.md)，再读[无有效机会审查](references/no-trade-review.zh-CN.md)。
- 混合任务按顺序执行：先筛选，再用颗粒化模块分析候选，最后只为通过验证的标的制定计划。

窄问题不要加载全部 reference。

## 共同规则

- 先用 `describe_capabilities` 确认市场、标的、周期、数据新鲜度和筛选池覆盖。
- 使用能回答问题的最窄 MCP 工具。`analyze_symbol` 只用于快速概览，不作为默认深度研究或独立确认。
- `notApplicable`、无法计算、中性和无信号是不同状态，不能合并。
- 高周期定义市场状态，低周期优化入场；不要把 `1d 趋势 -> 4h 回调 -> 1h 重启` 平均成冲突。
- 不要把不同市场筛选池的相对强弱百分位当成可直接横比的绝对分数。
- 不得用现货序列冒充期货，也不得静默拼接不同数据源。
- 外汇没有统一成交量；除非响应提供有效且明确标注的代理，否则不得用量能衍生结论支持外汇交易动作。
- 自动斐波那契仍是探索功能。完成样本外校准并通过邻近锚点与普通支撑阻力对照前，不得进入筛选权重、强共振或交易动作。
- 没有明确失效位不得给入场动作；用户未提供组合规模和风险预算时不得虚构仓位。
- 数据过期、证据明显冲突或关键图缺失时，降级为 `WATCH` 或 `AVOID` 并解释原因。

## 证据契约

每条影响决策的理由必须包含结论、数据依据、重要性、周期、模块、证据字段、分析时间和对应模块图表 URL。图表链接紧跟理由，不要集中放在末尾。

优先使用 `get_method_analysis` 返回的图；否则用相同标的和周期调用 `get_chart`，并选择 `price`、`chan`、`td9`、`wyckoff` 或 `vcp` 对应预设。若图只是背景而非数字证据的直接叠加，应明确说明。

回答必须结论优先。没有标的合格时直接说明，不得为凑数制造交易动作。
