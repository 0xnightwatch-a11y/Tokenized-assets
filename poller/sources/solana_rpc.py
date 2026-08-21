import logging

import requests

import config

log = logging.getLogger(__name__)


class SolanaRpcError(Exception):
    pass


def get_scaled_ui_multiplier(mint_address: str) -> float:
    """Read the current rebasing multiplier directly off a Token-2022 mint's
    Scaled UI Amount extension via a public Solana RPC -- no API key or
    partner access needed. This is the on-chain source of truth xStocks'
    own REST API would otherwise just re-serve.
    """
    resp = requests.post(
        config.SOLANA_RPC_URL,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [mint_address, {"encoding": "jsonParsed"}],
        },
        timeout=10,
    )
    resp.raise_for_status()
    body = resp.json()

    if "error" in body:
        raise SolanaRpcError(f"RPC error for mint {mint_address}: {body['error']}")

    value = body.get("result", {}).get("value")
    if value is None:
        raise SolanaRpcError(f"mint account not found: {mint_address}")

    try:
        extensions = value["data"]["parsed"]["info"]["extensions"]
    except (KeyError, TypeError):
        raise SolanaRpcError(f"mint {mint_address} is not a parsed Token-2022 mint")

    for ext in extensions:
        if ext.get("extension") == "scaledUiAmountConfig":
            return float(ext["state"]["multiplier"])

    raise SolanaRpcError(f"mint {mint_address} has no scaledUiAmountConfig extension")
