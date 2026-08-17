"""
FastAPI application factory.

Creates the FastAPI app, configures CORS middleware,
includes all route routers, and runs startup hooks.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from nexus.config import get_settings
from nexus.api.routes import chat, history, files
from nexus.chat.history import init_title_db


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Nexus AI Backend",
        version="2.0.0",
        description="Agentic RAG Orchestrator powered by Gemini 3.7 Flash",
    )

    # ── CORS ─────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes ───────────────────────────────────────────────────────
    app.include_router(chat.router)
    app.include_router(history.router)
    app.include_router(files.router)

    # ── Startup hooks ────────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup():
        os.makedirs(settings.upload_dir, exist_ok=True)
        init_title_db()

    return app
