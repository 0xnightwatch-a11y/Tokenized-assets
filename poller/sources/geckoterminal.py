import logging

import requests

import config

log = logging.getLogger(__name__)


class GeckoTerminalError(Exception):
    pass


def get_pool_price(chain: str, pool_address: str) -> dict:
    """Fetch current price + reserve for a single on-chain pool.

    Free tier is 10 calls/min -- always hit the specific-pool endpoint
    (not /search) for repeated polling to keep well under that limit.
    """
    url = f"{config.GECKOTERMINAL_BASE}/networks/{chain}/pools/{pool_address}"
    resp = requests.get(url, timeout=10)
    if resp.status_code == 429:
        raise GeckoTerminalError("rate limited by GeckoTerminal (10 calls/min free tier)")
    resp.raise_for_status()
    attrs = resp.json()["data"]["attributes"]
    dex = resp.json()["data"]["relationships"]["dex"]["data"]["id"]
    return {
        "raw_price_usd": attrs["base_token_price_usd"],
        "reserve_usd": attrs["reserve_in_usd"],
        "dex": dex,
    }
