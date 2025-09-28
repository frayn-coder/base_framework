"""Business helpers for the UIE sample routes."""
from __future__ import annotations

from apps.common import read_document

from ..schemas.sample import PromptDocument, QueryResponse


def extract_sample_entities() -> QueryResponse:
    return QueryResponse(entities=["人名", "时间", "地点"])


def load_prompt_example() -> PromptDocument:
    content = read_document("uie", "example_prompt.json")
    return PromptDocument(filename="example_prompt.json", content=content)


def raise_sample_error() -> None:
    raise RuntimeError("模拟抽取失败")
