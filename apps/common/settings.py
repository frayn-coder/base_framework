"""Application settings management."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

DEFAULT_LOG_CATEGORIES: List[str] = ["access", "error", "app", "perf"]

DEFAULT_LOG_PROJECTS: Dict[str, Dict[str, Any]] = {
    "rag": {"enabled": True, "categories": list(DEFAULT_LOG_CATEGORIES)},
    "text2sql": {"enabled": True, "categories": list(DEFAULT_LOG_CATEGORIES)},
    "uie": {"enabled": True, "categories": list(DEFAULT_LOG_CATEGORIES)},
}

PROJECT_ENV_PREFIX = "LOG_PROJECT_"


def _split_env_list(raw_value: str) -> List[str]:
    """Split a comma separated environment value into a clean list."""
    items = [item.strip() for item in raw_value.split(",") if item.strip()]
    return items or ["*"]


def _default_projects() -> Dict[str, Dict[str, Any]]:
    """Return a deep copy of the default project configuration."""

    return {
        project: {"enabled": config["enabled"], "categories": list(config["categories"])}
        for project, config in DEFAULT_LOG_PROJECTS.items()
    }


def _coerce_project_config(project: str, config: Dict[str, Any]) -> Dict[str, Any] | None:
    """Validate a single project configuration mapping."""

    if not isinstance(config, dict):
        return None

    defaults = DEFAULT_LOG_PROJECTS.get(
        project,
        {"enabled": True, "categories": list(DEFAULT_LOG_CATEGORIES)},
    )

    enabled_val = config.get("enabled", defaults["enabled"])
    if isinstance(enabled_val, str):
        enabled = enabled_val.strip().lower() not in {"false", "0", "no", "off"}
    else:
        enabled = bool(enabled_val)

    categories_val = config.get("categories", defaults["categories"])
    if isinstance(categories_val, (list, tuple)):
        categories = [str(cat).strip() for cat in categories_val if str(cat).strip()]
    else:
        categories = [
            item for item in _split_env_list(str(categories_val)) if item and item != "*"
        ]

    if not categories:
        categories = list(defaults["categories"])

    return {"enabled": enabled, "categories": categories}


def _load_project_overrides() -> Dict[str, Dict[str, Any]]:
    """Load project configurations from segmented environment variables."""

    overrides: Dict[str, Dict[str, Any]] = {}
    for key, raw_value in os.environ.items():
        if not key.startswith(PROJECT_ENV_PREFIX):
            continue

        suffix = key[len(PROJECT_ENV_PREFIX) :].strip()
        if not suffix:
            continue

        project = suffix.lower()
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            continue

        cleaned = _coerce_project_config(project, parsed)
        if cleaned:
            overrides[project] = cleaned

    return overrides


def _load_projects(raw_value: str | None) -> Dict[str, Dict[str, Any]]:
    """Parse the logging projects definition from environment variables."""

    overrides = _load_project_overrides()
    if overrides:
        return overrides

    if not raw_value:
        return _default_projects()

    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        return _default_projects()

    if not isinstance(parsed, dict):
        return _default_projects()

    cleaned: Dict[str, Dict[str, Any]] = {}
    for project, config in parsed.items():
        project_name = str(project).lower()
        cleaned_config = _coerce_project_config(project_name, config)
        if cleaned_config:
            cleaned[project_name] = cleaned_config

    return cleaned or _default_projects()


@dataclass(frozen=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    app_name: str
    api_host: str
    api_port: int
    allow_origins: List[str]
    log_level: str
    log_root: str
    log_backup_days: int
    log_projects: Dict[str, Dict[str, Any]]

    @property
    def logging_config(self) -> Dict[str, Any]:
        """Return a dictionary compatible with :class:`LoggerManager`."""

        return {
            "level": self.log_level,
            "log_root": self.log_root,
            "backup_days": self.log_backup_days,
            "projects": self.log_projects,
        }

    @classmethod
    def from_env(cls) -> "Settings":
        """Build a :class:`Settings` instance from environment variables."""

        return cls(
            app_name=os.getenv("APP_NAME", "Unified API Server"),
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("API_PORT", "8081")),
            allow_origins=_split_env_list(os.getenv("ALLOW_ORIGINS", "*")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_root=os.getenv("LOG_ROOT", "logs"),
            log_backup_days=int(os.getenv("LOG_BACKUP_DAYS", "7")),
            log_projects=_load_projects(os.getenv("LOG_PROJECTS")),
        )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""

    return Settings.from_env()


__all__ = ["Settings", "get_settings"]
