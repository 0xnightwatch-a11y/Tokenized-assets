# Stage 1 Build Plan (0-3 months)

Goal: validate demand cheaply, not build a finished platform.

## Weeks 1-6: technical spine

1. **Ingestion layer** — three source types, different cadence:
   - On-chain DEX pools (GeckoTerminal): Solana (xStocks, Ondo),
     Arbitrum/Ethereum (Dinari, Ondo).
   - Issuer reference data: Dinari NAV/last-trade, xStocks asset
     metadata + multiplier values.
   - Underlying equity reference price: Alpaca free plan, real-time
     IEX feed.
2. **Normalization layer** (the actual moat — see PROJECT.md):
   - Per-token multiplier/adjustment factor, refreshed from each
     issuer's API.
   - NAV-accrual math applied consistently, never raw exchange quotes.
   - Market-open/closed flag per timestamp, to separate genuine
     off-hours dislocation from noise.
3. **Storage & compute**: Postgres in Docker (self-hosted on the GCP
   VM), scheduled poller job every 1-5 min. Not a real-time streaming
   pipeline — correctness over latency for v1.
4. **Spread engine**: per ticker per timestamp — cross-wrapper spread
   in bps, executable depth estimate at $1k/$10k/$50k (from pool
   reserves), closeable-vs-wrapper-basis flag (see
   docs/redemption-gating.md).

**Build order**: NVDA end-to-end first (ingestion → normalization →
spread calc → display) before adding the other 5-6 tickers. Validates
the normalization logic before scaling.

## Weeks 6-10: product surface

- **Free tier**: public daily fixing page, one table, updated once a
  day. This is a marketing/credibility asset, not the product —
  modeled on how AltStreet's daily fixing works, but covering Dinari
  and Ondo (which AltStreet does not).
- **Paid tier**: live screener (updates every few minutes) + spread/
  depth API + threshold alerts (email or Telegram/webhook, e.g.
  "AAPL cross-wrapper spread exceeded 40bps"). Anchor pricing around
  $200-500/mo per seat — this sells to a market maker's operating
  cost line, not to consumers.
- **Docs page**: state plainly what each spread does and doesn't mean
  — wrapper basis vs. executable arb, US-access gating, rebasing
  methodology. This is a trust signal for the sophisticated buyer,
  not boilerplate.

## Weeks 1-12 (parallel): distribution & demand validation

- Publish the free daily fixing page publicly starting week 6; post it
  consistently (crypto Twitter/X, relevant RWA/tokenized-equity
  Discord/Telegram communities) every day it updates.
- Direct outreach to the actual buyer segment: prop desks and
  RWA-native funds with issuer redemption access. Small, identifiable
  group — personal cold outreach with the free data attached beats ad
  spend here.
- Track funnel: free-page visitors → email signups → qualified
  conversations with someone who has real redemption access → paying
  pilots.

## Success / kill criteria

See PROJECT.md — restated here for reference:
- **Continue**: 2-3 paying pilots or firm commitments from real
  market-making/prop desks by week 12, plus off-hours spread data
  showing genuinely surprising patterns to people shown it.
- **Pivot**: free page gets traffic but no one with redemption access
  engages → retool toward retail education instead.
- **Kill/rethink**: normalization proves unreliable given free-tier
  data quality — find this out in month 1, not after selling a
  subscription.
