from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.agents.base import ExtractorAgentProtocol
from app.core.schemas import QuotationUploadRequest, StructuredQuotation
from app.db.models import Quotation


class Orchestrator:
    """
    High-level orchestration layer for the Multi-Agent RAG system.

    In this stage we only implement quotation ingestion. Later this
    class can be extended with retrieval and evaluation flows.
    """

    def __init__(self, extractor: ExtractorAgentProtocol) -> None:
        self._extractor = extractor

    def ingest_quotation(
        self,
        db: Session,
        upload: QuotationUploadRequest,
    ) -> StructuredQuotation:
        """
        Ingest a new quotation into the system.

        Steps:
        1. Use the extractor agent to build structured fields.
        2. Persist a Quotation row with raw_text + structured_json.
        3. Return a StructuredQuotation schema built from the ORM object.
        """
        structured_fields = self._extractor.extract_structured_fields(upload)

        quotation = Quotation(
            supplier=upload.supplier,
            raw_text=upload.raw_text,
            structured_json=structured_fields,
        )

        db.add(quotation)
        db.commit()
        db.refresh(quotation)

        return StructuredQuotation.from_orm(quotation)
