-- Raw on-chain pool snapshots, one row per (ticker, wrapper, chain) per poll.
CREATE TABLE IF NOT EXISTS raw_pool_snapshots (
    id              BIGSERIAL PRIMARY KEY,
    ticker          TEXT NOT NULL,
    wrapper         TEXT NOT NULL,          -- 'xstocks' | 'dinari' | 'ondo'
    chain           TEXT NOT NULL,          -- 'solana' | 'arbitrum' | ...
    pool_address    TEXT NOT NULL,
    dex             TEXT,
    raw_price_usd   NUMERIC,
    reserve_usd     NUMERIC,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_raw_pool_snapshots_lookup
    ON raw_pool_snapshots (ticker, wrapper, chain, fetched_at DESC);

-- Underlying equity reference price (Alpaca).
CREATE TABLE IF NOT EXISTS underlying_prices (
    id              BIGSERIAL PRIMARY KEY,
    ticker          TEXT NOT NULL,
    price_usd       NUMERIC NOT NULL,
    source          TEXT NOT NULL DEFAULT 'alpaca',
    quote_time      TIMESTAMPTZ,             -- exchange-reported trade timestamp
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_underlying_prices_lookup
    ON underlying_prices (ticker, fetched_at DESC);

-- Per-wrapper rebasing/dividend-accrual multiplier, as reported by the issuer.
CREATE TABLE IF NOT EXISTS multipliers (
    id              BIGSERIAL PRIMARY KEY,
    ticker          TEXT NOT NULL,
    wrapper         TEXT NOT NULL,
    multiplier      NUMERIC NOT NULL,
    source          TEXT NOT NULL,           -- 'solana_onchain' | 'fallback_default'
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_multipliers_lookup
    ON multipliers (ticker, wrapper, fetched_at DESC);

-- NAV-accrual-adjusted price per wrapper, ready for the api service's
-- cross-wrapper spread calc. This is the output of the normalization step
-- described in PROJECT.md -- never compute spreads off raw_pool_snapshots
-- directly.
CREATE TABLE IF NOT EXISTS normalized_prices (
    id                    BIGSERIAL PRIMARY KEY,
    ticker                TEXT NOT NULL,
    wrapper               TEXT NOT NULL,
    chain                 TEXT NOT NULL,
    raw_price_usd         NUMERIC,
    multiplier            NUMERIC NOT NULL,
    multiplier_source     TEXT NOT NULL,
    normalized_price_usd  NUMERIC,
    underlying_price_usd  NUMERIC,
    deviation_bps         NUMERIC,           -- (normalized - underlying) / underlying * 10000
    fetched_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_normalized_prices_lookup
    ON normalized_prices (ticker, wrapper, fetched_at DESC);
