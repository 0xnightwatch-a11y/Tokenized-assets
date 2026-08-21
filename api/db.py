import psycopg2
import psycopg2.extras

import config


def connect():
    conn = psycopg2.connect(config.DATABASE_URL)
    conn.autocommit = True
    return conn


def latest_normalized_prices(conn, ticker: str | None = None):
    """One row per (ticker, wrapper): the most recent normalized_prices
    entry, if it's fresher than MAX_QUOTE_AGE_SECONDS. This is the raw
    material the spread engine diffs pairwise per ticker.
    """
    query = """
        SELECT DISTINCT ON (ticker, wrapper)
            ticker, wrapper, chain, raw_price_usd, multiplier, multiplier_source,
            normalized_price_usd, underlying_price_usd, deviation_bps, fetched_at
        FROM normalized_prices
        WHERE fetched_at > now() - (%(max_age_seconds)s || ' seconds')::interval
    """
    params = {"max_age_seconds": config.MAX_QUOTE_AGE_SECONDS}
    if ticker:
        query += " AND ticker = %(ticker)s"
        params["ticker"] = ticker
    query += " ORDER BY ticker, wrapper, fetched_at DESC"

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query, params)
        return cur.fetchall()


def latest_pool_reserve(conn, ticker: str, wrapper: str, chain: str):
    """Most recent pool reserve_usd for a (ticker, wrapper, chain) -- feeds
    the executable-depth estimate.
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT reserve_usd
            FROM raw_pool_snapshots
            WHERE ticker = %(ticker)s AND wrapper = %(wrapper)s AND chain = %(chain)s
            ORDER BY fetched_at DESC
            LIMIT 1
            """,
            {"ticker": ticker, "wrapper": wrapper, "chain": chain},
        )
        row = cur.fetchone()
        return row["reserve_usd"] if row else None
