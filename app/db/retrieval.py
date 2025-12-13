from __future__ import annotations

from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Quotation, QuotationEmbedding


def get_similar_quotations(
    db: Session,
    embedding: Sequence[float],
    limit: int = 5,
    supplier: Optional[str] = None,
) -> List[Quotation]:
    """
    Return quotations ordered by vector similarity to the given embedding.

    This function uses the pgvector `<->` operator through SQLAlchemy's
    generic `op` interface. It assumes that:
    - quotation_embeddings.embedding is a pgvector column
    - quotation_embeddings.quotation_id references quotations.id
    - optionally filters by supplier when provided
    """
    distance_expr = QuotationEmbedding.embedding.op("<->")(embedding)

    stmt = (
        select(Quotation)
        .join(
            QuotationEmbedding,
            QuotationEmbedding.quotation_id == Quotation.id,
        )
    )

    if supplier:
        stmt = stmt.where(Quotation.supplier == supplier)

    stmt = stmt.order_by(distance_expr).limit(limit)

    result = db.execute(stmt)
    return list(result.scalars().all())
