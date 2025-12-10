
from __future__ import annotations

from typing import List

from app.db.session import SessionLocal
from app.db.repositories import (
    create_quotation,
    get_quotation_by_id,
    upsert_quotation_embedding,
)


def build_dummy_embedding(dim: int = 1536) -> List[float]:
    """
    Build a simple dummy embedding vector for testing purposes.
    """
    return [0.0] * dim


def main() -> None:
    """
    Simple smoke test for the database connection and repositories.

    Steps:
    1. Open a database session.
    2. Create a new quotation.
    3. Fetch the quotation by ID.
    4. Create or update a vector embedding for this quotation.
    """
    db = SessionLocal()

    try:
        print("Creating a new quotation...")
        quotation = create_quotation(
            db,
            supplier="Test Supplier",
            raw_text="This is a test quotation from the DB smoke test.",
            structured_json={"example": True, "total": 123.45},
        )
        print(f"Created quotation with id={quotation.id}")

        print("Fetching quotation by id...")
        fetched = get_quotation_by_id(db, quotation.id)
        if fetched is None:
            raise RuntimeError("Failed to fetch quotation by id.")

        print(
            f"Fetched quotation: id={fetched.id}, "
            f"supplier={fetched.supplier}, "
            f"created_at={fetched.created_at}"
        )

        print("Upserting dummy embedding...")
        embedding = build_dummy_embedding()
        embedding_obj = upsert_quotation_embedding(
            db,
            quotation_id=fetched.id,
            embedding=embedding,
        )
        print(
            "Embedding stored with id="
            f"{embedding_obj.id} for quotation_id={embedding_obj.quotation_id}"
        )

        print("DB smoke test completed successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
