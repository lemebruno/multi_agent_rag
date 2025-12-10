from pydantic import BaseModel


class Settings(BaseModel):
    project_name: str = "Multi-Agent RAG API"
    api_prefix: str = "/api"


settings = Settings()
