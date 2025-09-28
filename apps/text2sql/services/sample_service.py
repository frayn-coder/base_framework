"""Business helpers for the Text2SQL sample routes."""
from __future__ import annotations

from apps.common import read_document

from ..schemas.sample import PromptDocument, QueryResponse


def generate_sample_sql() -> QueryResponse:
    return QueryResponse(sql="SELECT * FROM sales LIMIT 10;")


def load_prompt_example() -> PromptDocument:
    content = read_document("text2sql", "example_prompt.sql")
    return PromptDocument(filename="example_prompt.sql", content=content)


def raise_sample_error() -> None:
    raise ValueError("模拟业务异常")
