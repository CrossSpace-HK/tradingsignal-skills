# No-Valid-Opportunity Review

Use this workflow when the user prioritizes avoiding weak trades, asks whether any setup is executable, or presents materially conflicting evidence.

## Rejection gates

Reject or downgrade a candidate when any of these is decision-critical:

- stale or incomplete data;
- unsupported market, symbol, or timeframe coverage;
- material conflict between higher-timeframe regime and the proposed trigger;
- only one oscillator or one evidence family supports the thesis;
- missing or ambiguous invalidation;
- inadequate risk/reward to the next defensible level;
- a missing chart prevents visual audit of a key reason;
- a required input is `notApplicable` or not computable.

## Output

Start with a direct answer: either executable opportunities exist or “no valid trade qualifies today.” Never fill a requested count with weak setups.

When nothing qualifies, return the closest rejected candidates with:

- current action (`WATCH` or `AVOID`);
- the decisive rejection reason;
- remaining conflicts and coverage gaps;
- the exact price, structural event, fresh bar, or data condition that would upgrade the candidate;
- the chart attached to every reason that can be visually audited.
