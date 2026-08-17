"""
Centralized configuration using Pydantic Settings.

All environment variables, model parameters, and runtime configuration
are defined here as a single source of truth. Values are loaded from
the .env file and can be overridden by actual environment variables.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


# Suppress HuggingFace symlink warnings on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────────────────
    google_api_key: str
    llm_model_name: str = "gemini-3.7-flash"
    llm_temperature: float = 0.0

    # ── Embeddings ───────────────────────────────────────────────────────
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"

    # ── RAG ──────────────────────────────────────────────────────────────
    chunk_size: int = 1000
    chunk_overlap: int = 100
    retriever_top_k: int = 2

    # ── Persistence ──────────────────────────────────────────────────────
    memory_db_path: str = "nexus_memory.db"
    title_db_path: str = "nexus.db"

    # ── Server ───────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    upload_dir: str = "uploads"

    # ── CORS ─────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["*"]

    # ── Agent System Prompt ──────────────────────────────────────────────
    system_prompt: str = (
        "You are Nexus, an advanced AI with file-reading capabilities.\n\n"
        "CRITICAL RULES:\n"
        "1. You have a tool named 'retrieve_documents'.\n"
        "2. IF the user asks about \"the file\", \"uploaded documents\", or content you don't know:\n"
        "   YOU MUST USE 'retrieve_documents' to look it up.\n"
        "3. DO NOT say \"I cannot access files\". You HAVE the tool. Use it.\n"
        "4. If the tool returns text, assume it is the correct content of the file."
    )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once at startup)."""
    return Settings()
