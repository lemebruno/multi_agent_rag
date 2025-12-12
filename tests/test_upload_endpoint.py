from __future__ import annotations

from typing import List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Quotation
from app.db.session import SessionLocal
from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """
    Test client for the FastAPI application.

    Uses the same application factory as production so that routes and
    dependencies are wired in a realistic way.
    """
    app = create_app()
    return TestClient(app)


@pytest.fixture
def db_session() -> Session:
    """
    Database session used for verification in tests.

    This uses the same SessionLocal as the application, so the data
    created by the /upload endpoint is visible here.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_upload_single_quotation_persists_and_returns_structured(
    client: TestClient,
    db_session: Session,
) -> None:
    url = f"{settings.api_prefix}/upload"

    payload = {
        "supplier": "Upload Test Supplier - Single",
        "raw_text": "This is a test quotation from the /upload endpoint.",
        "filename": "upload_test_single.txt",
        "metadata": {"source": "pytest"},
    }

    response = client.post(url, json=payload)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    item = data[0]
    assert "id" in item
    assert item["supplier"] == payload["supplier"]
    assert item["raw_text"] == payload["raw_text"]
    assert isinstance(item["structured_json"], dict)

    quotation_id = item["id"]

    db_obj = db_session.query(Quotation).filter(Quotation.id == quotation_id).first()
    assert db_obj is not None
    assert db_obj.supplier == payload["supplier"]
    assert db_obj.raw_text == payload["raw_text"]
    assert isinstance(db_obj.structured_json, dict)


def test_upload_multiple_quotations_creates_multiple_records(
    client: TestClient,
    db_session: Session,
) -> None:
    url = f"{settings.api_prefix}/upload"

    payload: List[dict] = [
        {
            "supplier": "Upload Test Supplier - Batch 1",
            "raw_text": "First quotation in a batch request.",
            "filename": "batch_1.txt",
            "metadata": {"batch": 1},
        },
        {
            "supplier": "Upload Test Supplier - Batch 2",
            "raw_text": "Second quotation in a batch request.",
            "filename": "batch_2.txt",
            "metadata": {"batch": 1},
        },
    ]

    response = client.post(url, json=payload)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    ids = [item["id"] for item in data]
    assert len(set(ids)) == 2  # All ids must be distinct

    records = (
        db_session.query(Quotation)
        .filter(Quotation.id.in_(ids))
        .all()
    )

    assert len(records) == 2
    suppliers = {record.supplier for record in records}
    assert "Upload Test Supplier - Batch 1" in suppliers
    assert "Upload Test Supplier - Batch 2" in suppliers
