"""Business logic backing the RAG sample routes."""
from __future__ import annotations

import time

from apps.common import read_document

from ..schemas.sample import PerformanceResponse, PromptDocument, QueryResponse


def run_sample_query() -> QueryResponse:
    """Return a canned RAG response."""
    return QueryResponse(answer="这是 RAG 查询结果")


def simulate_workload(duration: float = 0.05) -> PerformanceResponse:
    """Sleep for *duration* seconds and report the elapsed milliseconds."""
    start = time.perf_counter()
    time.sleep(duration)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return PerformanceResponse(duration_ms=round(elapsed_ms, 2))


def load_prompt_example() -> PromptDocument:
    """Load the shared RAG prompt example from disk."""
    content = read_document("rag", "example_prompt.txt")
    return PromptDocument(filename="example_prompt.txt", content=content)


def raise_sample_error() -> None:
    """Utility used by the sample error endpoint to raise a failure."""
    raise ZeroDivisionError("模拟的 RAG 算子异常")
