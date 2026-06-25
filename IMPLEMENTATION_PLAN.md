# Implementation Plan

Goal: a **simple, presentation-friendly** CI/CD + Observability demo built around a
single feature flag (`NEW_UI`). Keep it minimal — no cloud, no Terraform, no Kubernetes,
no database, no auth, no paid services.

## Guiding principles

- **Simple over complete.** Every file should be explainable in one sentence during a demo.
- **One flag, one story.** `NEW_UI` is the whole product surface.
- **Phase by phase.** Each phase is a branch → PR → review → merge.
- **Green at every step.** Tests pass before each commit.

## Workflow per phase

```
checkout new branch  →  build phase  →  run tests  →  commit  →  push branch  →  open PR  →  wait for review  →  merge
```

Branch naming: `phaseN-short-name` (e.g. `phase1-app`).
Base branch: `main` (seeded with README + this plan).

---

## Phase 1 — FastAPI feature flag app + tests
**Branch:** `phase1-app`

- `pyproject.toml` — project metadata, deps (fastapi, uvicorn), dev deps (pytest, ruff, httpx), ruff config.
- `app/flags.py` — in-memory flag store; `NEW_UI` default in ONE obvious constant.
- `app/main.py` — FastAPI app with routes:
  - `GET /health` → `{"status": "ok"}`
  - `GET /flags` → list of all flags
  - `GET /flags/NEW_UI` → `{"name": "NEW_UI", "enabled": <bool>}`
  - `PATCH /flags/NEW_UI` → set/toggle, returns new state
- `tests/test_flags.py` — unit tests for the flag store.
- `tests/test_api.py` — API tests via FastAPI TestClient.

**Done when:** `ruff check`, `ruff format --check`, and `pytest` all pass locally.

---

## Phase 2 — Docker + local run
**Branch:** `phase2-docker`

- `Dockerfile` — python:3.12-slim, install deps, run uvicorn.
- `docker-compose.yml` — app only, port 8000.
- `.dockerignore`.
- README run instructions verified.

**Done when:** `docker compose up --build` serves the API on :8000.

---

## Phase 3 — GitHub Actions CI
**Branch:** `phase3-ci`

- `.github/workflows/ci.yml`, triggered on pull_request (and push to main), with jobs:
  1. **Quality gate** — `ruff check` + `ruff format --check`
  2. **Test gate** — `pytest`
  3. **Security gate** — `bandit` + `pip-audit`
  4. **Build gate** — `docker build`
- Add bandit + pip-audit to dev deps.

**Done when:** CI runs green on the PR.

---

## Phase 4 — Observability: logs + metrics
**Branch:** `phase4-observability`

- `app/observability.py`:
  - Structured **JSON logs**.
  - **request_id** correlation (middleware, header `X-Request-ID`).
  - Prometheus metrics via `prometheus-client`:
    - `http_requests_total` (counter, by method/path/status)
    - `http_request_duration_seconds` (histogram)
    - `feature_flag_changes_total` (counter, incremented on PATCH)
- Wire middleware + `GET /metrics` into `app/main.py`.
- Tests for metrics endpoint and request_id header.

**Done when:** `/metrics` exposes the three metrics; tests pass.

---

## Phase 5 — Prometheus + Grafana dashboard
**Branch:** `phase5-monitoring`

- `monitoring/prometheus/prometheus.yml` — scrape app `/metrics`.
- `monitoring/grafana/provisioning/datasources/` — auto-provision Prometheus datasource.
- `monitoring/grafana/provisioning/dashboards/` — dashboard provider config.
- `monitoring/grafana/dashboards/feature-flag-demo.json` — dashboard with:
  - App availability (up)
  - Request count
  - Request latency
  - Feature flag changes
- `docker-compose.observability.yml` — app + Prometheus + Grafana.

**Done when:** `docker compose -f docker-compose.observability.yml up` brings up all three,
Prometheus scrapes the app, Grafana shows the dashboard.

---

## Phase 6 — Demo runbook
**Branch:** `phase6-runbook`

- `docs/DEMO.md` (or README section) — the 9-step demo script with exact commands:
  1. Show `NEW_UI` default in `app/flags.py`
  2. Make a small change (flip default)
  3. Open PR
  4. CI passes
  5. Merge
  6. Run app
  7. Hit API
  8. Prometheus sees metrics
  9. Grafana shows dashboard
- Troubleshooting notes + teardown commands.

**Done when:** someone can run the demo end to end from the runbook alone.

---

## Out of scope (intentionally)

AWS / any cloud, Terraform, Kubernetes, databases, authentication, paid services,
multiple flags, persistence beyond process memory, user management.
