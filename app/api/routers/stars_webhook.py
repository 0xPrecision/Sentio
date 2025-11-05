from __future__ import annotations
from fastapi import APIRouter
from app.providers.stars.webhook import router as stars_router

router = APIRouter()
router.include_router(stars_router)
