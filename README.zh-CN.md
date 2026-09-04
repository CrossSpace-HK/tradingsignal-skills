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

## 连接 MCP 和安装 Skill 是两件事

- **连接并授权 TradingSignal MCP**：让 Agent 可以访问 TradingSignal 的数据和分析工具。不安装 Skill 也能直接使用这些工具，但需要用户自己决定问什么、按什么顺序调用。
- **安装 Skill**：给 Agent 一套可复用的工作流，由它选择并编排这些工具。这个 Skill 依赖已经授权的 TradingSignal MCP；只安装 Skill 并不会自动获得数据访问权限。

要使用 `tradingsignal`，请完成下面两个步骤。

## 第一步：连接并授权 TradingSignal MCP

### Codex

在终端执行：

```bash
codex mcp add tradingsignal --url https://tradingsignal.pro/mcp
codex mcp login tradingsignal
```

### Claude Code

在终端执行：

```bash
claude mcp add --scope user --transport http tradingsignal https://tradingsignal.pro/mcp
```

然后打开 Claude Code，输入 `/mcp`，选择 `tradingsignal`，再选择 **Authenticate**。

如需图形化引导和连接状态检查，请打开 <https://tradingsignal.pro/connect>。

## 第二步：安装 Skill

### Codex

使用 Codex plugin marketplace 安装；以后可以通过官方升级命令获取更新：

```bash
codex plugin marketplace add CrossSpace-HK/tradingsignal-skills
codex plugin add tradingsignal@tradingsignal
```

检查 Codex 是否列出已安装插件：

```bash
codex plugin list --marketplace tradingsignal
```

### Claude Code

在终端执行：

```bash
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/CrossSpace-HK/tradingsignal-skills/archive/refs/heads/main.tar.gz | tar -xz -C ~/.claude/skills --strip-components=2 tradingsignal-skills-main/skills/tradingsignal
```

检查文件是否已经安装：

```bash
ls ~/.claude/skills/tradingsignal/SKILL.md
```

## 第三步：新开会话并使用

安装后新开一个 Codex 或 Claude Code 会话。安装前已经打开的旧会话不会自动看到新增的 Skill。

```text
$tradingsignal 扫描 crypto、FX 和大宗商品，找出今天最值得关注的 3 个多周期交易机会。先给结论和 action，再给入场条件、失效位、目标、冲突；每条理由都附对应图表链接。
```

[EXAMPLES.md](EXAMPLES.md) 提供五组中英双语、可直接复制的工作流：多市场领头羊、回调重启、反转候选验证、单标的交易计划，以及重要的“无有效机会”输出。

## 更新与卸载

MCP 和 Skill 的更新机制不同：

- **MCP 在服务端更新。** 新开一个会话，让客户端重新连接并取得最新工具定义；不需要重新安装 MCP。
- **Skill 是本地文件。** Codex 可以用官方 plugin 命令刷新 Git marketplace；Claude Code 仍需清理后重装。两边更新后都应新开会话。

Codex 请刷新已经配置的 marketplace：

```bash
codex plugin marketplace upgrade tradingsignal
```

Claude Code 可以用下面这条更新命令；它只删除准确的 Skill 目录，然后重新安装：

```bash
rm -rf ~/.claude/skills/tradingsignal && mkdir -p ~/.claude/skills && curl -fsSL https://github.com/CrossSpace-HK/tradingsignal-skills/archive/refs/heads/main.tar.gz | tar -xz -C ~/.claude/skills --strip-components=2 tradingsignal-skills-main/skills/tradingsignal
```

Codex 用 `codex plugin remove tradingsignal@tradingsignal` 卸载。Claude Code 只执行准确目录的删除命令，不要重新安装。MCP 连接与 Skill 相互独立；删除 Skill 不会删除 MCP 授权。

## 决策边界

- 可返回的 action 包括 `ENTER_ON_PULLBACK`、`ENTER_ON_BREAKOUT`、`WATCH`、`REDUCE_OR_EXIT` 和 `AVOID`。
- 没有明确失效位时，不允许给出进场 action。
- 只有用户提供明确的组合风险预算后，才能给出仓位大小。
- 探索性斐波那契结果不作为筛选证据或独立交易信号。

## 许可证

MIT
