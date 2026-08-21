from decimal import Decimal
from itertools import combinations

# Per docs/redemption-gating.md "Practical implication for the product":
# a spread between a US-accessible wrapper and a non-US-only wrapper is
# jurisdictional segmentation, not executable arbitrage -- one side of the
# trade is legally closed to whoever the other side is open to. This is a
# v1 simplification: it only checks the US-access mismatch, not the finer
# redemption-access differences (accreditation, qualified-purchaser status,
# min size) also listed in that doc.
US_ACCESSIBLE = {
    "dinari": True,
    "xstocks": False,
    "ondo": False,
}

DEPTH_LEVELS_USD = [1_000, 10_000, 50_000]


def is_closeable(wrapper_a: str, wrapper_b: str) -> bool:
    return US_ACCESSIBLE.get(wrapper_a) == US_ACCESSIBLE.get(wrapper_b)


def spread_bps(price_a, price_b) -> Decimal:
    a, b = Decimal(str(price_a)), Decimal(str(price_b))
    if b == 0:
        return Decimal(0)
    return (a - b) / b * Decimal(10000)


def estimate_depth_impact_bps(trade_usd: int, reserve_usd) -> Decimal | None:
    """Rough price-impact estimate for a trade of `trade_usd` against a pool
    with `reserve_usd` total value locked.

    This assumes a constant-product AMM with reserves split evenly across
    both sides, and linearizes for trade_usd << reserve_usd (impact_pct ~=
    trade_usd / one_side_reserve). It is NOT accurate for concentrated-
    liquidity pools (Raydium CLMM, Byreal, etc -- several of the pools this
    project polls) where real depth near the current price can be much
    thinner or thicker than the flat 50/50 split assumed here. Good enough
    for a v1 "is this even in the right ballpark" signal; revisit with
    real per-tick liquidity data before quoting this to a paying customer.
    """
    if reserve_usd is None or reserve_usd <= 0:
        return None
    one_side_reserve = Decimal(str(reserve_usd)) / 2
    return Decimal(trade_usd) / one_side_reserve * Decimal(10000)


def compute_ticker_spreads(ticker: str, quotes: list[dict], reserves: dict) -> list[dict]:
    """`quotes`: normalized_prices rows for this ticker (one per wrapper).
    `reserves`: {wrapper: reserve_usd} for depth estimates.
    Returns one row per wrapper pair.
    """
    results = []
    for q_a, q_b in combinations(quotes, 2):
        bps = spread_bps(q_a["normalized_price_usd"], q_b["normalized_price_usd"])
        results.append(
            {
                "ticker": ticker,
                "wrapper_a": q_a["wrapper"],
                "wrapper_b": q_b["wrapper"],
                "price_a_usd": q_a["normalized_price_usd"],
                "price_b_usd": q_b["normalized_price_usd"],
                "spread_bps": bps,
                "closeable": is_closeable(q_a["wrapper"], q_b["wrapper"]),
                "depth_impact_bps": {
                    str(usd): {
                        "wrapper_a": estimate_depth_impact_bps(usd, reserves.get(q_a["wrapper"])),
                        "wrapper_b": estimate_depth_impact_bps(usd, reserves.get(q_b["wrapper"])),
                    }
                    for usd in DEPTH_LEVELS_USD
                },
            }
        )
    return results
