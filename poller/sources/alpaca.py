import logging

import requests

import config

log = logging.getLogger(__name__)

ALPACA_DATA_BASE = "https://data.alpaca.markets"


class AlpacaError(Exception):
    pass


def get_latest_trade(ticker: str) -> dict:
    """Latest IEX trade price for the underlying equity (Alpaca free plan)."""
    if not config.ALPACA_API_KEY_ID or not config.ALPACA_API_SECRET_KEY:
        raise AlpacaError("ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY not configured")

    url = f"{ALPACA_DATA_BASE}/v2/stocks/{ticker}/trades/latest"
    resp = requests.get(
        url,
        params={"feed": "iex"},
        headers={
            "APCA-API-KEY-ID": config.ALPACA_API_KEY_ID,
            "APCA-API-SECRET-KEY": config.ALPACA_API_SECRET_KEY,
        },
        timeout=10,
    )
    resp.raise_for_status()
    trade = resp.json()["trade"]
    return {"price_usd": trade["p"], "quote_time": trade["t"]}
