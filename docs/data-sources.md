# Data Sources

## Ticker / wrapper / chain map (v1)

| Underlying | Dinari (dShares) | Backed / xStocks | Ondo Global Markets |
|---|---|---|---|
| Apple | dAAPL — Arbitrum/Ethereum/Base | AAPLx — Solana | AAPLon — Ethereum/Solana |
| Tesla | dTSLA | TSLAx | TSLAon |
| Nvidia | dNVDA | NVDAx | NVDAon |
| Microsoft | dMSFT | MSFTx | — |
| S&P 500 | dSPY | SPYx | SPYon |
| Nasdaq 100 | — | QQQx | QQQon |
| SpaceX (stretch) | — | (via xStocks) | (via Ondo) — also Backpack SPCX |

Each of these is a legally distinct instrument, not the same token on
different rails. Do not treat "dAAPL vs AAPLx" as literally the same
asset — see docs/redemption-gating.md for what each actually
represents legally.

## API details

### GeckoTerminal public API
- On-chain DEX pool data (price, liquidity, volume) for Solana
  (Raydium/Orca — xStocks, Ondo) and Arbitrum/Ethereum (Uniswap —
  Dinari, Ondo).
- Free tier: 10 calls/min, no key required. Sufficient for v1's 6-7
  tickers polled every 1-5 min.
- Upgrade path if rate-limited: CoinGecko API Basic plan ($35/mo)
  raises limits and unlocks the same data via /onchain endpoints.
- Docs: https://apiguide.geckoterminal.com/

### Alpaca Market Data API (free plan)
- Underlying equity reference price (last trade), real-time IEX feed,
  200 requests/min.
- IEX is a partial view of consolidated volume (~2-5%) but sufficient
  for last-price comparison, which is all the spread engine needs.
- Upgrade path if data quality issues appear: Polygon/Massive.com
  Stocks Advanced ($199/mo) for full SIP tape — do not pre-pay this,
  only upgrade on a concrete observed problem.
- Docs: https://docs.alpaca.markets/us/docs/about-market-data-api

### Dinari API
- SDK: `@dinari/api-sdk` (npm). Provides NAV/reference data for
  dShares. Free to register for market-data access.
- Production/institutional-tier pricing beyond public market data is
  not publicly listed — confirm directly if heavier usage is needed
  later.
- Docs: https://dinari.com/

### xStocks API
- Two audiences: "Integrators" (public asset info, market prices,
  multiplier values — what we need) and "Clients" (onboarded issuer
  accounts, not needed for v1).
- Auth via API key (Settings → API on the xStocks platform). Free for
  integrator/public-data access.
- **The multiplier/asset-info endpoint is required reading before
  building the normalization layer** — this is where the
  rebasing-adjustment factor comes from.
- Docs: https://docs.xstocks.fi/developers

## What's explicitly out of scope for v1 (revisit in Stage 2)

- Robinhood Chain (Uniswap v3/v4 on Robinhood's Arbitrum Orbit L2) —
  needs separate indexing, high overlap with tickers already covered.
- Binance bStocks, Bitget rTokens, Gate gStocks — CEX order-book
  access adds integration time; add once the free-tier spine is proven.
- Any paid data tier (Polygon SIP, CoinGecko paid, Dune) — only adopt
  on a specific, observed limitation of the free tier, not
  preemptively.
