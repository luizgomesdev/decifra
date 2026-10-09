from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from decifra.config import get_settings
from decifra.features.chat.router import router as chat_router
from decifra.features.reports.router import router as reports_router
from decifra.shared.db import close_pool, get_pool
from decifra.shared.vectorstore import ensure_collection, get_qdrant_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_collection()
    yield
    close_pool()


app = FastAPI(title="Decifra API", lifespan=lifespan)

# The front runs on another origin, local in development and the server address in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports_router)
app.include_router(chat_router)


def probe(check) -> dict:
    try:
        check()
    except Exception as error:  # noqa: BLE001 - any failure means the dependency is down
        return {"status": "down", "error": type(error).__name__}
    return {"status": "ok"}


def qdrant_is_reachable() -> None:
    get_qdrant_client().get_collections()


def postgres_is_reachable() -> None:
    with get_pool().connection() as connection:
        connection.execute("SELECT 1")


def model_is_configured() -> None:
    if not get_settings().openai_api_key:
        raise RuntimeError("missing OPENAI_API_KEY")


@app.get("/health")
def health() -> JSONResponse:
    dependencies = {
        "qdrant": probe(qdrant_is_reachable),
        "postgres": probe(postgres_is_reachable),
        "model": probe(model_is_configured),
    }
    down = [name for name, result in dependencies.items() if result["status"] == "down"]
    body = {"status": "down" if down else "ok", "dependencies": dependencies}
    return JSONResponse(body, status_code=503 if down else 200)
