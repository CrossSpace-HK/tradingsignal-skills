# Technical Report Template

Use this template when writing a technical report on one named instrument. Read the chosen Skill version (including this template and `references/output-contract.md`) before authoring or reviewing a report, and cite evidence IDs issued in the current turn. Fill every section; never invent a fact the evidence does not supply.

## 1. Conclusion

Lead with the decision in one sentence: what to do, or that there is nothing to do.

- State the call: an actionable setup, `WATCH`, or `AVOID`.
- Name the symbol, market and timeframe the call applies to.
- Say in one clause what carries it: trend strength score and direction, resonance count, and the decisive readings ranked by notability.
- Never invent win rates, confidence intervals or probabilities of success. Discuss account percentages, position size or risk budgets only when the user supplied their portfolio size and risk budget.

## 2. Data Cutoff

Record exactly what the analysis saw, so a later reader can reproduce it.

- Symbol as the market quotes it, market, and the timeframe(s) used, with the higher timeframe setting the backdrop and the lower timeframe refining entries.
- `dataAsOf` for each timeframe cited, with timezone, from that timeframe's `freshness`; name any timeframe whose `stale` flag is set instead of using it silently.
- Each reading's `barDate` quoted as returned; where the last closed bar and the forming bar differ, say which bar the sentence means.
- Analysis timestamp, the Skill version, and the exact host-issued evidence IDs this report cites.
- Any `notApplicable` or not-computable field kept explicit and distinct from neutral and from "no signal".

## 3. Matching Charts

Every decision-relevant reason carries the chart that shows it, placed immediately after the sentence it backs.

| Section | Chart | What it shows |
| --- | --- | --- |
| Signals | `chart` from `get_indicators` | The readings taking a side; the moving-average, MACD and RSI panels are pinned, so name the decisive ones explicitly |
| Signals | `trendChart` from `get_indicators` | The composite strength score and its sections; never narrowed by a category filter |
| Entry, Exit, Where it is, Risk | The method chart behind the claim | Only methods whose engine has something to say |

- Use the symbol and timeframe the report is about, and link charts as named links, not naked URLs or embeds.
- Use each chart's signed URL exactly as returned, unedited; offer `openIn` when the reader wants the live analysis at the same bar.
- Drop the row for any method whose engine returns its nothing-to-say marker: no paragraph, no chart, and no sentence saying it was omitted.
- On risk, read `riskReward` whole (distance both ways in percent and price, `strength`, `levelsWithin`) and take every price from `drawnLevels`; a large ratio with `atLevel` usually means price is resting on support, not a generous trade.

## 4. Trigger and Invalidation Conditions

Make the plan falsifiable. No entry condition without a concrete invalidation.

- **Trigger** - the price or the condition that would start the idea, stated as a level or a measurable event, not a mood.
- **Invalidation** - the exact price or event that ends the idea, and what it would prove.
- **Targets** - the levels above, from the same evidence, with the room that remains.
- **Context** - trend strength against its no-trend threshold, VCP stage or position in the Chan structure, and which independent methods agree or disagree.
- If nothing qualifies, say so plainly and stop; never manufacture a trigger to fill the section.

## 5. Post-Mortem Review

Used only when reviewing a saved report against later evidence; leave it empty at authoring time rather than predicting the outcome.

- Read the exact saved report version first, then obtain dated follow-up evidence and cite its IDs.
- Separate outcome from reasoning: did the condition occur, and was the reasoning sound at the time it was written, whichever way price went?
- Compare each original trigger and invalidation with the follow-up evidence and record it as met, not met, or still open.
- Name what the evidence did not test, and mark the verdict as a qualitative author assessment, never a measured win rate.
- Propose concrete improvements to the Skill, this template, or the specific references the report relied on, phrased as editable text for a human to review.
