# Backend Deployment

## Goal

Automate backend deployments for the FastAPI API and Celery worker after stage releases are pushed to GitHub.

## Recommended Platform

Use a container-native platform such as Render for the backend stack:

- FastAPI API as a web service
- Celery worker as a background worker service
- PostgreSQL as a managed database
- Redis as a managed Redis instance

This keeps the frontend on Vercel and the backend on infrastructure that supports long-running workers.

## Files Added

- `.github/workflows/backend-render-deploy.yml`
- `render.yaml`

## Production Container Behavior

The backend Docker image now runs in production mode by default:

- `docker/backend/Dockerfile` starts `uvicorn` without `--reload`
- `docker/backend/entrypoint.sh` runs `alembic upgrade head` before the API starts
- `docker-compose.yml` overrides the backend command for local development and still enables `--reload`

## Render Service Setup

The repo now includes a Render Blueprint at [render.yaml](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/render.yaml).

The blueprint defines:

- one API web service
- one Celery worker service
- one Render key-value instance for Redis/Celery

The blueprint expects Postgres to remain on Neon via external `DATABASE_URL` values.

If you use the blueprint, Render can provision the services directly from the repo instead of creating them manually.

## Manual Render Service Setup

If you prefer not to use the blueprint, create two Render services from this repository:

### API Service

- Environment: `Docker`
- Root/Context: repository root
- Dockerfile Path: `docker/backend/Dockerfile`
- Health Check Path: `/health`

### Worker Service

- Environment: `Docker`
- Root/Context: repository root
- Dockerfile Path: `docker/worker/Dockerfile`

Attach both services to:

- one Neon Postgres database via `DATABASE_URL`
- one managed Redis/key-value instance

## Required Environment Variables

Set these on both backend services unless noted otherwise:

- `ENVIRONMENT=production`
- `APP_NAME=AI Local SEO Platform API`
- `API_V1_PREFIX=/api/v1`
- `SECRET_KEY=<strong-random-secret>`
- `JWT_ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- `DATABASE_ECHO=false`
- `REDIS_HOST=<render-redis-host>`
- `REDIS_PORT=<render-redis-port>`
- `REDIS_DB=0`
- `CELERY_DEFAULT_QUEUE=local-seo`

Set these on the API service for automated migrations:

- `RUN_DB_MIGRATIONS_ON_START=true`
- `MIGRATION_MAX_RETRIES=20`
- `MIGRATION_RETRY_DELAY_SECONDS=3`

Optional provider/configuration variables:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `GOOGLE_MAPS_API_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `SENTRY_DSN`

For Neon Postgres, set:

- `DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require`
- `ALEMBIC_DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require`

You can leave the `POSTGRES_*` variables unset when `DATABASE_URL` and `ALEMBIC_DATABASE_URL` are provided.

## GitHub Secrets

Add these repository secrets:

- `RENDER_API_DEPLOY_HOOK_URL`
- `RENDER_WORKER_DEPLOY_HOOK_URL`

You get these deploy hook URLs from the Render service settings for the API and worker.

## Blueprint Setup

Render Blueprints use a repository-root `render.yaml` file and support Docker services, service references, and external secrets, which matches this repo’s deployment model.[^render-blueprint]

To use the included blueprint:

1. Push this repository to GitHub
2. In Render, create a new Blueprint from the repo
3. Review the resources Render detects from `render.yaml`
4. Provide the required `sync: false` secrets in the Render dashboard:
   - `DATABASE_URL`
   - `ALEMBIC_DATABASE_URL`
   - `CORS_ALLOW_ORIGINS`
   - `CORS_ALLOW_ORIGIN_REGEX`
   - any provider secrets you plan to enable
5. Apply the blueprint

The API service will auto-run `alembic upgrade head` on startup before it begins serving traffic.

## Workflow Behavior

`backend-render-deploy.yml` runs:

- on pushes to `main` when backend or backend container files change
- on manual dispatch

It triggers:

- API deploy via Render deploy hook
- worker deploy via Render deploy hook

When the API container starts, it now runs `alembic upgrade head` automatically before serving traffic.

## Recommended Release Flow

1. Finish a stage locally
2. Run the stage release script

   ```bash
   bash scripts/release-stage.sh <stage-slug> "<message>"
   ```

3. GitHub Actions runs:
   - frontend CI
   - frontend Vercel preview or production deployment
   - backend deploy hook workflow on `main`

## Notes

- The backend workflow triggers deployment hooks; Render handles the actual container build and rollout.
- Database migrations are now automated at API container startup.
- The Celery worker does not run migrations; keep `RUN_DB_MIGRATIONS_ON_START` limited to the API service.

[^render-blueprint]: Render’s blueprint reference documents repository-root `render.yaml` files, Docker-based web and worker services, `fromService` environment references, and `sync: false` secrets for dashboard-provided values. [Render Blueprint YAML Reference](https://render.com/docs/blueprint-spec) and [Render Blueprints (IaC)](https://render.com/docs/infrastructure-as-code)
