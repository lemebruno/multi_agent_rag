
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class QuotationUploadRequest(BaseModel):
    """Payload used when a client uploads a new quotation."""

    supplier: str = Field(
        ...,
        description="Supplier or vendor name associated with the quotation.",
    )
    raw_text: str = Field(
        ...,
        description="Full raw text extracted from the quotation document.",
    )
    filename: Optional[str] = Field(
        default=None,
        description="Optional original filename for traceability.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata such as source channel, user id, etc.",
    )

    class Config:
        extra = "forbid"


class StructuredQuotation(BaseModel):
    """Normalized representation of a quotation stored in the system."""

    id: int = Field(
        ...,
        description="Database identifier of the quotation.",
    )
    supplier: str = Field(
        ...,
        description="Supplier or vendor name.",
    )
    raw_text: str = Field(
        ...,
        description="Original quotation text.",
    )
    structured_json: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured fields extracted from the quotation.",
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp in the database.",
    )

    class Config:
        extra = "forbid"
        orm_mode = True


class QueryRequest(BaseModel):
    """Query payload used by the retrieval/orchestration layer."""

    query: str = Field(
        ...,
        description="Natural language query from the user.",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of candidates to retrieve.",
    )
    filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional structured filters like supplier, date range, etc.",
    )

    class Config:
        extra = "forbid"


class EvaluationResult(BaseModel):
    """Result returned by an evaluator agent after checking an answer."""

    query: str = Field(
        ...,
        description="Original user query.",
    )
    answer: str = Field(
        ...,
        description="Answer that was evaluated.",
    )
    is_answer_grounded: bool = Field(
        ...,
        description="Whether the answer is grounded in retrieved quotations.",
    )
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall relevance score between 0 and 1.",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Free-form explanation describing why the score was assigned.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional evaluation details or per-criterion scores.",
    )

    class Config:
        extra = "forbid"
