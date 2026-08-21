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
    ONDO = "ondo"


# Instrument registry: one entry per (ticker, wrapper). `enabled=False`
# entries are scaffolded but not polled yet -- fill in a verified
# pool_address (and flip enabled=True) before adding a ticker/wrapper.
#
# xstocks pool/mint addresses below were confirmed live on 2026-08-20/21:
# GeckoTerminal's specific-pool endpoint for price/reserve, and Solana RPC
# getAccountInfo (jsonParsed) for the mint's tokenMetadata +
# scaledUiAmountConfig extensions (symbol matches, same issuer authority
# 5aMNNLQJwAEeoemTEMkv5NVjqKwvvefRYCQ5Z67HFvEq as NVDAx). Pool prices also
# cross-checked against real underlying prices at the time (NVDA $219.74 vs
# pool $218.96; AAPL $313.28 vs pool $313.75; TSLA $345.13 vs pool $348.64).
# AAPLx/USDC liquidity is thin ($100k reserve vs NVDA's $2.4M/TSLA's $2.0M)
# -- watch for stale/wide quotes on that one.
#
# */dinari has NO confirmed pool for any of these three: GeckoTerminal
# search returns nothing on Arbitrum, consistent with Dinari's primary
# liquidity being broker-dealer mint/burn rather than an AMM pool -- see
# docs/data-sources.md. Left disabled rather than guessed; also blocked on
# partner API access for NAV data as an alternate source.
#
# */ondo pool addresses confirmed live 2026-08-21 the same way as xstocks
# (GeckoTerminal specific-pool endpoint, price cross-checked against real
# underlying price: NVDA $219.74 vs pool $220.65; AAPL $313.28 vs pool
# $314.92; TSLA $345.13 vs pool $345.43) -- all on Ethereum/Uniswap v3.
# Liquidity is thin across the board ($3k-$33k reserve, thinner than any
# xstocks pool) -- treat depth/spread estimates on these as low-confidence.
#
# Ondo's multiplier: their own SyntheticSharesOracle ("sValue") on Ethereum
# wasn't pinned down, BUT Ondo also issues each of these on Solana, and
# those Solana mints use the exact same Token-2022 Scaled UI Amount
# extension as xstocks (confirmed live 2026-08-21 -- e.g. NVDAon's Solana
# mint multiplier reads 1.0009320542470574). solana_multiplier_mint below
# points at that Solana-side mint even though the polled price comes from
# the Ethereum pool -- this assumes Ondo keeps the NAV-adjustment factor
# in sync across chains for the same underlying, which is the standard
# multi-chain-issuance assumption but wasn't independently cross-checked
# against an Ethereum-side value (couldn't find one to check against).
INSTRUMENTS = [
    {
        "ticker": "NVDA",
        "wrapper": Wrapper.XSTOCKS,
        "chain": "solana",
        "xstocks_symbol": "NVDAx",
        "pool_address": "49iMatQtoyabsYAQc8GafVq6aeBFVDxSRH44oiatyyw6",
        "solana_multiplier_mint": "Xsc9qvGR1efVDFGLrVsmkzv3qi45LTBjeUKSPmx9qEh",
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
        "ticker": "NVDA",
        "wrapper": Wrapper.ONDO,
        "chain": "eth",
        "pool_address": "0xf5294094bce435bfbd0ec488be5c462aaf32bc7a",
        "solana_multiplier_mint": "gEGtLTPNQ7jcg25zTetkbmF7teoDLcrfTnQfmn2ondo",
        "enabled": True,
    },
    {
        "ticker": "AAPL",
        "wrapper": Wrapper.XSTOCKS,
        "chain": "solana",
        "xstocks_symbol": "AAPLx",
        "pool_address": "EHdow7Yhmr1ac8Qff9Co1LhSosr38puA6zLd4cbJLdpV",
        "solana_multiplier_mint": "XsbEhLAtcf6HdfpFZ5xEMdqW8nfAvcsP5bdudRLJzJp",
        "enabled": True,
    },
    {
        "ticker": "AAPL",
        "wrapper": Wrapper.DINARI,
        "chain": "arbitrum",
        "pool_address": None,
        "enabled": False,
    },
    {
        "ticker": "AAPL",
        "wrapper": Wrapper.ONDO,
        "chain": "eth",
        "pool_address": "0x50b31ab7a061843ca6ebab6c006ab4ece6ca2fd8",
        "solana_multiplier_mint": "123mYEnRLM2LLYsJW3K6oyYh8uP1fngj732iG638ondo",
        "enabled": True,
    },
    {
        "ticker": "TSLA",
        "wrapper": Wrapper.XSTOCKS,
        "chain": "solana",
        "xstocks_symbol": "TSLAx",
        "pool_address": "8aDaBQkTrS6HVMjyc6EZebgdiaXhLYGriDWKWWp1NpFF",
        "solana_multiplier_mint": "XsDoVfqeBukxuZHWhdvWHBhgEHjGNst4MLodqsJHzoB",
        "enabled": True,
    },
    {
        "ticker": "TSLA",
        "wrapper": Wrapper.DINARI,
        "chain": "arbitrum",
        "pool_address": None,
        "enabled": False,
    },
    {
        "ticker": "TSLA",
        "wrapper": Wrapper.ONDO,
        "chain": "eth",
        "pool_address": "0x31227b50eccdc9c589826aa2d9e7c5619b1895da",
        "solana_multiplier_mint": "KeGv7bsfR4MheC1CkmnAVceoApjrkvBhHYjWb67ondo",
        "enabled": True,
    },
]

TICKERS = sorted({i["ticker"] for i in INSTRUMENTS})
