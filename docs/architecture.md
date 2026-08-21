# Architecture

## Stack

Single Docker Compose stack, one GCP VM. No managed external services
(no Supabase, no Railway/Render) — self-hosted to keep ongoing cost
near zero.

```
services:
  postgres   — self-hosted Postgres, time-series price/spread data
  poller     — scheduled job: pulls all data sources, normalizes, writes DB
  api        — spread engine + web/API surface, reads DB
  caddy      — reverse proxy, automatic HTTPS via Let's Encrypt
```

See /docker-compose.yml in repo root for the actual compose file, and
/Caddyfile for the reverse-proxy config.

## Data flow

1. `poller` runs on a schedule (target: every 1-5 min). For each
   tracked ticker/wrapper pair, pulls raw price + pool depth
   (GeckoTerminal), underlying reference price (Alpaca), and current
   multiplier/NAV-adjustment values (Dinari, xStocks APIs).
2. `poller` applies the rebasing normalization (see PROJECT.md — this
   is the critical correctness step) and writes normalized prices +
   timestamps to Postgres.
3. `api` reads normalized data, computes cross-wrapper spreads in bps,
   flags each as closeable/wrapper-basis (see
   docs/redemption-gating.md), estimates executable depth at
   $1k/$10k/$50k from pool reserves, and serves both the public daily
   fixing page and the (later) paid live screener/API.
4. `caddy` terminates TLS and routes traffic to `api`.

## VM setup (GCP)

- **Instance**: e2-small (2 vCPU, 2 GB RAM) while free trial credits
  last; right-size down to e2-micro (2 vCPU, 1 GB RAM, Always Free —
  us-west1/us-central1/us-east1 only) once real resource usage is
  confirmed. Set a reminder for when the $300 trial (90 days from
  activation) expires, and resize before it starts billing at list rate.
- **Disk**: Standard persistent disk only (not SSD/Balanced — those
  are billed even under Always Free). 30 GB is within the free
  allowance.
- **Static IP**: reserve one, point the domain's A record at it. Free
  while attached to a running instance; only billbilled if reserved
  and left unattached or the VM is stopped.
- **Firewall**: only 80/443 open publicly, 22 restricted to your own
  IP for SSH. Postgres must NOT be exposed externally — only reachable
  inside the Docker network.
- **Egress**: 1 GB/month free (North America, excluding China/Australia)
  — this app moves small JSON payloads, should stay near-free
  indefinitely at this scale.

## Deployment steps

1. Install Docker + Compose plugin on the VM (Debian/Ubuntu via
   standard apt/convenience script).
2. `git clone` the repo (or `git pull` on redeploy).
3. Populate `.env` from `.env.example` (see repo root) with any API
   keys (Alpaca key, xStocks key if applicable — GeckoTerminal needs
   none at free tier).
4. `docker compose up -d`.
5. Confirm all four services are healthy: `docker compose ps`.
6. Test restart resilience once: `sudo reboot`, then confirm
   `docker compose ps` shows everything back up on its own (all
   services use `restart: unless-stopped`).

## Backups

Small cron job on the VM host (not in a container) running `pg_dump`
on a schedule, pushed to a GCS bucket. 5 GB-months of Standard Storage
is within Always Free — plenty for periodic dumps of a database this
size. Script to be written in Stage 1 (see docs/stage1-plan.md).

## Monitoring

Skip GCP's paid Cloud Monitoring for now. UptimeRobot's free tier
pinging the `api` service's health endpoint is sufficient signal for
a solo operator at this stage.
