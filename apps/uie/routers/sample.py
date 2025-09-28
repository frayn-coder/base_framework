"""Routes for the UIE sample endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..schemas.sample import PromptDocument, QueryResponse
from ..services.sample_service import (
    extract_sample_entities,
    load_prompt_example,
    raise_sample_error,
)
from ..utils.logging import get_uie_logger

router = APIRouter(tags=["UIE Samples"])


@router.get("/query", response_model=QueryResponse)
async def query_uie(logger=Depends(get_uie_logger)) -> QueryResponse:
    logger.info("UIE 查询开始")
    result = extract_sample_entities()
    logger.info("UIE 查询完成", extra=result.dict())
    return result


@router.get("/test-error")
async def trigger_error() -> None:
    raise_sample_error()


@router.get("/data/sample", response_model=PromptDocument)
async def fetch_prompt(logger=Depends(get_uie_logger)) -> PromptDocument:
    try:
        document = load_prompt_example()
    except FileNotFoundError as exc:  # pragma: no cover
        logger.warning("UIE 示例 prompt 不存在", extra={"filename": "example_prompt.json"})
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    logger.info("返回 UIE 示例 prompt")
    return document
