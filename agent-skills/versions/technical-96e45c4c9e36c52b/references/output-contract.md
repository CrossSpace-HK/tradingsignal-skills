[English](output-contract.md) | [中文](output-contract.zh-CN.md)

# Why the output rules are what they are

SKILL.md carries the rules; this file carries the reasoning and the failures
each rule came from. Read it when a rule looks wrong for the case in front of
you — the rules bind either way, but a rule you understand is one you apply
correctly at the edges.

It is a separate file because the reasoning is worth about 900 tokens on every
session that never needs it.

## Charts as named links, never naked URLs or embeds

Chat clients do not reliably fetch remote images, and a broken placeholder then
sits in exactly the position that claims to be the evidence. A long signed URL
in the open is unreadable noise the user cannot tell apart from garbage. Link
text carrying symbol, timeframe and method lets the reader know what they are
opening before they click.

## Chart URL versus method-page URL

A chart URL opens a picture; a method-page URL opens the product's live,
interactive analysis for that symbol, timeframe and method. Offer the method
page when the user wants "the latest analysis", the chart when the sentence's
evidence is the picture.

Never build the method-page link by hand. Every chart the tools return carries
`openIn`, which opens the app at the same symbol, timeframe and method AND at
the same bar the analysis ran to, with the snapshot it was drawn from. A
hand-built URL loses the snapshot, so the reader lands on live prices while the
sentence beside it describes a different moment.

## `conclusion` is your reading, not the engine's

It is printed at the top of the image, so the picture states the same thing as
the prose beside it. Restating an engine's raw output there ("TD9 count is 9")
wastes the line: the number is already in the chart.

## What the image's own caption does and does not prove

The image captions itself with symbol, timeframe and the bar it is drawn to,
and it is drawn from the exact bars the analysis ran on; when the history
behind it has moved, the image says so on its own face. That check covers that
symbol's own bar series at that timeframe and nothing else — not the benchmark
VCP reads, not the multi-timeframe pool behind levels. So do not paraphrase the
caption as if you had verified it, and do not claim the chart matches the
analysis's other inputs.

## Two lead charts, and why one of them never narrows

`chart` shows the readings taking a side, where they are saying it. 均线, MACD
and RSI are pinned there by product decision, so being drawn does not mean
agreeing — that is why `notable` marks the pinned ones `core: true` and why the
prose has to name the decisive ones explicitly.

`trendChart` is a composition over every contributing indicator. Drawing it
under a `categories` filter would produce a picture that looks like a
filtered-category score and is not one, so it never narrows.

Both are drawn on the last CLOSED bar while the readings run on every bar
including one still forming. When the two `barTs` differ, that difference is
real and the analysis has to say which bar it means.

## Why `notability` rather than judgement

It combines how recently an indicator changed its mind with how rarely it takes
this side at all. A reading held for sixty bars is background; one that fired
three bars ago is news; a pattern that fires in 5% of bars outranks both. It
deliberately ignores the trend engine's per-indicator weights, which are unit
conversions rather than importance.

## Omission, and why the omission is not itself a line

A method whose engine has nothing to say returns a default, not a judgement,
and prose cannot show the reader which one they are holding. "Wyckoff and VCP
show no clear conclusion" is a sentence shaped like a finding that reports
none. Each engine's own marker for nothing-to-say is listed in
[obsidian vault](obsidian-vault.md).

## Reading `riskReward`

`levelsWithin` counts the nearest support ITSELF, so 1 means a lone line and 3
means a shelf. Describing it as levels *below* the support reads one too many.
A thick shelf is worth more than one lone line at the same price.

A large ratio usually means price is sitting on support rather than that the
trade is generous — `atLevel` is what distinguishes the two, and it is an
observation, never a verdict. Price resting on a weak level about to give way
looks identical in that field to price holding a strong one, which is why the
four conditions in SKILL.md must all hold before it is called an entry.

## Prices must come from `drawnLevels`

That field names exactly what the attached chart contains, so a price outside
it cannot be checked against the picture — and a picture that does not show
what the sentence claims is worse than no picture. `riskReward` already reports
the nearest level on each side and its bounds are guaranteed to be in
`drawnLevels`, so computing your own "nearest" is both unnecessary and
uncheckable.

## No account percentages, no probabilities

A risk budget ("risk 0.5–1% per trade") is a common convention, not something
we computed; printing one turns a measurement into unauthorised advice. A win
rate or confidence interval would be invented outright — these engines are
rule-based and there is no backtest behind them. `riskReward` measures distance
to real levels: a ratio of 2 means twice the room, never a 2-in-3 chance.
