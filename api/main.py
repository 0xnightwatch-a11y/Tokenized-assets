import logging
from collections import defaultdict

from fastapi import FastAPI, HTTPException

import config
import db
import spread_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("api")

app = FastAPI(title="Tokenized Equity Spread API")


@app.get("/health")
def health():
    try:
        conn = db.connect()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"database unavailable: {e}")


@app.get("/quotes")
def quotes(ticker: str | None = None):
    """Latest normalized price per (ticker, wrapper), the raw material
    spreads are computed from. Useful on its own for a single-wrapper
    ticker where there's nothing to spread against yet.
    """
    conn = db.connect()
    try:
        return db.latest_normalized_prices(conn, ticker)
    finally:
        conn.close()


@app.get("/spreads")
def spreads(ticker: str | None = None):
    """Cross-wrapper spread in bps per ticker, tagged closeable vs
    wrapper-basis (see docs/redemption-gating.md), with a rough executable-
    depth estimate at $1k/$10k/$50k. Tickers with only one live wrapper
    quote produce no rows -- there's nothing to spread against yet.
    """
    conn = db.connect()
    try:
        rows = db.latest_normalized_prices(conn, ticker)

        by_ticker = defaultdict(list)
        for row in rows:
            by_ticker[row["ticker"]].append(row)

        results = []
        for tkr, quotes_for_ticker in by_ticker.items():
            if len(quotes_for_ticker) < 2:
                continue
            reserves = {
                q["wrapper"]: db.latest_pool_reserve(conn, tkr, q["wrapper"], q["chain"])
                for q in quotes_for_ticker
            }
            results.extend(spread_engine.compute_ticker_spreads(tkr, quotes_for_ticker, reserves))
        return results
    finally:
        conn.close()
