"""Routes for the Text2SQL sample endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..schemas.sample import PromptDocument, QueryResponse
from ..services.sample_service import (
    generate_sample_sql,
    load_prompt_example,
    raise_sample_error,
)
from ..utils.logging import get_text2sql_logger

router = APIRouter(tags=["Text2SQL Samples"])


@router.get("/query", response_model=QueryResponse)
async def query_text2sql(logger=Depends(get_text2sql_logger)) -> QueryResponse:
    logger.info("Text2SQL 查询开始")
    result = generate_sample_sql()
    logger.info("生成的 SQL 已返回", extra=result.dict())
    return result


@router.get("/test-error")
async def trigger_error() -> None:
    raise_sample_error()


@router.get("/data/sample", response_model=PromptDocument)
async def fetch_prompt(logger=Depends(get_text2sql_logger)) -> PromptDocument:
    try:
        document = load_prompt_example()
    except FileNotFoundError as exc:  # pragma: no cover
        logger.warning(
            "Text2SQL 示例 prompt 不存在",
            extra={"filename": "example_prompt.sql"},
        )
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    logger.info("返回 Text2SQL 示例 prompt")
    return document
