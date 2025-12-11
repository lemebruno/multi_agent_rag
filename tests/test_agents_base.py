
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Sequence

from app.agents.base import (
    EvaluatorAgentProtocol,
    ExtractorAgentProtocol,
    RetrieverAgentProtocol,
)
from app.core.schemas import (
    EvaluationResult,
    QueryRequest,
    QuotationUploadRequest,
    StructuredQuotation,
)


class DummyExtractorAgent:
    def extract_structured_fields(
        self,
        upload_request: QuotationUploadRequest,
    ) -> Dict[str, Any]:
        return {
            "supplier": upload_request.supplier,
            "length": len(upload_request.raw_text),
        }


class DummyRetrieverAgent:
    def retrieve(
        self,
        query: QueryRequest,
    ) -> Sequence[StructuredQuotation]:
        quotation = StructuredQuotation(
            id=1,
            supplier="ACME Corp",
            raw_text="Dummy quotation",
            structured_json={"query": query.query},
            created_at=datetime.utcnow(),
        )
        return [quotation]


class DummyEvaluatorAgent:
    def evaluate(
        self,
        query: QueryRequest,
        answer: str,
        context: Sequence[StructuredQuotation],
    ) -> EvaluationResult:
        return EvaluationResult(
            query=query.query,
            answer=answer,
            is_answer_grounded=bool(context),
            relevance_score=0.8,
            reasoning="Dummy evaluation result.",
        )


def test_dummy_extractor_conforms_to_protocol() -> None:
    extractor: ExtractorAgentProtocol = DummyExtractorAgent()
    upload = QuotationUploadRequest(
        supplier="ACME Corp",
        raw_text="Sample text",
    )

    structured = extractor.extract_structured_fields(upload)

    assert "supplier" in structured
    assert structured["supplier"] == "ACME Corp"


def test_dummy_retriever_conforms_to_protocol() -> None:
    retriever: RetrieverAgentProtocol = DummyRetrieverAgent()
    query = QueryRequest(query="Test query")

    results = retriever.retrieve(query)

    assert len(results) == 1
    assert results[0].supplier == "ACME Corp"


def test_dummy_evaluator_conforms_to_protocol() -> None:
    evaluator: EvaluatorAgentProtocol = DummyEvaluatorAgent()
    query = QueryRequest(query="Test query")
    context = DummyRetrieverAgent().retrieve(query)

    result = evaluator.evaluate(
        query=query,
        answer="Test answer",
        context=context,
    )

    assert result.is_answer_grounded is True
    assert result.relevance_score == 0.8
