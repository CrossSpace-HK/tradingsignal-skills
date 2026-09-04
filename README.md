# TradingSignal Skills

[English](README.md) | [中文](README.zh-CN.md)

One open-source TradingSignal agent skill that routes granular market-analysis tools into multiple on-demand workflows. Install once, then use the same `$tradingsignal` entry point for screening, research, and planning.

## One Skill, multiple workflows

| Install once | Included workflows | Resources |
| --- | --- | --- |
| [`tradingsignal`](skills/tradingsignal/) | Cross-market leaders, pullback restarts, reversal validation, single-symbol analysis, conditional trade plans, and risk-first “no valid opportunity” reviews. The router loads only the workflow needed for the request. | [Example prompts](EXAMPLES.md) · [Source](skills/tradingsignal/SKILL.md) |

Agent Skills do not register nested child skills. This package uses one discoverable Skill plus on-demand workflow references, so users install only once and narrow requests do not load every workflow. The former [`tradingsignal-macro-opportunity`](skills/tradingsignal-macro-opportunity/) package remains available for backward compatibility, but new installations should use `tradingsignal`.

The six independently maintained workflows are:

1. [Cross-market leaders](skills/tradingsignal/references/cross-market-leaders.md)
2. [Pullback restart](skills/tradingsignal/references/pullback-restart.md)
3. [Reversal validation](skills/tradingsignal/references/reversal-validation.md)
4. [Single-symbol analysis](skills/tradingsignal/references/symbol-analysis.md)
5. [Conditional trade plan](skills/tradingsignal/references/trade-plan.md)
6. [No-valid-opportunity review](skills/tradingsignal/references/no-trade-review.md)

Market-wide workflows share one [screening playbook](skills/tradingsignal/references/opportunity-scan.md). Adding a future workflow requires a focused reference plus one routing line in `SKILL.md`; it does not create another installation.

## MCP access and Skill instructions are different

- **TradingSignal MCP** gives the agent access to TradingSignal data and analysis tools. Authorization is still required before the tools can read your account.
- **The Skill** gives the agent reusable workflows for choosing and orchestrating those tools.

Both the Codex and Claude Code plugins install these two pieces together. Authorization remains a separate user step because the plugin never contains account credentials.

## Install the workflow package

### Codex

Use the Codex plugin marketplace so future updates can be fetched with the official upgrade command:

```bash
codex plugin marketplace add CrossSpace-HK/tradingsignal-skills
codex plugin add tradingsignal@tradingsignal
codex mcp login tradingsignal
```

The plugin supplies both the Skill and the `tradingsignal` MCP server definition; do not add a second standalone MCP entry. The login command opens TradingSignal's OAuth flow.

Verify that Codex lists the installed plugin:

```bash
codex plugin list --marketplace tradingsignal
```

### Claude Code

Inside Claude Code, add this repository as a marketplace and install the plugin:

```bash
/plugin marketplace add CrossSpace-HK/tradingsignal-skills
/plugin install tradingsignal@tradingsignal
```

The plugin contains both the Skill and the TradingSignal MCP definition. If Claude asks for a restart, either start a new session or run `/reload-plugins`. Then enter `/mcp`, select the plugin-provided `tradingsignal` server, and choose **Authenticate**.

Verify installation inside Claude Code:

```bash
/plugin
```

The installed list should show `tradingsignal@tradingsignal` as enabled.

For guided setup, a manual MCP-only fallback, and connection checks, visit <https://tradingsignal.pro/connect>.

## Load and use it

Open a new Codex session after installation. Claude Code can load a newly installed plugin in the current session with `/reload-plugins`; restarting also works.

```text
$tradingsignal Scan crypto, FX, and commodities for today's three clearest multi-timeframe technical opportunities. Lead with the action, then give entry conditions, invalidation, targets, conflicts, and a chart link for every reason.
```

In Claude Code, use the plugin-namespaced command instead:

```text
/tradingsignal:tradingsignal Scan crypto, FX, and commodities for today's three clearest multi-timeframe technical opportunities. Lead with the action, then give entry conditions, invalidation, targets, conflicts, and a chart link for every reason.
```

See [EXAMPLES.md](EXAMPLES.md) for five bilingual, copy-ready workflows: cross-market leaders, pullback restarts, reversal validation, a single-symbol trading plan, and the important “no valid opportunity” outcome.

## Updates and removal

MCP and Skill updates behave differently:

- **TradingSignal's server implementation updates server-side.** Reconnect or start a new session to fetch changed tool definitions; no MCP reinstall is required.
- **Plugin and Skill files update locally.** Both Codex and Claude Code can refresh this Git marketplace with official plugin commands.

For Codex, refresh the configured marketplace:

```bash
codex plugin marketplace upgrade tradingsignal
```

For Claude Code, refresh the marketplace metadata and update the installed plugin:

```bash
claude plugin marketplace update tradingsignal
claude plugin update tradingsignal@tradingsignal
```

For Codex, uninstall with `codex plugin remove tradingsignal@tradingsignal`. For Claude Code, use `claude plugin uninstall tradingsignal@tradingsignal`. Removing a plugin does not revoke the TradingSignal authorization itself; revoke it from the TradingSignal connection page if needed.

## Publishing a Skill release

Maintainers must publish through `python3 scripts/release.py --set <version>`. It synchronizes the source Skill, packaged plugin copy, and both Codex and Claude plugin manifests, then records Skill and whole-package digests in `release.json`. CI runs `python3 scripts/release.py --check`, so changed Skill or plugin content cannot pass with an unchanged release record.

## Decision boundaries

- Expected actions are `ENTER_ON_PULLBACK`, `ENTER_ON_BREAKOUT`, `WATCH`, `REDUCE_OR_EXIT`, or `AVOID`.
- An entry action is not allowed without a concrete invalidation level.
- Position sizing requires an explicit portfolio risk budget.
- Exploratory Fibonacci results are not screening evidence or an independent trading signal.

## License

MIT
