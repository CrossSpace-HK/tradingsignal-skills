---
name: setup
description: Connect and authorize the TradingSignal MCP bundled with this plugin after installation or when TradingSignal tools are unavailable.
---

# Set up TradingSignal

1. Run `/reload-plugins` if the installation summary says the plugin is not active yet.
2. Open `/mcp`, select the `tradingsignal` server supplied by this plugin, and choose **Authenticate**.
3. Complete the TradingSignal OAuth flow in the browser.
4. Return to Claude Code and verify that the server is connected.
5. Ask Claude to use TradingSignal for a market scan or symbol analysis.

Do not ask the user to add a second standalone TradingSignal MCP entry. The plugin already supplies it.
