"""Application settings management."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _split_env_list(raw_value: str) -> List[str]:
    """Split a comma separated environment value into a clean list."""
    items = [item.strip() for item in raw_value.split(",") if item.strip()]
    return items or ["*"]


@dataclass(frozen=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    app_name: str
    api_host: str
    api_port: int
    allow_origins: List[str]
    log_config: str

    @property
    def log_config_path(self) -> Path:
        """Return the absolute path to the logging configuration file."""
        return Path(self.log_config).resolve()

    @classmethod
    def from_env(cls) -> "Settings":
        """Build a :class:`Settings` instance from environment variables."""
        return cls(
            app_name=os.getenv("APP_NAME", "Unified API Server"),
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("API_PORT", "8081")),
            allow_origins=_split_env_list(os.getenv("ALLOW_ORIGINS", "*")),
            log_config=os.getenv("LOG_CONFIG", "logging.yaml"),
        )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings.from_env()


__all__ = ["Settings", "get_settings"]
