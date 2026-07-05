# SentinelAI — Backend

AI-powered Security Investigation Assistant — backend foundation (MVP).

This repository currently contains **only the backend foundation**:
project structure, configuration, database wiring, logging, and a
`/health` endpoint. No authentication, AI, or detection logic has been
implemented yet — those will be built on top of this foundation.

---

## Tech Stack

- Python 3.12
- FastAPI
- Uvicorn
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Pydantic Settings
- python-dotenv

---

## Folder Structure

```
sentinelai-backend/
├── app/
│   ├── main.py                     # FastAPI app entrypoint
│   ├── core/
│   │   ├── config.py                # Environment-based settings (Pydantic Settings)
│   │   └── logging_config.py        # Centralized logging setup
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy declarative Base (all models inherit from this)
│   │   └── session.py               # DB engine, session factory, get_db() dependency
│   └── api/
│       └── v1/
│           ├── router.py            # Aggregates all v1 endpoint routers
│           └── endpoints/
│               └── health.py        # /health endpoint
├── alembic/
│   ├── env.py                       # Alembic runtime config (wired to app settings + Base)
│   ├── script.py.mako                # Template used when generating new migrations
│   └── versions/                     # Generated migration files land here
├── alembic.ini                      # Alembic configuration
├── requirements.txt                 # Pinned Python dependencies
├── .env.example                     # Template for environment variables
├── .gitignore
└── README.md
```

### Why each folder exists

- **`app/`** — All application source code lives here, separate from
  config files like `alembic.ini` or `requirements.txt` at the repo root.

- **`app/core/`** — Cross-cutting concerns that every part of the app
  relies on: settings and logging. Kept separate from business logic
  so it's obvious where "how the app is configured" lives.

- **`app/db/`** — Everything related to the database connection itself
  (engine, sessions, declarative base). This is deliberately separate
  from `app/models/` (not created yet) so that connection/setup logic
  doesn't get mixed with table definitions once models are added.

- **`app/api/v1/`** — API routes, versioned from day one. Starting with
  `/api/v1/...` now avoids a painful breaking-change migration later
  when a `v2` is eventually needed. `endpoints/` holds one file per
  resource (e.g. `health.py`, later `cases.py`, `alerts.py`, etc.), and
  `router.py` aggregates them so `main.py` stays a thin entrypoint.

- **`alembic/`** — Database migration scripts. Kept at the project root
  (standard Alembic convention) and wired directly into `app.core.config`
  and `app.db.base`, so there is exactly one source of truth for DB
  credentials and one source of truth for model metadata.

- **`requirements.txt`** — Pinned, exact dependency versions for
  reproducible installs (no ranges, no surprises between environments).

- **`.env.example`** — Documents every environment variable the app
  needs, without exposing real secrets. Developers copy this to `.env`.

> Folders like `app/models/`, `app/schemas/`, and `app/services/` are
> intentionally **not created yet** — they'll be added when actual
> business features (users, cases, detections, etc.) are implemented,
> per the MVP scope of this task.

---

## Setup Instructions

### 1. Prerequisites

- Python 3.12 installed
- PostgreSQL running locally (or accessible remotely)
- `pip` and `venv` available

### 2. Clone and enter the project

```bash
cd sentinelai-backend
```

### 3. Create and activate a virtual environment

```bash
python3.12 -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Then edit `.env` with your actual PostgreSQL credentials:

```
POSTGRES_USER=sentinel_user
POSTGRES_PASSWORD=sentinel_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sentinelai_db
```

### 6. Create the PostgreSQL database

Make sure a database matching `POSTGRES_DB` exists, e.g.:

```bash
psql -U postgres -c "CREATE DATABASE sentinelai_db;"
```

### 7. Run Alembic migrations

There are no models yet, so this step simply confirms Alembic can
connect to the database. Once models are added, this is how you'd
apply schema changes:

```bash
alembic upgrade head
```

To generate a new migration after adding models later:

```bash
alembic revision --autogenerate -m "add users table"
alembic upgrade head
```

### 8. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### 9. Verify it's working

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`

---

## What's Intentionally NOT Included Yet

Per project scope, this foundation deliberately excludes:

- Authentication / authorization
- AI / ML integration
- Detection or investigation business logic
- Database models beyond the empty declarative `Base`
- Tests

These will be added in later stages, on top of this foundation.
