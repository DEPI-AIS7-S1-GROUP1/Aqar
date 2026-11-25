"""FastAPI entry point.

S0-T2-1 only adds /health so the compose healthcheck has something to call.
Real routes (e.g. /conversations in S1-T8-2) go under app/api/v1.
"""

from fastapi import FastAPI

app = FastAPI(title="AqarAI API")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check. Does not touch db or redis."""
    return {"status": "ok"}
