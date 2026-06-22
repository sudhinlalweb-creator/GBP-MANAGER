# Neon Database Setup

## Goal

Use Neon Postgres for staging and production while preserving local Docker Postgres for development.

## Current Behavior

The backend now supports both modes:

- local development via `POSTGRES_*`
- hosted Postgres via `DATABASE_URL`

If `DATABASE_URL` is set, the backend uses it instead of the local `POSTGRES_*` values.

## Environment Variables

Add these to your environment when using Neon:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require
ALEMBIC_DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require
```

Notes:

- `DATABASE_URL` is used by the FastAPI app and workers
- `ALEMBIC_DATABASE_URL` is used by Alembic migrations
- if `ALEMBIC_DATABASE_URL` is omitted, Alembic falls back to `DATABASE_URL`
- the app normalizes Neon Postgres URLs for `asyncpg` automatically

## Local Development

For local Docker Postgres, leave both values empty:

```env
DATABASE_URL=
ALEMBIC_DATABASE_URL=
```

In that case the backend uses:

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

## Alembic Setup

Alembic is now initialized under:

- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/`

## Migration Commands

Run these from `backend/`:

### Create a migration

```bash
alembic revision --autogenerate -m "create initial schema"
```

### Apply migrations

```bash
alembic upgrade head
```

### Roll back one migration

```bash
alembic downgrade -1
```

## Recommended Neon Flow

1. Create a Neon project and database
2. Copy the connection string
3. Set:

   ```env
   DATABASE_URL=postgresql://...?...sslmode=require
   ALEMBIC_DATABASE_URL=postgresql://...?...sslmode=require
   ```

4. Run:

   ```bash
   cd backend
   alembic upgrade head
   ```

5. Set the same database values in your backend deployment platform

## Important Limitation

Alembic is now configured, but the project does not yet include a committed initial migration file.

That means the next real step is:

```bash
cd backend
alembic revision --autogenerate -m "create initial schema"
```

Then review that migration before applying it to Neon.
