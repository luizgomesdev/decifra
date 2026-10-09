from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from decifra.config import get_settings
from decifra.features.chat.router import router as chat_router
from decifra.features.reports.router import router as reports_router
from decifra.shared.db import close_pool
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


@app.get("/health")
def health() -> dict:
    collections = get_qdrant_client().get_collections().collections
    return {"status": "ok", "qdrant_collections": [c.name for c in collections]}
