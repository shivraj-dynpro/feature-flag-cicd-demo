# Feature Flag CI/CD Observability Demo

A small, presentation-friendly demo that shows a complete modern delivery loop:

```
Developer changes code
        ↓
   Pull Request
        ↓
     CI passes   (lint · test · security · build)
        ↓
      Merge
        ↓
 Application starts
        ↓
 Prometheus sees requests
        ↓
 Grafana shows dashboard
```

The application itself is intentionally tiny — a **Feature Flag Service** with one flag,
`NEW_UI` — so the focus stays on the **CI/CD pipeline** and **observability**, not the product.

---

## What it does

A FastAPI service that manages a single feature flag, `NEW_UI`.

| Method & Path           | Description                                  |
| ----------------------- | -------------------------------------------- |
| `GET /health`           | Liveness check                               |
| `GET /flags`            | List all flags and their state               |
| `GET /flags/NEW_UI`     | Get the `NEW_UI` flag state                  |
| `PATCH /flags/NEW_UI`   | Toggle / set the `NEW_UI` flag (for the demo)|
| `GET /metrics`          | Prometheus metrics (added in Phase 4)        |

Example flag response:

```json
{
  "name": "NEW_UI",
  "enabled": true
}
```

The default value of `NEW_UI` lives in one obvious place in code so a developer change is
easy to show during the demo.

---

## Tech stack

- **Python 3.12** + **FastAPI**
- **pytest** for tests
- **ruff** for lint + format
- **bandit** + **pip-audit** for security
- **Docker** + **docker-compose**
- **GitHub Actions** for CI
- **Prometheus** + **Grafana** for observability

> No cloud, no Terraform, no Kubernetes, no database, no auth, no paid services.
> Everything runs locally with Docker.

---

## Quick start (after Phase 2)

```bash
# App only
docker compose up --build

# App + Prometheus + Grafana (after Phase 5)
docker compose -f docker-compose.observability.yml up --build
```

Then:

- App:        http://localhost:8000
- Metrics:    http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana:    http://localhost:3000  (admin / admin)

---

## Repository layout

```
feature-flag-cicd-observability-demo/
├── app/
│   ├── main.py            # FastAPI app + routes
│   ├── flags.py           # Flag store + NEW_UI default
│   └── observability.py   # JSON logging, request_id, metrics
├── tests/
│   ├── test_flags.py
│   └── test_api.py
├── .github/workflows/
│   └── ci.yml             # quality · test · security · build gates
├── monitoring/
│   ├── prometheus/prometheus.yml
│   └── grafana/provisioning/   # datasource + dashboard auto-provision
├── Dockerfile
├── docker-compose.yml                 # app only
├── docker-compose.observability.yml   # app + Prometheus + Grafana
├── pyproject.toml
└── README.md
```

---

## Build phases

See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for the full plan. In short:

1. **Phase 1** — FastAPI feature flag app + tests
2. **Phase 2** — Docker + local run
3. **Phase 3** — GitHub Actions CI (quality · test · security · build)
4. **Phase 4** — Observability: JSON logs + Prometheus metrics
5. **Phase 5** — Prometheus + Grafana dashboard
6. **Phase 6** — Demo runbook

---

## Demo script (the 9-step story)

1. Show `NEW_UI` default value in `app/flags.py`
2. Make a small change (flip the default)
3. Open a Pull Request
4. CI passes (all gates green)
5. Merge
6. Run the app
7. Hit the API
8. Prometheus scrapes the metrics
9. Grafana shows the dashboard

📖 Full presenter runbook: **[docs/DEMO.md](./docs/DEMO.md)**
