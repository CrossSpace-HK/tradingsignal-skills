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

`get_indicators` also returns `chart`: the decisive readings drawn on the
price, so the reader can see *where* each one is saying it. **This is the
lead image of the analysis** -- it belongs above every method chart, because
it is the picture of the conclusion rather than of one method's internals.
Pass your own one-line view as `conclusion` and it is printed on the image.
The chart narrows with the list: filter by `categories` or `side` and the
image shows the same subset, so it can never claim more than the text.
It is drawn on the last closed bar and reports its own `barTs`; if that
differs from the readings' `barTs`, the latest bar is still forming -- say
which one you mean rather than letting the two pass as the same.

**Leave Wyckoff out when it has no clear reading.** The engine states its own
limit: the side is decided only by the direction of the leg before the range,
and it cannot separate distribution from re-accumulation in an uptrend; a range
with `tr.quality < 0.5` is not tradeable. Writing the paragraph anyway presents
a default as a judgement. Omitting it costs the analysis nothing.

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
