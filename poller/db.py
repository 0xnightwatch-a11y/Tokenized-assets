import logging
import os

import psycopg2
import psycopg2.extras

import config

log = logging.getLogger(__name__)


def connect():
    conn = psycopg2.connect(config.DATABASE_URL)
    conn.autocommit = True
    return conn


def init_schema(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    log.info("schema ensured")


def insert_raw_pool_snapshot(conn, row):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw_pool_snapshots
                (ticker, wrapper, chain, pool_address, dex, raw_price_usd, reserve_usd)
            VALUES (%(ticker)s, %(wrapper)s, %(chain)s, %(pool_address)s, %(dex)s,
                    %(raw_price_usd)s, %(reserve_usd)s)
            """,
            row,
        )


def insert_underlying_price(conn, row):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO underlying_prices (ticker, price_usd, source, quote_time)
            VALUES (%(ticker)s, %(price_usd)s, %(source)s, %(quote_time)s)
            """,
            row,
        )


def insert_multiplier(conn, row):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO multipliers (ticker, wrapper, multiplier, source)
            VALUES (%(ticker)s, %(wrapper)s, %(multiplier)s, %(source)s)
            """,
            row,
        )


def insert_normalized_price(conn, row):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO normalized_prices
                (ticker, wrapper, chain, raw_price_usd, multiplier, multiplier_source,
                 normalized_price_usd, underlying_price_usd, deviation_bps)
            VALUES (%(ticker)s, %(wrapper)s, %(chain)s, %(raw_price_usd)s, %(multiplier)s,
                    %(multiplier_source)s, %(normalized_price_usd)s, %(underlying_price_usd)s,
                    %(deviation_bps)s)
            """,
            row,
        )
