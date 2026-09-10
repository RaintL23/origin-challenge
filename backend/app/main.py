from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import close_connection_pool, get_connection_pool
from app.routers import auth, favorites, stocks


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_connection_pool()
    try:
        yield
    finally:
        close_connection_pool()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Challenge Acciones API",
        description="API intermediaria entre el Frontend y Twelve Data",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(favorites.router)
    app.include_router(stocks.router)

    @app.get("/health")
    def health() -> dict[str, str]:
        pool = get_connection_pool()
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return {"status": "ok", "database": "postgres"}

    return app


app = create_app()
