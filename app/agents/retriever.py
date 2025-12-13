from __future__ import annotations

from typing import Sequence

from sqlalchemy.orm import Session

from app.agents.base import RetrieverAgentProtocol
from app.core.embeddings import embed_text
from app.core.schemas import QueryRequest, StructuredQuotation
from app.db.retrieval import get_similar_quotations


class RetrieverAgent(RetrieverAgentProtocol):
    """
    Agent responsible for retrieving quotations using vector similarity search.

    This implementation:
    - embeds the natural language query,
    - runs a pgvector similarity search in Postgres,
    - returns the top-k quotations as StructuredQuotation objects.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the retriever with an existing database session.

        The caller is responsible for managing the session lifecycle
        (opening, committing/rolling back, and closing).
        """
        self._db = db

    def retrieve(self, query: QueryRequest) -> Sequence[StructuredQuotation]:
        """
        Retrieve a ranked sequence of quotations relevant to the given query.

        Currently this method:
        - uses query.query as the text to embed,
        - uses query.top_k as the maximum number of results,
        - optionally filters by supplier via query.filters["supplier"].
        """
        query_text = query.query.strip()
        if not query_text:
            return []

        embedding_vector = embed_text(query_text)
        top_k = query.top_k

        supplier_filter = None
        if query.filters:
            raw_supplier = query.filters.get("supplier")
            if isinstance(raw_supplier, str):
                cleaned = raw_supplier.strip()
                if cleaned:
                    supplier_filter = cleaned

        quotations = get_similar_quotations(
            db=self._db,
            embedding=embedding_vector,
            limit=top_k,
            supplier=supplier_filter,
        )

        return [StructuredQuotation.from_orm(q) for q in quotations]
