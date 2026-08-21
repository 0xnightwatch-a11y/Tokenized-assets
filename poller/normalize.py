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

    Empirical spot-check (2026-08-20): NVDAx/USDC raw pool price was
    $218.96 vs. NVDA underlying at $219.74 -- multiplier is evidently ~1.0
    right now (no recent corporate action), so this direction could not be
    definitively confirmed against a multiplier != 1. Re-verify once a real
    multiplier value is observed via the xStocks API.
    """
    return Decimal(str(raw_price_usd)) * Decimal(str(multiplier))


def deviation_bps(normalized_price_usd, underlying_price_usd) -> Decimal:
    normalized = Decimal(str(normalized_price_usd))
    underlying = Decimal(str(underlying_price_usd))
    if underlying == 0:
        return Decimal(0)
    return (normalized - underlying) / underlying * Decimal(10000)
