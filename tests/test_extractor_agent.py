from __future__ import annotations

from app.agents.extractor import ExtractorAgent
from app.core.schemas import QuotationUploadRequest


def test_extractor_agent_basic_enrichment() -> None:
    upload = QuotationUploadRequest(
        supplier="ACME Corp",
        raw_text="Sample quotation text.",
        filename="quote_123.pdf",
    )

    agent = ExtractorAgent()
    result = agent.extract_structured_fields(upload)

    # Fields coming from SimpleExtractorAgent
    assert result["supplier"] == "ACME Corp"
    assert result["raw_text_length"] == len(upload.raw_text)
    assert result["has_metadata"] is False
    assert result["filename"] == "quote_123.pdf"

    # Extra enrichment from ExtractorAgent
    assert result["raw_text"] == upload.raw_text
    assert result["metadata"] == {}


def test_extractor_agent_with_metadata_and_multiline_text() -> None:
    raw_text = "Line one\nLine two with Total: 100.00\nLine three"

    upload = QuotationUploadRequest(
        supplier="PDF Supplier",
        raw_text=raw_text,
        metadata={"source": "pdf"},
    )

    agent = ExtractorAgent()
    result = agent.extract_structured_fields(upload)

    # The agent should keep the raw text intact and flag metadata correctly
    assert result["raw_text"] == raw_text
    assert result["raw_text_length"] == len(raw_text)
    assert result["has_metadata"] is True
    assert result["metadata"] == {"source": "pdf"}
