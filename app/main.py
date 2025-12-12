from app.api.routes import health, upload
from app.core.config import settings
from fastapi import FastAPI


def create_app() -> FastAPI:
    """
    Application factory function.

    Using a factory makes it easier to:
    - Configure the app differently for tests vs production.
    - Inject dependencies and middlewares in a single place.
    """
    app = FastAPI(title=settings.project_name)

    # Include routers
    app.include_router(health.router, prefix=settings.api_prefix)
    app.include_router(upload.router, prefix=settings.api_prefix)

    return app


# This is the ASGI application object that Uvicorn will use.
app = create_app()
