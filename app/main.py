"""FastAPI Feature Flag Service.

Exposes a tiny API around a single feature flag (``NEW_UI``):

- ``GET  /health``        liveness check
- ``GET  /flags``         list all flags
- ``GET  /flags/{name}``  get one flag (e.g. ``/flags/NEW_UI``)
- ``PATCH /flags/{name}`` set or toggle a flag (e.g. ``/flags/NEW_UI``)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.flags import default_store

app = FastAPI(title="Feature Flag Service", version="0.1.0")

# Process-memory store (resets on restart — fine for a demo).
store = default_store()


class FlagState(BaseModel):
    name: str
    enabled: bool


class FlagUpdate(BaseModel):
    # When ``enabled`` is omitted the flag is toggled; otherwise it is set.
    enabled: bool | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/flags", response_model=list[FlagState])
def list_flags() -> list[FlagState]:
    return [FlagState(name=name, enabled=enabled) for name, enabled in store.all().items()]


@app.get("/flags/{name}", response_model=FlagState)
def get_flag(name: str) -> FlagState:
    try:
        return FlagState(name=name, enabled=store.get(name))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown flag: {name}") from None


@app.patch("/flags/{name}", response_model=FlagState)
def update_flag(name: str, update: FlagUpdate) -> FlagState:
    try:
        if update.enabled is None:
            enabled = store.toggle(name)
        else:
            enabled = store.set(name, update.enabled)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown flag: {name}") from None
    return FlagState(name=name, enabled=enabled)
