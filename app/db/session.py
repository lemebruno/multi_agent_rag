from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from pgvector.psycopg2 import register_vector


# SQLAlchemy engine: single, shared connection factory
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def register_vector_type(dbapi_connection, connection_record) -> None:
    """
    Register the pgvector type with the underlying psycopg2 connection.
    This ensures that VECTOR columns are handled correctly by SQLAlchemy.
    """
    register_vector(dbapi_connection)
# Session factory: creates Session objects bound to the engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes.
    Yields a database session and ensures it is closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()