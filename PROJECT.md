# Tokenized Equity Spread Dashboard — Build Spec

Read this file first. Supporting detail lives in /docs — read the relevant
doc before starting work on that area.

## What this is

A cross-issuer, cross-chain spread/liquidity monitoring product for
tokenized equities. The same underlying stock (e.g. NVDA) trades as
multiple, legally distinct token wrappers across different issuers and
chains. This product tracks those wrappers, computes normalized
cross-wrapper spreads, and surfaces them via a free daily fixing page
and a paid live screener + alerts.

This is explicitly a **data/monitoring product, not a trading bot**.
It does not execute trades, hold funds, or manage user custody. It
reads public/free-tier data and republishes derived analytics.

## Who it's for (in priority order)

1. Market makers / prop desks / RWA-native funds with issuer redemption
access — the only parties who can actually close cross-wrapper
spreads. This is the paid-tier buyer.
2. Public free daily fixing page — marketing/credibility surface, not
the revenue driver.

## Stage 1 scope (build this first — see docs/stage1-plan.md for full detail)

**Tickers:** NVDA, AAPL, TSLA, MSFT, SPY, QQQ, plus SPCX (SpaceX) if
time allows.

**Wrappers/chains to track in v1** (see docs/data-sources.md for full
ticker/wrapper/chain map and API details):

* Dinari dShares — Arbitrum (primary), Ethereum, Base
* Backed/xStocks — Solana
* Ondo Global Markets — Ethereum, Solana (Jupiter)

Explicitly OUT of v1 scope: Robinhood Chain, Binance bStocks, Bitget
rTokens, Gate gStocks, CEX order-book depth. Add these in a later
stage once the spine works.

## Non-negotiable technical requirement: rebasing normalization

xStocks and Ondo tokens rebase supply for dividends (adjust via a
multiplier field rather than paying cash dividends). **Never compare
raw exchange quotes across wrappers.** Every price must be converted
to NAV-accrual terms using each issuer's current multiplier before any
spread is computed. Getting this wrong produces confidently-wrong
numbers on a page real market makers will look at — treat this as the
first thing to get right, not a later polish pass.

Also tag every computed spread with an "is this closeable" flag: if
one wrapper is US-accessible and the other is non-US-only (e.g. Dinari
vs xStocks), that spread is NOT executable arbitrage — it's
jurisdictional segmentation. Label it as such rather than implying it's
tradeable.

## Architecture (see docs/architecture.md for full detail)

Single Docker Compose stack on one GCP VM:

* `postgres` — time-series price/spread data, self-hosted (no managed DB)
* `poller` — scheduled job (\~1-5 min cadence) pulling from data sources,
normalizing, writing to Postgres
* `api` — spread engine + web/API surface, reads from Postgres
* `caddy` — reverse proxy + automatic HTTPS

## Data sources (see docs/data-sources.md for endpoints/keys/limits)

All free-tier for v1: GeckoTerminal public API (on-chain pool prices),
Alpaca free plan (underlying equity reference price, real-time IEX
feed), Dinari public API (NAV/reference data), xStocks public API
(asset metadata + multiplier values).

## Budget constraint

Solo operator. Target ongoing cost after initial free-credit period:
\~$1-3/mo (domain only) — see docs/cost-budget.md. Do not introduce a
paid dependency without flagging it and checking it against this
budget first.

## Working style

* Build one ticker (NVDA) fully end-to-end — ingestion, normalization,
spread calc, display — before adding the rest. Validate the
normalization logic on one name before scaling to six.
* Each service (poller, api) should run and be testable independently
via `docker compose up <service>` before wiring them together.
* Prefer boring, correct, and cheap over clever. This is a v1 meant to
validate demand, not a finished platform.

## Stage 1 success/kill criteria

* **Continue to Stage 2** if 2-3 real market-making/prop desks engage
with the paid tier (or firm verbal commitment) within 12 weeks of
the free page going live, and off-hours spread data shows genuinely
surprising patterns to the people shown it.
* **Pivot** if the free page gets traffic but nobody with issuer
redemption access engages — signals a retail-education audience
instead of the professional buyer the thesis depends on.
* **Kill/rethink** if the normalization/rebasing logic proves unreliable
given free-tier data quality (sparse pools, unstable issuer APIs) —
better to learn this in month 1 than after selling a subscription.

