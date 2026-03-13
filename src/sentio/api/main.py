from fastapi import FastAPI

from sentio.api.exception_handlers import (
    not_found_error_handler,
    conflict_error_handler,
)
from sentio.core.exceptions import NotFoundError, ConflictError
from sentio.api import get_api_router


def create_app() -> FastAPI:
    app = FastAPI(title="Sentio API")

    app.include_router(get_api_router(), prefix="/api")

    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(ConflictError, conflict_error_handler)

    return app


app = create_app()
