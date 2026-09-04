# TradingSignal Skills

Open-source agent skills for turning TradingSignal's granular market-analysis tools into repeatable workflows.

## Available skill

### `tradingsignal-macro-opportunity`

Scans crypto, FX, commodities, and supported futures across timeframes, then returns the clearest technical opportunities with conditional entry plans, invalidation levels, targets, conflicts, and a chart for every decision-relevant reason.

The skill orchestrates individual TradingSignal MCP modules. It does not treat the all-in-one symbol analysis as the default research path, and it does not use exploratory Fibonacci results as screening evidence or a trading signal.

## Prerequisite: connect TradingSignal MCP

Codex:

```bash
codex mcp add tradingsignal --url https://tradingsignal.pro/mcp
codex mcp login tradingsignal
```

Claude Code:

```bash
claude mcp add --scope user --transport http tradingsignal https://tradingsignal.pro/mcp
```

Complete the login flow before using a skill. TradingSignal's setup page is available at <https://tradingsignal.pro/connect>.

## Install in Codex

Paste this into Codex:

```text
$skill-installer Install https://github.com/CrossSpace-HK/tradingsignal-skills/tree/main/skills/tradingsignal-macro-opportunity
```

The skill becomes available on the next turn after installation.

For a manual installation, copy the whole skill directory to:

```text
~/.codex/skills/tradingsignal-macro-opportunity/
```

## Install in Claude Code

Copy the whole skill directory to:

```text
~/.claude/skills/tradingsignal-macro-opportunity/
```

The required entrypoint is `SKILL.md`. Restart or open a new session after installation.

## Try it

```text
$tradingsignal-macro-opportunity Scan crypto, FX, and commodities for today's three clearest multi-timeframe technical opportunities. Lead with the action, then give entry conditions, invalidation, targets, conflicts, and a chart link for every reason. Do not use Fibonacci as strong-resonance evidence.
```

Expected actions are `ENTER_ON_PULLBACK`, `ENTER_ON_BREAKOUT`, `WATCH`, `REDUCE_OR_EXIT`, or `AVOID`. An entry action is not allowed without a concrete invalidation level. Position sizing requires an explicit portfolio risk budget.

## License

MIT
