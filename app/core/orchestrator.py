
from __future__ import annotations

from dataclasses import dataclass

from app.agents.base import (
    EvaluatorAgentProtocol,
    ExtractorAgentProtocol,
    RetrieverAgentProtocol,
)
from app.core.schemas import StructuredQuotation


@dataclass
class MultiAgentOrchestrator:
    """High-level coordinator for the multi-agent RAG workflow."""

    extractor: ExtractorAgentProtocol
    retriever: RetrieverAgentProtocol
    evaluator: EvaluatorAgentProtocol

    def ingest_quotation(self, raw_text: str) -> StructuredQuotation:
        """
        Stub method responsible for ingesting a new quotation into the system.

        In future stages this method will:
        - Build a QuotationUploadRequest with extra metadata.
        - Use the extractor agent to obtain structured fields.
        - Persist the quotation and return the stored StructuredQuotation.
        """
        raise NotImplementedError("ingest_quotation is not implemented yet.")

    def answer_query(self, query: str) -> str:
        """
        Stub method responsible for answering a user query.

        In future stages this method will:
        - Build a QueryRequest from the raw query string.
        - Use the retriever agent to fetch relevant quotations.
        - Generate an answer from retrieved quotations.
        - Evaluate the answer using the evaluator agent.
        """
        raise NotImplementedError("answer_query is not implemented yet.")
