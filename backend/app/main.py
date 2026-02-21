from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.db.database import init_db


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG Policy Intelligence Engine",
        version="1.0.0",
        description="RAG-powered document intelligence backend",
    )

    # CORS (Allow frontend on Vercel)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    return app


app = create_app()
