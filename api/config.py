import os

DATABASE_URL = os.environ["DATABASE_URL"]

# How stale a normalized_prices row can be before it's excluded from
# /spreads -- the poller runs every POLL_INTERVAL_SECONDS (default 300s
# in poller/config.py), so anything much older than a couple of cycles
# means that wrapper's feed is stuck/down, not just between polls.
MAX_QUOTE_AGE_SECONDS = int(os.environ.get("MAX_QUOTE_AGE_SECONDS", 900))
