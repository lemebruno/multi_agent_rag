from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import Quotation, QuotationEmbedding


def create_quotation(
    db: Session,
    *,
    supplier: str,
    raw_text: str,
    structured_json: Optional[dict] = None,
) -> Quotation:
    """
    Create and persist a new quotation record.
    """
    quotation = Quotation(
        supplier=supplier,
        raw_text=raw_text,
        structured_json=structured_json,
    )
    db.add(quotation)
    db.commit()
    db.refresh(quotation)
    return quotation


def get_quotation_by_id(db: Session, quotation_id: int) -> Optional[Quotation]:
    """
    Retrieve a single quotation by its primary key.
    """
    return db.query(Quotation).filter(Quotation.id == quotation_id).first()


def list_quotations(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[Quotation]:
    """
    List quotations ordered by creation time (newest first).
    """
    return (
        db.query(Quotation)
        .order_by(Quotation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def upsert_quotation_embedding(
    db: Session,
    *,
    quotation_id: int,
    embedding: List[float],
) -> QuotationEmbedding:
    """
    Insert or update the embedding associated with a quotation.
    """
    obj = (
        db.query(QuotationEmbedding)
        .filter(QuotationEmbedding.quotation_id == quotation_id)
        .first()
    )

    if obj is None:
        obj = QuotationEmbedding(
            quotation_id=quotation_id,
            embedding=embedding,
        )
        db.add(obj)
    else:
        obj.embedding = embedding

    db.commit()
    db.refresh(obj)
    return obj
