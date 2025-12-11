
from __future__ import annotations

from typing import Any, Dict, Protocol, Sequence, runtime_checkable

from app.core.schemas import (
    EvaluationResult,
    QueryRequest,
    QuotationUploadRequest,
    StructuredQuotation,
)


@runtime_checkable
class ExtractorAgentProtocol(Protocol):
    """Agent responsible for extracting structured information from a quotation."""

    def extract_structured_fields(
        self,
        upload_request: QuotationUploadRequest,
    ) -> Dict[str, Any]:
        """Return structured fields to be stored as the quotation structured_json."""
        


@runtime_checkable
class RetrieverAgentProtocol(Protocol):
    """Agent responsible for retrieving relevant quotations for a given query."""

    def retrieve(
        self,
        query: QueryRequest,
    ) -> Sequence[StructuredQuotation]:
        """Return a ranked sequence of quotations relevant to the query."""
        ...


@runtime_checkable
class EvaluatorAgentProtocol(Protocol):
    """Agent responsible for evaluating an answer against supporting quotations."""

    def evaluate(
        self,
        query: QueryRequest,
        answer: str,
        context: Sequence[StructuredQuotation],
    ) -> EvaluationResult:
        """Return an evaluation result for the given answer and context."""
        ...
