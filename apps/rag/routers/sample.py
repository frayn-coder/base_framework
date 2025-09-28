"""Routes exposing the RAG sample functionality."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..schemas.sample import PerformanceResponse, PromptDocument, QueryResponse
from ..services.sample_service import (
    load_prompt_example,
    raise_sample_error,
    run_sample_query,
    simulate_workload,
)
from ..utils.logging import get_rag_logger

router = APIRouter(tags=["RAG Samples"])


@router.get("/query", response_model=QueryResponse)
async def query_rag(logger=Depends(get_rag_logger)) -> QueryResponse:
    """Return a canned response to demonstrate the query flow."""
    logger.info("RAG 查询业务开始执行")
    result = run_sample_query()
    logger.info("RAG 查询结果已生成", extra=result.dict())
    return result


@router.get("/test-error")
async def trigger_error() -> None:
    """Raise an exception to exercise the unified error handling."""
    raise_sample_error()


@router.get("/test-perf", response_model=PerformanceResponse)
async def measure_performance(logger=Depends(get_rag_logger)) -> PerformanceResponse:
    """Simulate a workload and return the measured latency."""
    result = simulate_workload()
    logger.info("性能测试完成", extra=result.dict())
    return result


@router.get("/data/sample", response_model=PromptDocument)
async def fetch_prompt(logger=Depends(get_rag_logger)) -> PromptDocument:
    """Serve the prompt example stored under the shared data directory."""
    try:
        document = load_prompt_example()
    except FileNotFoundError as exc:  # pragma: no cover - defensive branch
        logger.warning("示例 prompt 不存在", extra={"filename": "example_prompt.txt"})
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    logger.info("返回 RAG 示例 prompt")
    return document
