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

    This keeps the script idempotent so it can be run multiple times
    without polluting the main tables with duplicated test data.
    """
    # First delete embeddings linked to our demo quotations
    (
        db.query(QuotationEmbedding)
        .join(Quotation, QuotationEmbedding.quotation_id == Quotation.id)
        .filter(Quotation.supplier == DEMO_SUPPLIER)
        .delete(synchronize_session=False)
    )

    # Then delete the quotations themselves
    (
        db.query(Quotation)
        .filter(Quotation.supplier == DEMO_SUPPLIER)
        .delete(synchronize_session=False)
    )

    db.commit()


def _seed_demo_quotations(db: Session) -> List[Quotation]:
    """
    Insert a small set of demo quotations and generate their embeddings.

    We store both the raw_text and a simple structured_json payload so we
    can see what comes back from the retriever.
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


def _run_single_query(db: Session, query_text: str, top_k: int = 3) -> None:
    """
    Run a single query through the RetrieverAgent and print the results.
    """
    retriever = RetrieverAgent(db=db)

    request = QueryRequest(
        query=query_text,
        top_k=top_k,
        filters={},
    )

    print("=" * 80)
    print(f"Query: {request.query!r}")
    print("-" * 80)

    results = retriever.retrieve(request)

    if not results:
        print("No quotations found.")
        return

    for idx, quotation in enumerate(results, start=1):
        print(f"[{idx}] Quotation ID: {quotation.id}")
        print(f"    Supplier      : {quotation.supplier}")
        print(f"    Created at    : {quotation.created_at}")
        print("    Structured JSON:")
        print(f"        {quotation.structured_json}")
        print("    Raw text:")
        print(f"        {quotation.raw_text}")
        print("-" * 80)


def main() -> None:
    """
    Seed demo quotations, then run a few example queries using RetrieverAgent.

    Usage:
        python -m scripts.test_retriever_agent
    """
    db = SessionLocal()
    try:
        print("Clearing previous demo data...")
        _clear_demo_data(db)

        print("Seeding demo quotations...")
        quotations = _seed_demo_quotations(db)
        print(f"Inserted {len(quotations)} demo quotations.")

        # Example queries covering different aspects of the demo data
        _run_single_query(
            db,
            query_text="monthly cost for cloud infrastructure and virtual machines",
        )
        _run_single_query(
            db,
            query_text="annual software license for analytics platform",
        )
        _run_single_query(
            db,
            query_text="network hardware for new office, switches and firewalls",
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
