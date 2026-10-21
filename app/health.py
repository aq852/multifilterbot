from fastapi import FastAPI
import uvicorn

from app.config import settings
from app.database import ping_database

app = FastAPI(title="MultiFilterBot health")


@app.get("/health")
async def health() -> dict[str, object]:
    db_ok = await ping_database()
    return {"status": "ok" if db_ok else "degraded", "database": db_ok}


async def run_health_server() -> None:
    config = uvicorn.Config(app, host=settings.health_host, port=settings.health_port, log_level="warning")
    await uvicorn.Server(config).serve()

