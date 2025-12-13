

from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from app.agents.retriever import RetrieverAgent
from app.core.embeddings import embed_text
from app.core.schemas import QueryRequest
from app.db.models import Quotation, QuotationEmbedding
from app.db.repositories import create_quotation, upsert_quotation_embedding
from app.db.session import SessionLocal


DEMO_SUPPLIER = "DEMO_SUPPLIER_RETRIEVER_TEST"


def _clear_demo_data(db: Session) -> None:
    """
    Remove demo quotations and their embeddings from the database.

    This keeps the tests idempotent so they can run multiple times
    without polluting the main tables with duplicated test data.
    """
    quotation_rows = (
        db.query(Quotation.id)
        .filter(Quotation.supplier == DEMO_SUPPLIER)
        .all()
    )

    quotation_ids = [row[0] for row in quotation_rows]

    if not quotation_ids:
        return

    (
        db.query(QuotationEmbedding)
        .filter(QuotationEmbedding.quotation_id.in_(quotation_ids))
        .delete(synchronize_session=False)
    )

    (
        db.query(Quotation)
        .filter(Quotation.id.in_(quotation_ids))
        .delete(synchronize_session=False)
    )

    db.commit()


def _seed_demo_quotations(db: Session) -> List[Quotation]:
    """
    Insert a small set of demo quotations and generate their embeddings.
    """
    demo_payloads = [
        {
            "raw_text": (
                "Cloud hosting for production environment including virtual machines, "
                "managed database and load balancer. Monthly cost estimated at 1200 EUR."
            ),
            "structured_json": {
                "category": "cloud_infrastructure",
                "currency": "EUR",
                "estimated_monthly_cost": 1200,
            },
        },
        {
            "raw_text": (
                "Annual software license for data analytics platform covering 20 users. "
                "Total quote: 8000 EUR per year, support included."
            ),
            "structured_json": {
                "category": "software_license",
                "currency": "EUR",
                "billing_period": "yearly",
                "total_cost": 8000,
            },
        },
        {
            "raw_text": (
                "Managed backup and disaster recovery service for on-premise servers. "
                "Monthly subscription of 600 EUR with 24/7 support."
            ),
            "structured_json": {
                "category": "backup_dr",
                "currency": "EUR",
                "estimated_monthly_cost": 600,
            },
        },
        {
            "raw_text": (
                "Network equipment including switches, firewalls and access points "
                "for new office location. One-time cost: 15000 EUR."
            ),
            "structured_json": {
                "category": "network_hardware",
                "currency": "EUR",
                "one_time_cost": 15000,
            },
        },
    ]

    quotations: List[Quotation] = []

    for payload in demo_payloads:
        quotation = create_quotation(
            db=db,
            supplier=DEMO_SUPPLIER,
            raw_text=payload["raw_text"],
            structured_json=payload["structured_json"],
        )

        embedding_vector = embed_text(quotation.raw_text)
        upsert_quotation_embedding(
            db=db,
            quotation_id=quotation.id,
            embedding=embedding_vector,
        )

        quotations.append(quotation)

    return quotations


def test_retriever_returns_results_for_demo_data() -> None:
    db = SessionLocal()
    try:
        _clear_demo_data(db)
        _seed_demo_quotations(db)

        retriever = RetrieverAgent(db=db)
        request = QueryRequest(
            query="cloud infrastructure and virtual machines",
            top_k=3,
            filters={"supplier": DEMO_SUPPLIER},
        )

        results = retriever.retrieve(request)

        assert results, "Retriever should return at least one result for demo data."
        assert all(
            quotation.supplier == DEMO_SUPPLIER for quotation in results
        ), "All results should belong to the demo supplier."
    finally:
        _clear_demo_data(db)
        db.close()


def test_retriever_respects_top_k_limit() -> None:
    db = SessionLocal()
    try:
        _clear_demo_data(db)
        _seed_demo_quotations(db)

        retriever = RetrieverAgent(db=db)
        request = QueryRequest(
            query="backup and disaster recovery service",
            top_k=2,
            filters={"supplier": DEMO_SUPPLIER},
        )

        results = retriever.retrieve(request)

        assert len(results) <= 2, "Retriever must not return more than top_k results."
    finally:
        _clear_demo_data(db)
        db.close()


def test_retriever_returns_empty_for_blank_query() -> None:
    db = SessionLocal()
    try:
        retriever = RetrieverAgent(db=db)
        request = QueryRequest(
            query="   ",
            top_k=5,
            filters={"supplier": DEMO_SUPPLIER},
        )

        results = retriever.retrieve(request)

        assert results == [], "Blank queries should return an empty result set."
    finally:
        db.close()
