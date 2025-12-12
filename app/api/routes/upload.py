from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.extractor import ExtractorAgent
from app.agents.orchestrator import Orchestrator
from app.core.schemas import QuotationUploadRequest, StructuredQuotation
from app.db.session import get_db

router = APIRouter()

UploadPayload = QuotationUploadRequest | List[QuotationUploadRequest]


def get_orchestrator() -> Orchestrator:
    """
    FastAPI dependency that provides an Orchestrator instance.

    For now we create it on demand with a local ExtractorAgent
    implementation. Later this can be replaced with a more complex
    wiring or dependency injection container if needed.
    """
    extractor = ExtractorAgent()
    return Orchestrator(extractor=extractor)


@router.post(
    "/upload",
    response_model=List[StructuredQuotation],
    tags=["upload"],
    summary="Upload one or more quotations and store them in the database",
)
def upload_quotations(
    payload: UploadPayload,
    db: Session = Depends(get_db),
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> List[StructuredQuotation]:
    """
    Ingest one or multiple quotations.

    Accepts either a single QuotationUploadRequest object or a list of
    them. Returns the persisted StructuredQuotation objects for each
    upload request.
    """
    if isinstance(payload, QuotationUploadRequest):
        uploads: List[QuotationUploadRequest] = [payload]
    else:
        uploads = payload

    results: List[StructuredQuotation] = []

    for upload in uploads:
        quotation = orchestrator.ingest_quotation(db=db, upload=upload)
        results.append(quotation)

    return results
