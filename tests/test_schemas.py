
from datetime import datetime
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from app.core.schemas import (
    EvaluationResult,
    QueryRequest,
    QuotationUploadRequest,
    StructuredQuotation,
)


def test_quotation_upload_request_defaults_metadata() -> None:
    upload = QuotationUploadRequest(
        supplier="ACME Corp",
        raw_text="Sample quotation text.",
    )

    assert upload.supplier == "ACME Corp"
    assert upload.raw_text == "Sample quotation text."
    assert upload.metadata == {}


def test_query_request_default_top_k() -> None:
    query = QueryRequest(query="What is the latest price?")

    assert query.query == "What is the latest price?"
    assert query.top_k == 5
    assert isinstance(query.filters, dict)


def test_query_request_invalid_top_k_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        QueryRequest(query="invalid top_k", top_k=0)


def test_structured_quotation_basic_fields() -> None:
    data: Dict[str, Any] = {
        "id": 1,
        "supplier": "ACME Corp",
        "raw_text": "Raw quotation text",
        "structured_json": {"total": 123.45},
        "created_at": datetime.utcnow(),
    }

    quotation = StructuredQuotation(**data)

    assert quotation.id == 1
    assert quotation.supplier == "ACME Corp"
    assert quotation.structured_json == {"total": 123.45}


def test_evaluation_result_score_range() -> None:
    result = EvaluationResult(
        query="What is the total?",
        answer="The total is 123.45.",
        is_answer_grounded=True,
        relevance_score=0.9,
    )

    assert 0.0 <= result.relevance_score <= 1.0
    assert result.is_answer_grounded is True
