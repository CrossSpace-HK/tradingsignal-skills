# TradingSignal Skills

[English](README.md) | [中文](README.zh-CN.md)

一个开源的 TradingSignal 总 Skill，把颗粒化市场分析工具路由到多个按需加载的工作流。只需安装一次，即可用同一个 `$tradingsignal` 入口完成筛选、研究和交易计划。

## 一个 Skill，多种工作流

| 安装一次 | 内含工作流 | 相关资料 |
| --- | --- | --- |
| [`tradingsignal`](skills/tradingsignal/SKILL.zh-CN.md) | 多市场领头羊、回调重启、反转验证、单标的分析、条件式交易计划，以及风险优先的“无有效机会”审查。总入口只加载当前问题需要的工作流。 | [示例提示词](EXAMPLES.md) · [中文说明](skills/tradingsignal/SKILL.zh-CN.md) |

Agent Skills 不能注册真正嵌套的子 Skill。本仓库采用“一个可发现的总 Skill + 按需加载的 workflow references”，因此用户只安装一次，窄问题也不会加载全部流程。旧的 [`tradingsignal-macro-opportunity`](skills/tradingsignal-macro-opportunity/SKILL.zh-CN.md) 继续保留兼容，但新用户应安装 `tradingsignal`。

当前六个独立维护的工作流是：

1. [多市场领头羊](skills/tradingsignal/references/cross-market-leaders.zh-CN.md)
2. [回调重启](skills/tradingsignal/references/pullback-restart.zh-CN.md)
3. [反转验证](skills/tradingsignal/references/reversal-validation.zh-CN.md)
4. [单标的分析](skills/tradingsignal/references/symbol-analysis.zh-CN.md)
5. [条件式交易计划](skills/tradingsignal/references/trade-plan.zh-CN.md)
6. [无有效机会审查](skills/tradingsignal/references/no-trade-review.zh-CN.md)

市场级工作流共用一份[筛选基础流程](skills/tradingsignal/references/opportunity-scan.zh-CN.md)。以后新增 workflow，只需增加一个聚焦的 reference，并在 `SKILL.md` 增加一条路由；不需要让用户再安装一个 Skill。

## MCP 数据访问和 Skill 工作流是两件事

- **TradingSignal MCP**：让 Agent 可以访问 TradingSignal 的数据和分析工具；工具读取账户前仍需完成授权。
- **Skill**：给 Agent 一套可复用的工作流，由它选择并编排这些工具。

Codex 与 Claude Code 的插件都会一次装好 Skill 和 MCP 定义。账户授权仍是独立的用户操作，因为插件本身不包含任何账户凭证。

## 安装工作流包

### Codex

使用 Codex plugin marketplace 安装；以后可以通过官方升级命令获取更新：

```bash
codex plugin marketplace add CrossSpace-HK/tradingsignal-skills
codex plugin add tradingsignal@tradingsignal
codex mcp login tradingsignal
```

插件已经同时提供 Skill 与 `tradingsignal` MCP server 定义，请勿再添加第二条 standalone MCP。登录命令会打开 TradingSignal 的 OAuth 授权流程。

检查 Codex 是否列出已安装插件：

```bash
codex plugin list --marketplace tradingsignal
```

### Claude Code

在 Claude Code 内添加本仓库 marketplace 并安装插件：

```bash
/plugin marketplace add CrossSpace-HK/tradingsignal-skills
/plugin install tradingsignal@tradingsignal
```

插件同时包含 Skill 和 TradingSignal MCP 定义。若 Claude 提示重启，可新开会话，也可执行 `/reload-plugins`。随后输入 `/mcp`，选择插件提供的 `tradingsignal` server，再选择 **Authenticate**。

在 Claude Code 内检查安装状态：

```bash
/plugin
```

已安装列表中应显示 `tradingsignal@tradingsignal` 且为 enabled。

如需图形化引导、只安装 MCP 的手动备用路径或连接状态检查，请打开 <https://tradingsignal.pro/connect>。

## 加载并使用

Codex 安装后请新开会话。Claude Code 可以在当前会话执行 `/reload-plugins` 加载新插件，也可以重启。

```text
$tradingsignal 扫描 crypto、FX 和大宗商品，找出今天最值得关注的 3 个多周期交易机会。先给结论和 action，再给入场条件、失效位、目标、冲突；每条理由都附对应图表链接。
```

Claude Code 使用带插件命名空间的命令：

```text
/tradingsignal:tradingsignal 扫描 crypto、FX 和大宗商品，找出今天最值得关注的 3 个多周期交易机会。先给结论和 action，再给入场条件、失效位、目标、冲突；每条理由都附对应图表链接。
```

[EXAMPLES.md](EXAMPLES.md) 提供五组中英双语、可直接复制的工作流：多市场领头羊、回调重启、反转候选验证、单标的交易计划，以及重要的“无有效机会”输出。

## 更新与卸载

MCP 和 Skill 的更新机制不同：

- **TradingSignal 服务实现由服务端更新。** 重连或新开会话即可取得变化后的工具定义，不需要重装 MCP。
- **插件和 Skill 文件在本地更新。** Codex 与 Claude Code 都可以用官方 plugin 命令刷新本 Git marketplace。

Codex 请刷新已经配置的 marketplace：

```bash
codex plugin marketplace upgrade tradingsignal
```

Claude Code 先刷新 marketplace 元数据，再更新已安装插件：

```bash
claude plugin marketplace update tradingsignal
claude plugin update tradingsignal@tradingsignal
```

Codex 用 `codex plugin remove tradingsignal@tradingsignal` 卸载。Claude Code 用 `claude plugin uninstall tradingsignal@tradingsignal` 卸载。删除插件不会自动撤销 TradingSignal 授权；如需撤销，请到 TradingSignal 连接页面操作。

## 发布 Skill 版本

维护者必须通过 `python3 scripts/release.py --set <version>` 发布。脚本会同步源 Skill、插件内副本以及 Codex/Claude 两份插件清单，再把 Skill 和完整插件包摘要写入 `release.json`。CI 会运行 `python3 scripts/release.py --check`，因此 Skill 或插件内容变化但发布版本记录未更新时无法通过。

## 决策边界

- 可返回的 action 包括 `ENTER_ON_PULLBACK`、`ENTER_ON_BREAKOUT`、`WATCH`、`REDUCE_OR_EXIT` 和 `AVOID`。
- 没有明确失效位时，不允许给出进场 action。
- 只有用户提供明确的组合风险预算后，才能给出仓位大小。
- 探索性斐波那契结果不作为筛选证据或独立交易信号。

## 许可证

MIT
