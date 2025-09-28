"""Schemas for the UIE sample routes."""
from __future__ import annotations

from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    entities: list[str] = Field(..., description="模拟抽取的实体列表")


class PromptDocument(BaseModel):
    filename: str = Field(..., description="示例文件名")
    content: str = Field(..., description="示例文件内容")
