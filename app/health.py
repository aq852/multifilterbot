from time import monotonic

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.database import ping_database

app = FastAPI(title="MultiFilterBot health")
started_at = monotonic()


@app.get("/health")
async def health() -> dict[str, object]:
    db_ok = await ping_database()
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "multifilterbot",
        "database": db_ok,
        "uptime_seconds": round(monotonic() - started_at, 2),
    }


@app.get("/ready")
async def ready() -> JSONResponse:
    db_ok = await ping_database()
    payload = {"ready": db_ok, "database": db_ok}
    return JSONResponse(content=payload, status_code=200 if db_ok else 503)


async def run_health_server() -> None:
    config = uvicorn.Config(app, host=settings.health_host, port=settings.health_port, log_level="warning")
    await uvicorn.Server(config).serve()
