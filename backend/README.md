# Backend

Backend API service (FastAPI + PostgreSQL) managed with `uv`.

## Requirements

- `uv`
- PostgreSQL (local or remote)

## Setup

From the `backend` directory:

1. Install dependencies:
```sh
   uv sync
```

2. Create `.env`:
```sh
   cp examples/.env.example .env
```

   Then edit `.env` (set `DATABASE_URL` and other required values).

## Database Migrations

Apply migrations:
```sh
uv run alembic upgrade head
```

## Create Default Admin
```sh
uv run -m scripts.init_admin --email admin@example.com --prompt-password
```
## Run the Server
```sh
uv run uvicorn app.main:app --host 0.0.0.0
```
Server will be available at http://0.0.0.0:8000 (docs usually at /docs).