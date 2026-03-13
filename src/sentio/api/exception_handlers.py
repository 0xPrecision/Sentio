from fastapi import Request
from fastapi.responses import JSONResponse

from sentio.core.exceptions import NotFoundError, ConflictError


async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )
