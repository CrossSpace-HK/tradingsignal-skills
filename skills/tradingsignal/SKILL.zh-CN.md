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
- 把分析存进用户自己的 Obsidian vault 以便日后复盘，或回看以前的分析：读[写入 Obsidian](references/obsidian-vault.zh-CN.md)。默认不开，没有用户给的 vault 路径就不写任何文件。
- 混合任务按顺序执行：先筛选，再用颗粒化模块分析候选，最后只为通过验证的标的制定计划。

窄问题不要加载全部 reference。

## Skill 版本检查

把英文运行时入口 frontmatter 中的 `metadata.version` 视为当前安装的 Skill 版本。仓库发布脚本会强制它与 Codex 插件清单保持一致。

- 必须调用的 `describe_capabilities` 可能返回 `skillRelease.version`；不要为了检查更新额外调用一次工具。
- 按合法语义版本比较。仅当 `skillRelease.version` 严格高于 `metadata.version` 时，在市场分析结尾提示一次更新。
- 只有比较结果为新版时，才调用 `get_methodology` 并传入 `topic: "skill-update"`；按当前客户端给出返回结果中的更新命令，客户端不明确时应分别标注两条命令，不得猜测。
- 版本相同、服务端版本更旧、任一字段缺失或格式无效时保持静默。版本检查不得阻断用户请求的分析。

## MCP 授权失效时

OAuth 会过期，过期后所有工具调用都会失败。**直说这件事**，并且**只给当前客户端**那一条能修好它的命令：

- **Codex** —— 在终端里输入：`codex mcp login tradingsignal`；或在桌面端
  **Settings → MCP servers → tradingsignal → Authenticate**，完成后重启或新开会话。
- **Claude Code** —— 在终端里输入：`claude mcp login tradingsignal`

**`/mcp` 是查看器，不是授权按钮**：在 Codex 里它只列出当前活跃的 server，所以
「打开 `/mcp` → tradingsignal → Authenticate」是 Claude Code 的习惯用法，会把 Codex 用户
指向一个他的客户端根本没有的控件。它只能用来诊断「这个 server 到底出现了没有」。
**要写清楚在哪里输入**——终端，不是聊天框；客户端不确定时两条都给并各自标注，不要猜。
从用户角度看，「指令写错」和「装坏了」长得一模一样，所以这里说错，代价是整个安装。

然后**停下来等**。不要用取不到的数据继续分析，也不要凭记忆补上缺口。

## 共同规则

- 先用 `describe_capabilities` 确认市场、标的、周期、数据新鲜度和筛选池覆盖。
- 使用能回答问题的最窄 MCP 工具。`analyze_symbol` 只用于快速概览，不作为默认深度研究或独立确认。**不要在同一轮里同时调 `analyze_symbol` 和 `get_indicators`**——两者返回的是同一批读数，多付大约 2,100 token 只为拿到第二份副本。
- **研究时给 `get_indicators` 传 `side: "decisive"`。** 未表态的读数约占响应的四分之一，而完整计数仍然在 `summary` / `resonance` 里，所以没有信息损失。问题只涉及某一类时，再加 `categories`。
- **互不依赖的调用要一次发出去，不要一个接一个。** `get_indicators`、`get_levels` 和各个 `get_method_analysis` 之间没有依赖，一批发出只花一个往返而不是四个，用户等待的时间大部分就在这里。
- **运行时不要打开 `SKILL.zh-CN.md` 或任何 `*.zh-CN.md` 参考文件。** 它们是英文文件的中文阅读版，加载一份什么也不多，却要付和原文件一样多的 token。按英文指令执行，用用户的语言作答。
- `notApplicable`、无法计算、中性和无信号是不同状态，不能合并。
- 高周期定义市场状态，低周期优化入场；不要把 `1d 趋势 -> 4h 回调 -> 1h 重启` 平均成冲突。
- 不要把不同市场筛选池的相对强弱百分位当成可直接横比的绝对分数。
- 不得用现货序列冒充期货，也不得静默拼接不同数据源。
- 货币对一律按市场惯用方向返回：USD/JPY，不是 JPY/USD。用户怎么写都行，返回的是常规方向，并附 `quoteNotice` 说明方向。**按返回的方向如实转述**——不要为了迎合用户的写法把价格、关键位或目标位倒过来算，也不要把倒过来的读数说成是产品给出的。
- 外汇没有统一成交量；除非响应提供有效且明确标注的代理，否则不得用量能衍生结论支持外汇交易动作。
- 自动斐波那契仍是探索功能。完成样本外校准并通过邻近锚点与普通支撑阻力对照前，不得进入筛选权重、强共振或交易动作。
- 没有明确失效位不得给入场动作；用户未提供组合规模和风险预算时不得虚构仓位。
- 数据过期、证据明显冲突或关键图缺失时，降级为 `WATCH` 或 `AVOID` 并解释原因。

## 证据契约

每条规则背后的理由、以及它各自来自哪次失败，见[输出契约](references/output-contract.zh-CN.md)。某条规则在你的场景里看起来不对时再读它；不读，规则一样有约束力。

- 每条与决策相关的理由都要给出：结论、依据、为什么重要、周期、模块、证据字段、分析时间戳，以及该模块的图链接，紧跟在理由后面。
- 图一律写成 markdown 链接，链接文字要写明标的、周期、方法——`[查看 ETH/USDT 4小时 TD9 图](url)`。不许裸 URL，不许内嵌图片（`![](...)`）：聊天客户端不保证会取远程图片。
- **图链接 ≠ 方法页链接。** 图是一张图，方法页是实时交互分析。方法页链接绝不能自己拼——用工具返回的 `openIn`，它带着分析当时的那根 K 线和快照。
- 任何返回图的工具都要传 `conclusion`（`get_indicators`、`get_method_analysis`、`get_chart`、`get_levels`）：一句话，≤80 字，**是你的判断**，不是引擎读数。
- 图片会自己标注，历史变了它自己会写出来。不要把这行标注复述成"我核对过"，也不要说这张图和分析的其他输入一致——校验只覆盖该标的在该周期上的这条 K 线序列。
- 优先用 `get_method_analysis` 返回的图；否则用 `get_chart` 加对应预设（`price`、`chan`、`td9`、`wyckoff`、`vcp`、`levels`、`signals`、`trend`）。图只是背景而非证据本身时要说明。
- **两张图排最前面。** `get_indicators` 一次都给：`chart`（均线/MACD/RSI 固定 + 按 `notability` 最多再三个，共六个叠加）和 `trendChart`（综合 0–100 强弱，带方向正负号与无趋势阈值带）。两张都排在方法图之上。主图跟着 `categories`/`side` 收窄，趋势图永不收窄。两张都画最后一根已收盘 K 线并带自己的 `barTs`；和读数的 `barTs` 不同时，说明最新一根还在走，要说清指的是哪一根。
- **画了 ≠ 在表态。** 均线、MACD、RSI 不管读数如何都画。`notable` 给出画了哪几个并用 `core: true` 标出固定位；表态与否看 `signal`。正文必须点名真表态的是哪几个。
- `get_indicators` 的 `readings` 是列式的：`readings.fields` 给出列名，每一类下面是按该顺序排列的行。`notability`／`barsSinceFlip` 为 null 表示这条读数没有表态。
- **用 `notability` 排序，不按读到的先后。** 它由"多久前转向"和"这个指标平时多罕见地这样读"合成。
- 结论优先，且结论只写有明确读数的东西。引擎没什么可说的方法不写段落，也不写"已省略"这一行——各引擎的"没什么可说"见 [obsidian vault](references/obsidian-vault.zh-CN.md)。用户直接问该方法时，才用一句话回答。
- 没有标的合格时直接说明，不得为凑数制造交易动作。

## 报告结构

先给结论：一句话说清做什么，或者说清今天没有可做的。然后用 bullet 展开，每条最多两句，每条后面跟着能证明它的那张图：

1. **信号**——趋势强弱（分数、方向、有没有超过无趋势阈值）、共振数，以及按 `notability` 排序的表态读数。两张头图放这里。
2. **入场点**——具体价位，或者什么条件成立才进。
3. **计划出场**——目标位，以及说明想法已错的失效位。
4. **它现在在哪**——VCP 第几阶段、缠论在什么位置，或哪几个独立方法同时支持。
5. **风险**——上下各有多少空间，**只能**取自 `get_levels` 的 `riskReward`。

关于风险这一条，以下全部有约束力：

- `riskReward` 要整体读：上下距离同时给百分比和价格，再看 `strength`（这个位由多少共振形成）和 `levelsWithin`（有几条位在托这个区域，**含最近那一条本身**——1 是孤线，3 是台阶）。
- **比值很大通常意味着价格正贴在支撑上，而不是这笔交易划算。** `atLevel` 为真时，说"价格正踩在这个位上"，不要把比值当成优势报出来。
- `atLevel` 只是观察，不是结论。要叫它入场，必须同时满足：下方的位够强且不薄、上方有值得拿的空间、有证据表明价格是在守而不是还在跌、并给出失效位。否则只报位置，到此为止。
- **绝不给出账户百分比、仓位大小或风险预算**——"每笔风险 0.5–1%"这类数字一律不给，除非用户在本次对话里给了自己的资金规模和风险预算。
- 这一条下面的图必须是 `get_levels` 的支撑阻力图。没有就说没有匹配的图，绝不拿别的模块的图来凑。
- **只能引用 `drawnLevels` 里列出的价格**——那正是所附图上画了什么。绝不自己算"最近的位"：`riskReward` 已经给了，且其边界保证在 `drawnLevels` 里。

每一条 bullet 都要配能证明它的那张图；没有就说没有。

写得让人第一遍就读懂。精确，不要修饰；避免 `regime`、`trigger`、`payoff` 这类术语标签。

**绝不给出胜率、置信区间或任何成功概率。** 这些引擎是规则驱动的，背后没有回测，这类数字只能是编的。`riskReward` 量的是距离不是概率：比值 2 表示空间是两倍，绝不表示三分之二的胜算。
