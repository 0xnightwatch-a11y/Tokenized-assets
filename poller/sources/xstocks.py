import logging

import requests

import config

log = logging.getLogger(__name__)


class XStocksError(Exception):
    pass


def get_multiplier(symbol: str) -> float:
    """Current rebasing/dividend-accrual multiplier for an xStocks asset.

    NOTE: the exact endpoint shape is UNVERIFIED. docs.xstocks.fi is behind
    Cloudflare bot-protection and the public swagger UI at api.xstocks.fi
    isn't wired to a real spec (both checked 2026-08-20), so this could not
    be confirmed against a live response without an API key. Once you have
    XSTOCKS_API_KEY, hit this once by hand and adjust
    XSTOCKS_ASSET_PATH_TEMPLATE / the field lookups below to match the real
    response shape before trusting this in production.
    """
    if not config.XSTOCKS_API_KEY:
        raise XStocksError("XSTOCKS_API_KEY not configured")

    url = config.XSTOCKS_API_BASE + config.XSTOCKS_ASSET_PATH_TEMPLATE.format(symbol=symbol)
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {config.XSTOCKS_API_KEY}"},
        timeout=10,
    )
    resp.raise_for_status()
    body = resp.json()

    multiplier = _find_multiplier(body)
    if multiplier is None:
        raise XStocksError(f"could not locate a multiplier field in response: {body}")
    return float(multiplier)


def _find_multiplier(body: dict):
    if "multiplier" in body:
        return body["multiplier"]
    for deployment in body.get("deployments", []):
        if "multiplier" in deployment:
            return deployment["multiplier"]
    pricing = body.get("pricing", {})
    if "multiplier" in pricing:
        return pricing["multiplier"]
    return None
