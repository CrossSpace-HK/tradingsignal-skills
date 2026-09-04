# TradingSignal Skills

[English](README.md) | [中文](README.zh-CN.md)

One open-source TradingSignal agent skill that routes granular market-analysis tools into multiple on-demand workflows. Install once, then use the same `$tradingsignal` entry point for screening, research, and planning.

## One Skill, multiple workflows

| Install once | Included workflows | Resources |
| --- | --- | --- |
| [`tradingsignal`](skills/tradingsignal/) | Cross-market leaders, pullback restarts, reversal validation, single-symbol analysis, conditional trade plans, and risk-first “no valid opportunity” reviews. The router loads only the workflow needed for the request. | [Example prompts](EXAMPLES.md) · [Source](skills/tradingsignal/SKILL.md) |

Agent Skills do not register nested child skills. This package uses one discoverable Skill plus on-demand workflow references, so users install only once and narrow requests do not load every workflow. The former [`tradingsignal-macro-opportunity`](skills/tradingsignal-macro-opportunity/) package remains available for backward compatibility, but new installations should use `tradingsignal`.

## MCP connection and Skill installation are different

- **Connect and authorize TradingSignal MCP** to let the agent access TradingSignal data and analysis tools. You can use those tools directly without installing a Skill, but you must decide what to ask and in what order.
- **Install a Skill** to give the agent a reusable workflow for choosing and orchestrating those tools. This Skill requires an authorized TradingSignal MCP connection; installing it alone does not grant data access.

Complete both steps below to use `tradingsignal`.

## Step 1: Connect and authorize TradingSignal MCP

### Codex

Run in a terminal:

```bash
codex mcp add tradingsignal --url https://tradingsignal.pro/mcp
codex mcp login tradingsignal
```

### Claude Code

Run in a terminal:

```bash
claude mcp add --scope user --transport http tradingsignal https://tradingsignal.pro/mcp
```

Then open Claude Code, enter `/mcp`, select `tradingsignal`, and choose **Authenticate**.

For guided setup and connection checks, visit <https://tradingsignal.pro/connect>.

## Step 2: Install the Skill

### Codex

Paste this into Codex:

```text
$skill-installer Install https://github.com/CrossSpace-HK/tradingsignal-skills/tree/main/skills/tradingsignal
```

Verify the file exists:

```bash
ls ~/.codex/skills/tradingsignal/SKILL.md
```

### Claude Code

Run in a terminal:

```bash
mkdir -p ~/.claude/skills && curl -fsSL https://github.com/CrossSpace-HK/tradingsignal-skills/archive/refs/heads/main.tar.gz | tar -xz -C ~/.claude/skills --strip-components=2 tradingsignal-skills-main/skills/tradingsignal
```

Verify the file exists:

```bash
ls ~/.claude/skills/tradingsignal/SKILL.md
```

## Step 3: Open a new session and use it

Open a new Codex or Claude Code session after installation. A session that was already open before installation will not see the newly added Skill.

```text
$tradingsignal Scan crypto, FX, and commodities for today's three clearest multi-timeframe technical opportunities. Lead with the action, then give entry conditions, invalidation, targets, conflicts, and a chart link for every reason.
```

See [EXAMPLES.md](EXAMPLES.md) for five bilingual, copy-ready workflows: cross-market leaders, pullback restarts, reversal validation, a single-symbol trading plan, and the important “no valid opportunity” outcome.

## Decision boundaries

- Expected actions are `ENTER_ON_PULLBACK`, `ENTER_ON_BREAKOUT`, `WATCH`, `REDUCE_OR_EXIT`, or `AVOID`.
- An entry action is not allowed without a concrete invalidation level.
- Position sizing requires an explicit portfolio risk budget.
- Exploratory Fibonacci results are not screening evidence or an independent trading signal.

## License

MIT
