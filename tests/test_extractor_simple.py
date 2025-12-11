from app.agents.extractor_simple import SimpleExtractorAgent
from app.core.schemas import QuotationUploadRequest


def test_simple_extractor_basic_fields() -> None:
    upload = QuotationUploadRequest(
        supplier="ACME Corp",
        raw_text="Some quotation text.",
        filename="quote_001.pdf",
    )
    agent = SimpleExtractorAgent()

    result = agent.extract_structured_fields(upload)

    assert result["supplier"] == "ACME Corp"
    assert result["raw_text_length"] == len(upload.raw_text)
    assert result["has_metadata"] is False
    assert result["filename"] == "quote_001.pdf"


def test_simple_extractor_with_metadata_flag() -> None:
    upload = QuotationUploadRequest(
        supplier="ACME Corp",
        raw_text="Another quotation text.",
        metadata={"source": "email"},
    )
    agent = SimpleExtractorAgent()

    result = agent.extract_structured_fields(upload)

    assert result["has_metadata"] is True
