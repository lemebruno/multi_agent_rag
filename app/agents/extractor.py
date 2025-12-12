from __future__ import annotations

from typing import Any, Dict

from app.agents.base import ExtractorAgentProtocol
from app.agents.extractor_simple import SimpleExtractorAgent
from app.core.schemas import QuotationUploadRequest


class ExtractorAgent(ExtractorAgentProtocol):
    """
    Production extractor agent placeholder.

    For now this agent is a thin wrapper around SimpleExtractorAgent,
    adding a few extra fields. It already implements the
    ExtractorAgentProtocol, so it can be used by the orchestrator and
    later replaced by an LLM-based implementation without changing
    the public interface.
    """

    def __init__(self) -> None:
        self._base_extractor = SimpleExtractorAgent()

    def extract_structured_fields(
        self,
        upload_request: QuotationUploadRequest,
    ) -> Dict[str, Any]:
        """
        Return structured fields that will be stored as structured_json.

        This implementation:
        - delegates basic fields to SimpleExtractorAgent;
        - adds raw_text and metadata so downstream agents have more context.
        """
        fields = self._base_extractor.extract_structured_fields(upload_request)

        # Enrich with extra context that may be useful later
        fields["raw_text"] = upload_request.raw_text
        fields["metadata"] = upload_request.metadata

        return fields
