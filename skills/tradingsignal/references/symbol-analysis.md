[English](symbol-analysis.md) | [中文](symbol-analysis.zh-CN.md)

# Single-Symbol Analysis

Use this workflow when the user names a symbol, timeframe, or technical method and wants an explanation rather than a broad scan.

## Scope the question

Call `describe_capabilities` when support is uncertain. Identify the requested holding horizon and assign explicit roles to each timeframe. If the user asks only about one method, do not call unrelated engines merely to create confluence.

Use `analyze_symbol` only when the user explicitly wants a quick overview. For research, call granular modules independently:

- `get_method_analysis(engine="vcp")`: stage, trend template, contraction quality, pivot, and stop;
- `get_method_analysis(engine="chan")`: strokes, centers, structural points, confirmation, and invalidation;
- `get_method_analysis(engine="wyckoff")`: range quality, phase, events, entry, stop, and target;
- `get_method_analysis(engine="td9")`: setup/countdown maturity, TDST, risk level, and required next-bar confirmation;
- `get_levels`: support, resistance, clusters, and distance from current price;
- `get_candles` or `run_engine`: raw or advanced evidence only when needed.

**Researching one symbol, trend strength and indicator resonance are required,
not optional.** Take them from `get_indicators`: it reports, per category
(trend, momentum, volatility, volume, patterns, support/resistance), how many
indicators are bullish and bearish, **which ones are taking a side and the
reason each gives**. `side: "decisive"` keeps only those actually taking one,
which is usually the real question -- not "what does everything say" but
"which of them is saying anything right now".

`get_indicators` also returns TWO pictures, and both lead the analysis, above
every method chart -- they show the conclusion, a method chart shows one
method's internals. `chart` is the main technical picture: 均线 / MACD / RSI
always drawn, plus up to three more chosen by `notability`, six in all.
`trendChart` is the composite trend strength, signed by direction, with the
no-trend band drawn. Pass your own one-line view as `conclusion` and it is
printed on both.

The main chart narrows with the list -- filter by `categories` or `side` and
it shows the same subset, so it can never claim more than the text. The trend
chart does not narrow: the strength is a composition over every contributor,
and a filtered one would not be that number.

Both are drawn on the last closed bar and report their own `barTs`; if that
differs from the readings' `barTs`, the latest bar is still forming -- say
which one you mean rather than letting the two pass as the same.

**Rank the readings by `notability`, and never let a pinned chart line pass
for agreement.** Every reading carries `notability` (0-100) and
`barsSinceFlip`: recency of the last change of mind, combined with how rarely
that indicator takes this side at all. `notable` lists what was drawn, marks
the pinned three `core: true`, and gives a `why` for the rest. 均线, MACD and
RSI appear on the chart whatever they read, so state which readings are
actually decisive.

**Leave a method out when it has no clear reading -- every method, not just
Wyckoff.** Writing the paragraph anyway presents a default as a judgement, and
the reader cannot tell which one they are holding. Do not write the omission
either: "Chan has no clear conclusion" is a sentence shaped like a finding.
Say it only if the user asked about that method directly, and then in one
clause with the reason.

Each engine declares its own version of nothing-to-say: Wyckoff cannot
separate distribution from re-accumulation in an uptrend and calls
`tr.quality < 0.5` untradeable; VCP's `nearMissReason` means no pattern was
found, and `unavailable` means the score came from fewer factors; a Chan 笔
with `sureness: "MAYBE"` is unconfirmed and a borderline divergence `ratio` is
a cutoff, not a finding; a TD9 count still in progress is a maturity, not a
direction; the Fibonacci rhythm layer is exploratory and may not be counted as
strong resonance evidence. See `references/obsidian-vault.md` for the same
list in full.

Do not treat the combined overview or two outputs from one engine as independent evidence. Preserve every caveat and distinguish unavailable computation from a neutral reading.

## Explain the result

**State the view in the first sentence** (buy / sell / neutral), **and follow
it immediately with one line of trend strength and resonance** -- those are the
fastest answers to "why this view", and they do not belong at the end. Then,
still before any method detail, **name the bullish and bearish signals that
matter and show the signals chart**: the reader should meet the picture and
the handful of readings drawn on it before reading a word about Chan or
Wyckoff. Anything visible in that image is the part of the analysis that gets
read; burying it under method paragraphs wastes it. Then explain:

1. where the higher timeframes stand;
2. the current structure, and what has just triggered;
3. nearest support, resistance, and invalidation candidates;
4. agreement and conflicts across independent methods;
5. what the next bar or price event must do to confirm or reject the reading.

Attach each method's own same-symbol, same-timeframe chart immediately after the reason it supports -- after the signals chart, which leads. If the method cannot be confirmed visually, say so and do not elevate the conclusion beyond `WATCH`.
