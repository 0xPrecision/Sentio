# Sentio

Sentio is a SaaS booking platform with a Telegram bot interface for service-based businesses (e.g. barbershops, salons, studios).  
The goal is to provide a simple, flexible way for owners to manage time slots, staff schedules, and client bookings, while clients can book and manage their appointments directly in Telegram.

> Status: early development. The project is being built as a production-like training project using a modern Python backend stack.

---

## Features (planned)

- **Multi-tenant booking system**
  - Separate workspaces for different businesses
  - Staff, services, and schedules per organization

- **Time slots & scheduling**
  - Configurable working hours and breaks
  - Time slot generation per staff member
  - Basic conflict detection for bookings

- **Telegram bot for clients**
  - Browse available services and time slots
  - Create, reschedule, and cancel bookings
  - Reminders and notifications via Telegram

- **Admin API / panel**
  - Manage organizations, staff, services, schedules
  - View and manage bookings
  - Authentication & basic access control (planned)

- **Background processing (planned)**
  - Reminders
  - Cleanup tasks
  - Periodic maintenance jobs

---

## Tech stack

**Backend & API**

- Python 3.13
- FastAPI (HTTP API, OpenAPI, dependency injection)
- SQLAlchemy 2.x (async ORM / Core)
- Alembic (database migrations)
- PostgreSQL (main database)
- Redis (cache, locks, state)

**Telegram bot**

- aiogram 3.x (async Telegram bot framework)
- Integration with the HTTP API instead of direct DB access

**Infrastructure & tooling**

- Poetry (dependency & environment management)
- Docker / Docker Compose (services orchestration)
- pytest, pytest-asyncio (testing)
- httpx (HTTP client)
- black, ruff, mypy, pre-commit (code quality & linting)

CI/CD and additional tools will be added later as the project grows.

---

## Project structure (planned)

The structure will evolve, but the core idea is to keep a clear separation between API, bot, domain logic, and infrastructure:

```bash
sentio/
  sentio/
    api/        # FastAPI routes and API-related code
    bot/        # aiogram bot logic
    core/       # settings, db, logging, application wiring
    models/     # SQLAlchemy models
    schemas/    # Pydantic schemas
    services/   # domain services/use-cases (booking, scheduling, etc.)
    workers/    # background tasks (Celery/RQ, if used)
  tests/        # unit and integration tests
  docker/       # Dockerfiles, compose configs (planned)
  docs/         # documentation, design notes, task specs
  pyproject.toml
  README.md
```

This layout may change as the domain model and requirements become clearer.

---

## Getting started

### Prerequisites

- Python 3.13
- Poetry installed (`pip install poetry`)
- Docker & Docker Compose (for running Postgres/Redis, later)

### Install dependencies

From the project root:

```bash
poetry install
```

This will:

- create a virtual environment (if not present),
- install all runtime and development dependencies defined in `pyproject.toml`.

Activate the environment:

```bash
poetry shell
```

### Run basic checks

Once dependencies are installed, you can run:

```bash
# Run tests
poetry run pytest

# Lint and format checks
poetry run ruff check .
poetry run black --check .
poetry run mypy
```

These commands will be refined as the project structure and tooling configuration mature.

---

## Roadmap (high level)

1. **Core infrastructure**
   - Project layout
   - Config, logging, DB setup, migrations

2. **Domain model**
   - Organizations, staff, services
   - Schedules and time slots
   - Bookings

3. **HTTP API**
   - Basic CRUD endpoints for the core entities
   - Booking creation and validation

4. **Telegram bot**
   - Basic flow: select service → select time slot → confirm booking
   - Booking management (view/cancel)

5. **Background tasks**
   - Reminders & cleanup jobs

6. **Operational tooling**
   - Docker setup
   - CI (tests + linters)

---

## License

Currently not specified.  
The license will be added once the project is closer to a stable state.
