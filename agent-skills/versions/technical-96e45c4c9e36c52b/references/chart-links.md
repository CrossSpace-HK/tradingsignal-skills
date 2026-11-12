[English](chart-links.md) | [中文](chart-links.zh-CN.md)

# Attaching a chart

Read this before attaching any chart. It is the mechanics — how a link is
written, which URL is which, which preset to ask for. The rules are binding;
the reasoning behind them is in [output contract](output-contract.md).

It lives here rather than in SKILL.md because a session that never attaches a
chart should not pay for it.

- Charts are markdown links whose TEXT names symbol, timeframe and method —
  `[查看 ETH/USDT 4小时 TD9 图](url)`. Never a naked URL, never an image embed
  (`![](...)`): chat clients do not reliably fetch remote images, and the
  broken placeholder lands exactly where the evidence should be.
- **Chart URL ≠ method-page URL.** The chart is a picture; the method page is
  the live interactive analysis. Never build the method-page link yourself —
  use the `openIn` the tools return, which carries the bar and the snapshot the
  analysis ran on. A hand-built URL drops the snapshot and lands the reader on
  live prices while your sentence describes a different moment.
- Pass `conclusion` to any tool that returns a chart (`get_indicators`,
  `get_method_analysis`, `get_chart`, `get_levels`): one line, ≤80 characters,
  **your** reading, not an engine reading.
- The image captions itself and says for itself when the history behind it has
  moved. Do not paraphrase that caption as if you had checked it, and do not
  claim the chart matches the analysis's other inputs — the check covers that
  symbol's own bars at that timeframe only.
- Use the chart `get_method_analysis` returns; otherwise `get_chart` with the
  matching preset (`price`, `chan`, `td9`, `wyckoff`, `vcp`, `levels`,
  `signals`, `trend`). Say when a chart is contextual rather than the evidence
  itself.
- Every bullet gets the chart that shows what it claims. Where there is none,
  say so rather than reaching for another module's image — a picture that does
  not show the claim is worse than no picture.
- The risk bullet's chart must be the `get_levels` chart specifically, and only
  prices listed in `drawnLevels` may be cited: that field names exactly what
  the attached image contains, so anything else cannot be checked against it.
