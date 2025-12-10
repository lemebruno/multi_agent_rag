from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from pgvector.sqlalchemy import VECTOR


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Quotation(Base):
    """
    Represents a supplier quotation parsed from an input document.
    This table stores both the raw text and the structured representation.
    """

    __tablename__ = "quotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    supplier: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    embedding: Mapped[Optional["QuotationEmbedding"]] = relationship(
        back_populates="quotation",
        uselist=False,
        cascade="all, delete-orphan",
    )


class QuotationEmbedding(Base):
    """
    Stores the vector embedding for a quotation.
    Separated into its own table to keep the main entity lean.
    """

    __tablename__ = "quotation_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quotation_id: Mapped[int] = mapped_column(
        ForeignKey("quotations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    # Adjust the dimension to match your embedding model (e.g. 1536 for many OpenAI models)
    embedding: Mapped[List[float]] = mapped_column(VECTOR(1536), nullable=False)

    quotation: Mapped[Quotation] = relationship(
        back_populates="embedding",
    )
