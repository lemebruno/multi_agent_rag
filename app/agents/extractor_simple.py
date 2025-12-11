from __future__ import annotations

from typing import Any, Dict

from app.agents.base import ExtractorAgentProtocol
from app.core.schemas import QuotationUploadRequest


class SimpleExtractorAgent(ExtractorAgentProtocol):
    """Minimal extractor agent that produces basic structured fields.

    This implementation is intentionally simple and deterministic so it can be
    used in tests and local development before introducing an LLM-based agent.
    """

    def extract_structured_fields(
        self,
        upload_request: QuotationUploadRequest,
    ) -> Dict[str, Any]:
        """Return a small set of structured fields derived from the upload request."""
        return {
            "supplier": upload_request.supplier,
            "raw_text_length": len(upload_request.raw_text),
            "has_metadata": bool(upload_request.metadata),
            "filename": upload_request.filename,
        }
