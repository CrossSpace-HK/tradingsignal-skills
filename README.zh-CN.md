# TradingSignal Skills

[English](README.md) | [中文](README.zh-CN.md)

一个开源的 TradingSignal 总 Skill，把颗粒化市场分析工具路由到多个按需加载的工作流。只需安装一次，即可用同一个 `$tradingsignal` 入口完成筛选、研究和交易计划。

## 一个 Skill，多种工作流

| 安装一次 | 内含工作流 | 相关资料 |
| --- | --- | --- |
| [`tradingsignal`](skills/tradingsignal/) | 多市场领头羊、回调重启、反转验证、单标的分析、条件式交易计划，以及风险优先的“无有效机会”审查。总入口只加载当前问题需要的工作流。 | [示例提示词](EXAMPLES.md) · [源码](skills/tradingsignal/SKILL.md) |

Agent Skills 不能注册真正嵌套的子 Skill。本仓库采用“一个可发现的总 Skill + 按需加载的 workflow references”，因此用户只安装一次，窄问题也不会加载全部流程。旧的 [`tradingsignal-macro-opportunity`](skills/tradingsignal-macro-opportunity/) 继续保留兼容，但新用户应安装 `tradingsignal`。

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

把下面这句话粘贴到 Codex：

```text
$skill-installer Install https://github.com/CrossSpace-HK/tradingsignal-skills/tree/main/skills/tradingsignal
```

检查文件是否已经安装：

```bash
ls ~/.codex/skills/tradingsignal/SKILL.md
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

## 决策边界

- 可返回的 action 包括 `ENTER_ON_PULLBACK`、`ENTER_ON_BREAKOUT`、`WATCH`、`REDUCE_OR_EXIT` 和 `AVOID`。
- 没有明确失效位时，不允许给出进场 action。
- 只有用户提供明确的组合风险预算后，才能给出仓位大小。
- 探索性斐波那契结果不作为筛选证据或独立交易信号。

## 许可证

MIT
