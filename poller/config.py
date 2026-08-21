import os


def _env_int(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


DATABASE_URL = os.environ["DATABASE_URL"]
POLL_INTERVAL_SECONDS = _env_int("POLL_INTERVAL_SECONDS", 300)

ALPACA_API_KEY_ID = os.environ.get("ALPACA_API_KEY_ID", "")
ALPACA_API_SECRET_KEY = os.environ.get("ALPACA_API_SECRET_KEY", "")

# xStocks tokens use Solana's Token-2022 Scaled UI Amount extension, which
# stores the rebasing multiplier directly on the mint account. Read it via
# a public Solana RPC instead of xStocks' partner-gated REST API -- see
# sources/solana_rpc.py.
SOLANA_RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

DINARI_API_KEY_ID = os.environ.get("DINARI_API_KEY_ID", "")
DINARI_API_SECRET_KEY = os.environ.get("DINARI_API_SECRET_KEY", "")

GECKOTERMINAL_BASE = "https://api.geckoterminal.com/api/v2"


class Wrapper:
    XSTOCKS = "xstocks"
    DINARI = "dinari"


# Instrument registry: one entry per (ticker, wrapper). `enabled=False`
# entries are scaffolded but not polled yet -- fill in a verified
# pool_address (and flip enabled=True) before adding a ticker/wrapper.
#
# NVDA/xstocks pool address below was confirmed live against GeckoTerminal's
# search API on 2026-08-20 (name "NVDAx / USDC", $2.4M reserve, quote token
# = real USDC mint). NVDA/dinari has NO confirmed pool: GeckoTerminal search
# returns nothing for dNVDA on Arbitrum, consistent with Dinari's primary
# liquidity being broker-dealer mint/burn rather than an AMM pool -- see
# docs/data-sources.md. Left disabled rather than guessed.
INSTRUMENTS = [
    {
        "ticker": "NVDA",
        "wrapper": Wrapper.XSTOCKS,
        "chain": "solana",
        "xstocks_symbol": "NVDAx",
        "pool_address": "49iMatQtoyabsYAQc8GafVq6aeBFVDxSRH44oiatyyw6",
        "mint_address": "Xsc9qvGR1efVDFGLrVsmkzv3qi45LTBjeUKSPmx9qEh",
        "enabled": True,
    },
    {
        "ticker": "NVDA",
        "wrapper": Wrapper.DINARI,
        "chain": "arbitrum",
        "pool_address": None,
        "enabled": False,
    },
    {
        "ticker": "AAPL",
        "wrapper": Wrapper.XSTOCKS,
        "chain": "solana",
        "xstocks_symbol": "AAPLx",
        "pool_address": None,
        "enabled": False,
    },
    {
        "ticker": "AAPL",
        "wrapper": Wrapper.DINARI,
        "chain": "arbitrum",
        "pool_address": None,
        "enabled": False,
    },
    {
        "ticker": "TSLA",
        "wrapper": Wrapper.XSTOCKS,
        "chain": "solana",
        "xstocks_symbol": "TSLAx",
        "pool_address": None,
        "enabled": False,
    },
    {
        "ticker": "TSLA",
        "wrapper": Wrapper.DINARI,
        "chain": "arbitrum",
        "pool_address": None,
        "enabled": False,
    },
]

TICKERS = sorted({i["ticker"] for i in INSTRUMENTS})
