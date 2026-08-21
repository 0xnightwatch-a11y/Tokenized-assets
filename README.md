# Tokenized Equity Spread Dashboard

Start here: **PROJECT.md** — full build spec.

Supporting docs (read the relevant one before working in that area):
- `docs/data-sources.md` — ticker/wrapper map, API details
- `docs/redemption-gating.md` — which spreads are closeable vs. wrapper basis
- `docs/architecture.md` — Docker Compose stack, GCP VM deployment
- `docs/cost-budget.md` — cost constraints, do-not-exceed list
- `docs/stage1-plan.md` — full Stage 1 (0-3 month) build plan

Scaffolding already in place: `docker-compose.yml`, `Caddyfile`,
`.env.example`. `poller/` and `api/` are empty — that's the first
build task.
