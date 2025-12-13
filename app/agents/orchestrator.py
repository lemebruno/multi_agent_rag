from __future__ import annotations

from sqlalchemy.orm import Session

from app.agents.base import ExtractorAgentProtocol
from app.core.embeddings import embed_text
from app.core.schemas import QuotationUploadRequest, StructuredQuotation
from app.db.repositories import create_quotation, upsert_quotation_embedding


class Orchestrator:
    """
    High-level orchestration layer for the Multi-Agent RAG system.

    In this stage we implement quotation ingestion and embedding generation.
    Later this class can be extended with retrieval and evaluation flows.
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
        3. Generate an embedding for the quotation text.
        4. Upsert the embedding into the quotation_embeddings table.
        5. Return a StructuredQuotation schema built from the ORM object.
        """
        structured_fields = self._extractor.extract_structured_fields(upload)

        quotation = create_quotation(
            db=db,
            supplier=upload.supplier,
            raw_text=upload.raw_text,
            structured_json=structured_fields,
        )

        embedding_vector = embed_text(upload.raw_text)
        upsert_quotation_embedding(
            db=db,
            quotation_id=quotation.id,
            embedding=embedding_vector,
        )

        return StructuredQuotation.from_orm(quotation)
