from fastapi import FastAPI
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.api.routers.admin_services import router as admin_services
from app.api.routers.admin_subscription import router as admin_subscription
from app.api.routers.stars_webhook import router as stars_webhook

app = FastAPI(title="Booking SaaS API", version="0.2.0")

REQS = Counter("http_requests_total", "Requests", ["route", "status"])

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/readyz")
async def readyz():
    return {"ok": True}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

app.include_router(admin_services)
app.include_router(admin_subscription)
app.include_router(stars_webhook)
