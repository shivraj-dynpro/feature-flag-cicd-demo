# Demo Runbook

A presenter-friendly script for the **Feature Flag CI/CD Observability Demo**.

The story in one line:

> **Developer changes code → PR → CI passes → Merge → App starts → Prometheus sees requests → Grafana shows the dashboard.**

Everything runs locally with Docker. No cloud, no Kubernetes, no database.

---

## 0. Before you present (one-time setup)

- Docker Desktop running.
- This repo cloned.
- Two browser tabs ready: the GitHub repo, and a blank tab for Grafana.

URLs you'll use:

| Service    | URL                          | Notes                       |
| ---------- | ---------------------------- | --------------------------- |
| App        | http://localhost:8000        | the API                     |
| Metrics    | http://localhost:8000/metrics| Prometheus format           |
| Prometheus | http://localhost:9090        | Status → Targets            |
| Grafana    | http://localhost:3000        | admin / admin (or just view)|

---

## 1. Start the stack

```bash
docker compose -f docker-compose.observability.yml up --build
```

This starts three containers: **app**, **Prometheus**, **Grafana**.

Wait until you see the app logging JSON lines and Grafana saying it's ready.

> 💡 Talking point: "One command brings up the application *and* its full observability stack."

---

## 2. Show the GitHub PR flow

Open the repo on GitHub and show the **Pull Requests** tab.

- Each phase of this project was built as its own PR (Phases 1–6).
- A developer never pushes straight to `main` — every change goes through a PR.

> 💡 Talking point: "Change → Pull Request. This is where review and automation happen before anything reaches `main`."

---

## 3. Show the CI gates

Open any merged PR → **Checks** (or the **Actions** tab). Point at the four gates:

| Gate          | What it does                          |
| ------------- | ------------------------------------- |
| 🧹 **Quality** | `ruff check` + `ruff format --check`  |
| 🧪 **Test**    | `pytest`                              |
| 🔒 **Security**| `bandit` + `pip-audit`                |
| 🐳 **Build**   | `docker build`                        |

All four must be green before a merge.

> 💡 Talking point: "CI is the safety net. Lint, tests, security scan, and a real container build — all automatic, all required."

---

## 4. Show the NEW_UI feature flag

The whole app is built around one flag: **`NEW_UI`**.

**Read the current state:**

```bash
curl -s http://localhost:8000/flags/NEW_UI
# {"name":"NEW_UI","enabled":false}
```

**Turn it on (set):**

```bash
curl -s -X PATCH http://localhost:8000/flags/NEW_UI \
  -H 'Content-Type: application/json' -d '{"enabled":true}'
# {"name":"NEW_UI","enabled":true}
```

**Toggle it (no body = flip):**

```bash
curl -s -X PATCH http://localhost:8000/flags/NEW_UI -d '{}'
# flips enabled back to false
```

**List all flags:**

```bash
curl -s http://localhost:8000/flags
# [{"name":"NEW_UI","enabled":false}]
```

> 💡 The default value lives in **one obvious line** — `NEW_UI_DEFAULT` in
> [`app/flags.py`](../app/flags.py). That's the "developer change" you make in the demo.

### The "developer change" moment

1. Open `app/flags.py`, show `NEW_UI_DEFAULT = False`.
2. Change it to `True`.
3. That single line is the change that flows through PR → CI → merge → deploy.

---

## 5. Show observability

### a) Raw metrics

```bash
curl -s http://localhost:8000/metrics | grep -E "http_requests_total|feature_flag_changes_total"
```

You'll see the three demo metrics:

- `http_requests_total`
- `http_request_duration_seconds`
- `feature_flag_changes_total`

### b) Prometheus is scraping the app

Open **http://localhost:9090** → **Status → Targets**.

- The `feature-flag-app` target should be **UP**.

Try a query in the Prometheus expression bar:

```promql
feature_flag_changes_total
```

> 💡 Talking point: "Prometheus pulls `/metrics` every few seconds. Each flag change shows up here."

### c) Grafana dashboard

Open **http://localhost:3000** → dashboard **"Feature Flag Demo"**.

Four panels:

- **App availability** — is the app up?
- **Request count** — traffic by path
- **Request latency (p95)** — how fast
- **Feature flag changes** — how often `NEW_UI` changes

Now generate some live traffic and watch the panels move:

```bash
for i in $(seq 1 10); do curl -s http://localhost:8000/flags/NEW_UI > /dev/null; done
curl -s -X PATCH http://localhost:8000/flags/NEW_UI -d '{}'
```

> 💡 Talking point: "Hit the API, and seconds later the dashboard updates. That's the whole feedback loop, live."

---

## 6. Tell the final story

Walk the audience back through the full loop, now that they've seen each piece:

```
Developer changes code        (flip NEW_UI_DEFAULT in app/flags.py)
        ↓
Pull Request                  (GitHub PR)
        ↓
CI passes                     (quality · test · security · build)
        ↓
Merge                         (into main)
        ↓
Application starts            (docker compose up)
        ↓
Prometheus sees requests      (scrapes /metrics)
        ↓
Grafana shows dashboard       (live panels)
```

> 💡 Closing line: "A one-line code change, shipped safely through CI, and observable end to end — in a demo small enough to read in five minutes."

---

## Teardown

```bash
docker compose -f docker-compose.observability.yml down
```

Add `-v` if you also want to remove any volumes.

---

## Troubleshooting

| Symptom                              | Fix                                                                 |
| ------------------------------------ | ------------------------------------------------------------------- |
| Ports 8000/9090/3000 already in use  | Stop the other process, or change the port mappings in the compose. |
| Prometheus target shows **DOWN**     | Give it ~10s; confirm the `app` container is healthy.               |
| Grafana dashboard empty              | Generate traffic (Step 5c); panels need data points to draw.        |
| Docker daemon not running            | Start Docker Desktop, then re-run the `up` command.                  |
| Grafana asks for login               | Use `admin` / `admin`, or just view (anonymous viewer is enabled).  |
