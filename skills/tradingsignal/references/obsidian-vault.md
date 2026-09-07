[English](obsidian-vault.md) | [中文](obsidian-vault.zh-CN.md)

# Recording an Analysis to Obsidian

Use this workflow when the user asks to save an analysis for later review, or to review what they concluded before. It is **opt-in**: without it, nothing is ever written to disk.

## Ask before writing anything

1. Ask once, at the end of an analysis, whether to record it to Obsidian. Do not ask again in the same conversation after a "no".
2. If yes, ask for the **vault path**. Never guess one, never write into a vault the user has not named, and never create a vault inside another vault's root — a nested vault is indexed twice and the two sets of notes bleed into each other.
3. Check the path exists and holds `分析/`, `标的/` and `附件/`. If it does not, list what you would create and ask before creating it.
4. Write only inside `分析/`, `标的/` and `附件/`. Nothing outside those three, ever.

The user must repeat the path in a new conversation unless they have stored it themselves; say so rather than inventing a remembered path.

## Two layers, because one cannot answer both questions

- `标的/<SYMBOL>.md` — one living note per instrument: what the user thinks **now**, and the levels that still matter. Rewritten as the view changes.
- `分析/<date>-<SYMBOL>-<timeframe>-<id>.md` — one note per analysis: what was thought **that day**. Written once and not edited afterwards, except to fill in the review section.

A single layer loses one of "what do I think now" and "what did I think then". Review needs both.

## What goes in the front matter

Machine-readable fields carry the review queries, so they must be facts, not prose:

```yaml
analysis_id, symbol, asset_class, market, timeframe
as_of          # the last CLOSED bar the analysis is about
date           # when the note was written
provider, route, data_digest    # which data this rests on
methods, bias, confidence, key_levels, invalidation
outcome        # left null; filled at review time
image_archived, image_sha256
data_staleness_days             # as_of vs today, when the series lags
```

Distinguish "not computable" from neutral here as strictly as in the chat answer. A null is honest; a zero is a claim.

## Tags are a controlled vocabulary

Read the vault's own `标签.md` and use only the tags it lists. Free-form tags are worthless a year later, because the same idea gets five spellings and no query returns a complete set.

- **Fact tags** (market, region, data source) are derived by you from the instrument, never typed by hand — a derived tag cannot be missing or misspelled.
- **Judgement tags** (direction, method, outcome) come from the analysis, and `结果/*` only at review time.
- Keep the two kinds separate. "All US equities" is a fact; "all the ones I was long" is a judgement, and mixing them in one namespace makes both unfilterable.

If the analysis needs a tag the vocabulary lacks, propose adding it to `标签.md` rather than inventing one in a note.

## Charts

Archive the chart the analysis actually rests on, using the product's own screenshot action from a logged-in browser. Save it as `附件/<analysis_id>-<slot>.png`, embed it with `![[附件/...]]`, and record its SHA-256.

**Do not archive a chart that shows something the note does not claim.** If the live chart draws a bar later than the note's `as_of` — a forming bar, or a series that has refreshed since — the image contradicts the note in the one position that claims to be its evidence. Say so and leave the image unarchived.

Be exact about what an image proves. A screenshot proves the symbol and timeframe only if the picture itself is titled with them. It does not prove its own date; that comes from `data_digest`, from the store holding no later bar at archive time, and from the filename matching `analysis_id`. State that chain rather than letting the PNG stand in for it.

## Links

- `liveUrl` — a shareable link to the chart. It opens **today's** data, not the day the analysis was written. Label it that way. Never describe it as returning to that day's chart.
- `snapshotUrl` — a link that replays the day. Write "暂无" until the product actually has one.

## Review

To review, read the vault rather than re-deriving from memory:

1. Query `分析/` by tag and front matter for the question asked ("everything I was long that has not played out", "every Fibonacci call that reached 0.618").
2. For each hit, fetch what the instrument did **after** `as_of`, and compare it against the note's own `invalidation` — not against a target chosen afterwards.
3. Fill `outcome` and the review section of that note, and add the `结果/*` tag. Leave the original conclusion and reasoning untouched: a record edited to match the outcome cannot be reviewed again.
4. Report the pattern across notes, not just the last one, and say plainly when the sample is too small to support one.
