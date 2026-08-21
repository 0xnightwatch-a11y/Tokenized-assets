from decimal import Decimal


def apply_multiplier(raw_price_usd, multiplier) -> Decimal:
    """Convert a raw on-chain pool price into NAV-accrual (per-share-equivalent)
    terms.

    xStocks tokens on Solana use the Token-2022 Scaled UI Amount extension:
    the raw on-chain balance is constant and a multiplier is applied only at
    display time as dividends/splits accrue. AMM pool prices are typically
    quoted off raw reserve ratios, so as the multiplier grows the raw pool
    price increasingly understates true NAV-equivalent value per display
    unit -- hence multiplying (not dividing) here.

    Confirmed live (2026-08-20) via Solana RPC (sources/solana_rpc.py):
    NVDAx's scaledUiAmountConfig multiplier is 1.000103090792305, with a
    scheduled bump to 1.0009180758490996 already queued on-chain. Raw pool
    price ($218.96) vs. NVDA underlying (~$219.74) is consistent with a
    multiplier this close to 1.0 -- re-check the direction once the
    multiplier has moved further from 1.0 and produces a bigger, more
    conclusive delta.
    """
    return Decimal(str(raw_price_usd)) * Decimal(str(multiplier))


def deviation_bps(normalized_price_usd, underlying_price_usd) -> Decimal:
    normalized = Decimal(str(normalized_price_usd))
    underlying = Decimal(str(underlying_price_usd))
    if underlying == 0:
        return Decimal(0)
    return (normalized - underlying) / underlying * Decimal(10000)
