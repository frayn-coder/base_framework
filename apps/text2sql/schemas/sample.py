"""Schemas for the Text2SQL sample routes."""
from __future__ import annotations

from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    sql: str = Field(..., description="示例 SQL 语句")


class PromptDocument(BaseModel):
    filename: str = Field(..., description="示例文件名")
    content: str = Field(..., description="示例文件内容")
