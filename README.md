# Booking SaaS

Python 3.13 · aiogram 3.x · FastAPI · SQLAlchemy 2.x (async) · Alembic · Redis · Dramatiq · APScheduler · Docker/Compose · GitHub Actions · Postgres 15+

## Quick start (dev)

```bash
cp .env.example .env
docker compose -f docker/compose.yml up --build
```

## Migrations
```bash
docker compose -f docker/compose.yml run --rm api alembic upgrade head
```

## Create tenant & deep-link
```bash
python app/ops/scripts/create_tenant.py --slug barber-1 --plan starter
python app/ops/scripts/gen_deeplink.py --slug barber-1
# t.me/<BOT>?start=tn-barber-1
```

## Milestone: Stars + Booking core + Admin lite

### Stars webhook
- POST `/stars/webhook` exposed publicly.
- Signature header: `X-Stars-Signature` (placeholder). TODO(api): confirm exact header and scheme.
- Idempotency: Redis key `stars:{event}:{external_id}`; duplicates return `200 {"duplicate": true}`.

### Booking engine
- Slot materializer actor: `materialize_slots` (45-day horizon).
- Book/reschedule uses `SELECT .. FOR UPDATE` to prevent double booking.

### Reminders & Dunning
- Reminder actor `send_reminder(tenant, appt, phase)` with key `notif:{tenant}:{appt}:{phase}`.
- Dunning: Day0/3/7 notify; Day10 set `tenant.plan_status=past_due` to disable writes/public booking.

### Admin lite
- Endpoints: `/admin/services`, `/admin/subscription` (use `?tenant=<slug>`).
- Write requests blocked when `plan_status in {past_due,canceled}` via HTTP 402.

## CI/CD
- CI builds and pushes images to GHCR on main.
- CD (tag push or manual) SSH → pull → up → `alembic upgrade head` → `/healthz` smoke.
