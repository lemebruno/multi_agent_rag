from __future__ import annotations

from typing import List, Sequence

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
        - ignores query.filters (reserved for future extensions).
        """
        query_text = query.query.strip()
        if not query_text:
            return []

        embedding_vector = embed_text(query_text)
        top_k = query.top_k

        quotations = get_similar_quotations(
            db=self._db,
            embedding=embedding_vector,
            limit=top_k,
        )

        return [StructuredQuotation.from_orm(q) for q in quotations]
