"""Pydantic schemas for the RAG sample endpoints."""
from __future__ import annotations

from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    """Schema returned by the sample query endpoint."""

    answer: str = Field(..., description="示例 RAG 查询结果")


class PerformanceResponse(BaseModel):
    """Schema describing a simple performance measurement."""

    duration_ms: float = Field(..., ge=0, description="模拟任务耗时 (毫秒)")


class PromptDocument(BaseModel):
    """Schema for the shared prompt examples stored under /data."""

    filename: str = Field(..., description="示例文件名")
    content: str = Field(..., description="示例文件内容")
