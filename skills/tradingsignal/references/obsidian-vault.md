[English](obsidian-vault.md) | [中文](obsidian-vault.zh-CN.md)

# Recording an Analysis to Obsidian

Use this workflow when the user asks to save an analysis for later review, or to review what they concluded before. It is **opt-in**: without it, nothing is ever written to disk.

## Ask before writing anything

1. Ask once, at the end of an analysis, whether to record it to Obsidian. Do not ask again in the same conversation after a "no".
2. If yes, ask for the **vault path**. Never guess one, never write into a vault the user has not named, and never create a vault inside another vault's root — a nested vault is indexed twice and the two sets of notes bleed into each other.
3. Check the path exists and holds `分析/`, `标的/` and `附件/`. If it does not, list what you would create and ask before creating it. Before writing into an existing vault, verify its shape still matches what you write — in particular that any Dataview column a symbol page asks for exists as a frontmatter field in the analysis template, because the drift renders as an empty column that looks exactly like "no analyses yet" (`scripts/vault_check.py` in this repository is the reference check).
4. Write only inside `分析/`, `标的/` and `附件/`. Nothing outside those three, ever.

The user must repeat the path in a new conversation unless they have stored it themselves; say so rather than inventing a remembered path.

## Two layers, because one cannot answer both questions

- `标的/<SYMBOL>.md` — one living note per instrument: what the user thinks **now**, and the levels that still matter. Rewritten as the view changes.
- `分析/<date>-<SYMBOL>-<timeframe>-<id>.md` — one note per analysis: what was thought **that day**. Written once and not edited afterwards, except to fill in the review section.

A single layer loses one of "what do I think now" and "what did I think then". Review needs both.

## The write procedure — the same every time

The first real run through a chat client drifted on four of these at once
(invented filename, invented tags, no hub page, embedded live charts), so the
procedure is numbered and none of its steps is optional or reorderable:

1. **Derive the identity.** `analysis_id` = 6 lowercase hex characters, stable
   for this analysis. Filename = `YYYY-MM-DD-<SYMBOL>-<timeframe>-<id>.md`
   where `<SYMBOL>` is the symbol with `=X` dropped and every non-alphanumeric
   removed (`BTC/USDT` → `BTCUSDT`), and `<timeframe>` is the **decision
   timeframe**. A multi-timeframe study still decides on one timeframe; that
   one goes in the name and in `timeframe`; any other timeframe the body
   leans on is declared in `context_timeframes`, which is also what permits
   a link to it. "多周期" is not a timeframe and cannot be sorted or filtered.
2. **Copy the front matter from `_模板/分析.md`** — every key, no additions,
   no renames. Values come from the vault's own vocabularies; do not invent
   field values in another language than the vocabulary uses.
3. **Tags only from `标签.md`.** If the analysis needs a tag the vocabulary
   lacks, propose the addition there — never mint one in a note.
4. **Upsert the hub page, always.** `标的/<hub>.md` where `<hub>` is the
   symbol with `=X` dropped and `/` replaced by `-`. If it does not exist,
   create it from `_模板/标的.md` with the derived fact tags. Either way, add
   a plain-Markdown link to the new analysis under `## 历史分析`, and update
   `现在的看法`, `current_bias` and `updated`. The upsert is IDEMPOTENT: a
   link that already exists is not added again, and re-saving the same
   analysis must leave the hub with one link, not two. An analysis without its hub answers "what
   did I think that day" while "what do I think now" silently has nowhere to
   live — this is the step the first real run skipped.
5. **Images: a vault note SHOWS the chart.** This surface is the opposite of
   a chat reply, and the two must not be confused. Obsidian renders local
   images, so an archived chart is EMBEDDED in the body with `![[附件/...]]`,
   at the reason it supports, with a readable text link underneath it to the
   product's latest analysis for that symbol/timeframe/method. ONE ANALYSIS
   MAY HOLD SEVERAL CHARTS -- one per method it ran -- and each sits in the
   section it belongs to: the VCP chart under the VCP reasoning, the TD9
   chart under the TD9 reasoning. Do not pool them at the end under `## 链接`;
   that section is for links, and a picture filed there is a picture nobody
   reads beside the sentence it proves. A note whose
   evidence is a bare URL is a note nobody can read at a glance -- which is
   the whole reason the vault exists.
   Archiving is REQUIRED, not an option: a save the user asked for owes at
   least one real analysis chart -- archived, hash-verified, embedded, with
   its method link directly beneath. Each image's link must match THAT
   image: the slot's method and, when the caption names a timeframe, that
   timeframe. A 4h chart may not carry a 1d link.
   The slot names the method, from a closed set -- `levels, vcp, chan, td9,
   wyckoff, fib, trend, indicators` -- and the file is `附件/<id>-<slot>.png`.
   A slot outside that set (`main`, anything new) has no implied method, so
   it must be bound explicitly with `primary_method: <tab>` in front matter;
   unbound, the save fails rather than accepting any tab at all.
   When the evidence chain genuinely cannot close -- the live chart draws a
   bar later than the note's `as_of`, or no logged-in browser is available --
   the note is still written, with the 未归档 marker and what is missing, but
   it is a DEGRADED record and must be reported as **未完整保存**. Do not
   tell the user the analysis is in Obsidian; tell them what is missing and
   what would complete it.
   Live chart URLs still go under `## 链接` as `liveUrl` lines, because they
   open TODAY's data and are not the frozen evidence.
6. **Run the postcondition and fix before finishing.** One save's artefacts
   must exist and agree: the analysis front matter, the hub page, the hub's
   link back to the analysis, and the image contract's ACTIVE arm --
   `image_archived: true` means every declared attachment exists with a
   matching SHA-256; `image_archived: false` means no attachment is owed,
   but the body must state the gap with the marker **未归档** rather than
   imply it. No section title may appear twice in one note. RUN the checker that
   ships WITH this skill -- `scripts/vault_check.py` inside the skill's own
   directory: `python3 <skill-dir>/scripts/vault_check.py <vault-path>`. Do
   not improvise a substitute check; the first Codex run did, declared PASS,
   and missed a guessed link the real checker refuses. If any part fails,
   report **"未完整保存"** and say which part -- never tell the user the
   analysis is in Obsidian when it half is.

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

**Two surfaces, opposite rules.** In a CHAT reply (Codex, Claude) an image
cannot render, so a chart travels as a named text link and never as an embed.
In an OBSIDIAN note the image renders, so the archived chart is embedded in
the body AND carries a text link beneath it. Applying the chat rule to a note
produces a wall of URLs; applying the note rule to a chat produces broken
placeholders. Decide by surface, every time.

Archive the chart the analysis actually rests on, using the product's own screenshot action from a logged-in browser. Save it as `附件/<analysis_id>-<slot>.png`, embed it with `![[附件/...]]`, and record its SHA-256.

Under every archived image, add one readable text link to the product's LATEST analysis for the same symbol, timeframe and method — `[查看 ETH/USDT 的最新 VCP 分析](...)` — so the frozen record and the living view are one click apart. This is the method-page URL, not the chart URL; its contract is LIVE and exact: `https://tradingsignal.pro/app?market=<market>&symbol=<url-encoded symbol>&timeframe=<tf>&tab=<tab>`, where `tab` is one of `indicators, levels, trend, fib, chan, td9, vcp, wyckoff` and the method decides it (VCP → `vcp`, TD/DeMark → `td9`, Chan → `chan`, Wyckoff → `wyckoff`, support/resistance → `levels`). A link missing any of market, symbol, timeframe or tab is not a deep link, it is a guess. Complete-but-wrong is worse: the checker also requires the link to open THIS note's instrument -- same symbol, same market, and the note's own decision timeframe or one it declares in `context_timeframes` -- and requires the tab to be the method the link TEXT promises and a method this analysis actually ran. A link that passes a shape check and shows the reader a different chart is the failure this exists to prevent.

**Do not archive a chart that shows something the note does not claim.** If the live chart draws a bar later than the note's `as_of` — a forming bar, or a series that has refreshed since — the image contradicts the note in the one position that claims to be its evidence. Say so and leave the image unarchived.

Be exact about what an image proves. A screenshot proves the symbol and timeframe only if the picture itself is titled with them. It does not prove its own date; that comes from `data_digest`, from the store holding no later bar at archive time, and from the filename matching `analysis_id`. State that chain rather than letting the PNG stand in for it.

## Links

- `liveUrl` — a shareable link to the chart. It opens **today's** data, not the day the analysis was written. Label it that way. Never describe it as returning to that day's chart.
- `snapshotUrl` — a link that replays the day. Write "暂无" until the product actually has one.

## Review

To review, read the vault rather than re-deriving from memory:

1. Query `分析/` by tag and front matter for the question asked ("everything I was long that has not played out", "every Fibonacci call that reached 0.618"). Keep a plain-Markdown history link on every symbol page — Dataview is an optional enhancement, and a vault without the plugin must still show its history.
2. For each hit, fetch what the instrument did **after** `as_of`, and compare it against the note's own `invalidation` — not against a target chosen afterwards.
3. Fill `outcome` and the review section of that note, and add the `结果/*` tag. Leave the original conclusion and reasoning untouched: a record edited to match the outcome cannot be reviewed again.
4. Report the pattern across notes, not just the last one, and say plainly when the sample is too small to support one.
