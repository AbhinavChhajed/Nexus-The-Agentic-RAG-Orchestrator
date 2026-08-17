"""
Nexus AI Service — Entrypoint

Slim entrypoint that creates the FastAPI app and runs it with uvicorn.
All logic lives in the `nexus` package.
"""

import uvicorn

from nexus.config import get_settings
from nexus.api.app import create_app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )