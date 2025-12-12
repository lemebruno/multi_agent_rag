from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class QuotationItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total_price: float


class StructuredQuotation(BaseModel):
    """
    Structured representation of a quotation extracted from raw text.

    This model will be stored as JSON in the database and used by
    other agents in the system.
    """

    raw_text: str

    title: Optional[str] = None
    customer_name: Optional[str] = None
    vendor_name: Optional[str] = None

    items: List[QuotationItem] = []
    subtotal: Optional[float] = None
    taxes: Optional[float] = None
    total: Optional[float] = None
    currency: Optional[str] = None
