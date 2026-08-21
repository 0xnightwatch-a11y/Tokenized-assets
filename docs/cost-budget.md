# Cost & Budget

Target: near-zero ongoing cost. Do not add a paid dependency without
checking it against this doc and flagging it explicitly.

## Ongoing monthly cost (after GCP free-trial credits expire)

| Component | Cost | Notes |
|---|---|---|
| GCP VM (e2-micro) | $0 | Always Free, us-west1/us-central1/us-east1 only |
| Static IP, disk, egress | $0 | Within Always Free limits at this app's data volume |
| GeckoTerminal API | $0 | Free tier, 10 calls/min |
| Alpaca Market Data (free plan) | $0 | Real-time IEX feed, 200 req/min |
| Dinari API | $0 | Free for market-data access |
| xStocks API | $0 | Free for integrator/public-data access |
| Domain | ~$1-3/mo | Only real recurring cost |
| **Total** | **~$1-3/mo** | |

## During the GCP free-trial period

Use e2-small (2 GB RAM, ~$12-14/mo list) instead of e2-micro for a
more comfortable development experience — this is covered by the
$300 / 90-day trial credit. **Set a calendar reminder for the credit
expiry date** and resize down to e2-micro before it lapses into
billing.

## Explicit non-goals for v1 spend

Do not adopt any of these without a specific, observed problem the
free tier can't solve:

- Polygon/Massive.com Stocks Advanced ($199/mo) — only if Alpaca's IEX
  feed produces observably wrong market-open/closed flags or missing
  ticks on tracked names.
- CoinGecko API Basic ($35/mo) — only if GeckoTerminal's 10 calls/min
  becomes an actual bottleneck given real poll frequency × tracked
  pool count.
- Dune Plus/Premium ($390-1990/mo) — not needed for 6-7 tickers; skip
  entirely for v1.
- Any managed Postgres/BaaS (Supabase, etc.) — self-hosting in Docker
  on the VM replaces this.
- Render/Railway hosting — replaced by the self-hosted GCP VM.
