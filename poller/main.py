import logging
import time
from datetime import datetime, timezone

import config
import db
import normalize
from sources import alpaca, geckoterminal, solana_rpc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("poller")


def fetch_underlying_prices(conn) -> dict:
    """One Alpaca call per ticker per cycle. Returns {ticker: price_usd}."""
    prices = {}
    for ticker in config.TICKERS:
        try:
            trade = alpaca.get_latest_trade(ticker)
        except alpaca.AlpacaError as e:
            log.warning("alpaca: skipping %s (%s)", ticker, e)
            continue
        except Exception:
            log.exception("alpaca: failed to fetch %s", ticker)
            continue

        quote_time = datetime.fromisoformat(trade["quote_time"].replace("Z", "+00:00"))
        db.insert_underlying_price(
            conn,
            {
                "ticker": ticker,
                "price_usd": trade["price_usd"],
                "source": "alpaca",
                "quote_time": quote_time,
            },
        )
        prices[ticker] = trade["price_usd"]
        log.info("alpaca: %s underlying = $%s", ticker, trade["price_usd"])
    return prices


def get_multiplier(instrument: dict):
    """Returns (multiplier, source). Dinari dShares are 1:1, not rebasing --
    only xStocks needs a live multiplier lookup."""
    if instrument["wrapper"] != config.Wrapper.XSTOCKS:
        return 1, "not_applicable"

    try:
        m = solana_rpc.get_scaled_ui_multiplier(instrument["mint_address"])
        return m, "solana_onchain"
    except solana_rpc.SolanaRpcError as e:
        log.warning(
            "solana_rpc: multiplier lookup failed for %s (%s) -- falling back to 1.0",
            instrument["mint_address"],
            e,
        )
        return 1, "fallback_default"
    except Exception:
        log.exception("solana_rpc: unexpected error fetching multiplier for %s", instrument["mint_address"])
        return 1, "fallback_default"


def poll_instrument(conn, instrument: dict, underlying_prices: dict):
    ticker = instrument["ticker"]
    wrapper = instrument["wrapper"]
    chain = instrument["chain"]

    try:
        pool = geckoterminal.get_pool_price(chain, instrument["pool_address"])
    except geckoterminal.GeckoTerminalError as e:
        log.warning("geckoterminal: skipping %s/%s (%s)", ticker, wrapper, e)
        return
    except Exception:
        log.exception("geckoterminal: failed to fetch %s/%s", ticker, wrapper)
        return

    db.insert_raw_pool_snapshot(
        conn,
        {
            "ticker": ticker,
            "wrapper": wrapper,
            "chain": chain,
            "pool_address": instrument["pool_address"],
            "dex": pool["dex"],
            "raw_price_usd": pool["raw_price_usd"],
            "reserve_usd": pool["reserve_usd"],
        },
    )

    multiplier, multiplier_source = get_multiplier(instrument)
    db.insert_multiplier(
        conn,
        {"ticker": ticker, "wrapper": wrapper, "multiplier": multiplier, "source": multiplier_source},
    )

    normalized_price = normalize.apply_multiplier(pool["raw_price_usd"], multiplier)

    underlying_price = underlying_prices.get(ticker)
    dev_bps = (
        normalize.deviation_bps(normalized_price, underlying_price)
        if underlying_price is not None
        else None
    )

    db.insert_normalized_price(
        conn,
        {
            "ticker": ticker,
            "wrapper": wrapper,
            "chain": chain,
            "raw_price_usd": pool["raw_price_usd"],
            "multiplier": multiplier,
            "multiplier_source": multiplier_source,
            "normalized_price_usd": normalized_price,
            "underlying_price_usd": underlying_price,
            "deviation_bps": dev_bps,
        },
    )

    log.info(
        "%s/%s: raw=$%s multiplier=%s (%s) -> normalized=$%s underlying=$%s dev=%sbps",
        ticker, wrapper, pool["raw_price_usd"], multiplier, multiplier_source,
        normalized_price, underlying_price, dev_bps,
    )


def run_once(conn):
    started = datetime.now(timezone.utc)
    log.info("poll cycle starting at %s", started.isoformat())

    underlying_prices = fetch_underlying_prices(conn)

    for instrument in config.INSTRUMENTS:
        if not instrument["enabled"]:
            continue
        poll_instrument(conn, instrument, underlying_prices)

    log.info("poll cycle done in %.1fs", (datetime.now(timezone.utc) - started).total_seconds())


def main():
    conn = db.connect()
    db.init_schema(conn)

    log.info(
        "poller started: interval=%ss tickers=%s enabled_instruments=%s",
        config.POLL_INTERVAL_SECONDS,
        config.TICKERS,
        [f"{i['ticker']}/{i['wrapper']}" for i in config.INSTRUMENTS if i["enabled"]],
    )

    while True:
        try:
            run_once(conn)
        except Exception:
            log.exception("poll cycle failed")
        time.sleep(config.POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
