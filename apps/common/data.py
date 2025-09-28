"""Utility helpers for managing prompt and conversation data on disk."""
from __future__ import annotations

from pathlib import Path
from typing import List

DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


def _ensure_data_root() -> Path:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    return DATA_ROOT


def _sanitize_segment(segment: str) -> str:
    if not segment:
        raise ValueError("Segment must be a non-empty string")
    segment_path = Path(segment)
    if segment_path.is_absolute() or any(part == ".." for part in segment_path.parts):
        raise ValueError("Segment cannot be absolute or contain parent directory references")
    return segment_path.as_posix()


def _resolve(app_name: str, filename: str | None = None) -> Path:
    root = _ensure_data_root()
    app_segment = _sanitize_segment(app_name)
    app_dir = root / app_segment
    app_dir.mkdir(parents=True, exist_ok=True)
    if filename is None:
        return app_dir
    file_segment = _sanitize_segment(filename)
    return app_dir / file_segment


def list_documents(app_name: str, pattern: str = "*") -> List[str]:
    """Return a list of document names stored for the given application."""
    if ".." in pattern:
        raise ValueError("Pattern must not contain parent directory references")
    if any(sep in pattern for sep in ("/", "\\")):
        raise ValueError("Pattern must not contain path separators")
    directory = _resolve(app_name)
    return sorted(
        entry.name for entry in directory.glob(pattern) if entry.is_file()
    )


def create_document(app_name: str, filename: str, content: str, *, encoding: str = "utf-8") -> Path:
    """Create a new document and return its path. Raise if it already exists."""
    target = _resolve(app_name, filename)
    if target.exists():
        raise FileExistsError(f"Document '{filename}' already exists in '{app_name}'")
    target.write_text(content, encoding=encoding)
    return target


def read_document(app_name: str, filename: str, *, encoding: str = "utf-8") -> str:
    """Read the content of a stored document."""
    target = _resolve(app_name, filename)
    if not target.exists():
        raise FileNotFoundError(f"Document '{filename}' not found in '{app_name}'")
    return target.read_text(encoding=encoding)


def update_document(app_name: str, filename: str, content: str, *, encoding: str = "utf-8") -> Path:
    """Overwrite an existing document with new content."""
    target = _resolve(app_name, filename)
    if not target.exists():
        raise FileNotFoundError(f"Document '{filename}' not found in '{app_name}'")
    target.write_text(content, encoding=encoding)
    return target


def delete_document(app_name: str, filename: str) -> None:
    """Delete an existing document."""
    target = _resolve(app_name, filename)
    if not target.exists():
        raise FileNotFoundError(f"Document '{filename}' not found in '{app_name}'")
    target.unlink()


__all__ = [
    "DATA_ROOT",
    "list_documents",
    "create_document",
    "read_document",
    "update_document",
    "delete_document",
]
