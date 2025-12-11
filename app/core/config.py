from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    """
    project_name: str = "Multi-Agent RAG"
    api_prefix: str = "/api"
    app_name: str = "Multi-Agent RAG System"
    debug: bool = False

    # SQLAlchemy/Postgres connection string.
    # Example: postgresql+psycopg2://raguser:ragpassword@localhost:5432/ragdb
    database_url: str = (
        "postgresql+psycopg2://raguser:ragpassword@localhost:5432/ragdb"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
