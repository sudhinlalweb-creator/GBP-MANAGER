# AI Local SEO SaaS Platform

Production-oriented workspace for a multi-tenant Local SEO platform focused on
Google Business Profile optimization, AI recommendations, keyword tracking,
review workflows, reporting, and agency operations.

## Workspace Layout

- `frontend/`: Next.js dashboard shell
- `backend/`: FastAPI API, Celery worker code, domain modules
- `docker/`: container definitions for frontend, backend, and workers
- `infrastructure/`: local Nginx and observability placeholders
- `docs/`: architecture and roadmap references

## Local Development

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Start the full stack:

   ```bash
   docker compose up --build
   ```

3. Open the applications:

- Frontend via Nginx: `http://localhost:8080`
- Backend docs: `http://localhost:8080/docs`
- Direct backend health: `http://localhost:8000/health`

## Current Baseline

- Backend code from the earlier prototype now lives under `backend/app`
- Frontend is re-initialized as a clean Next.js shell for the SaaS dashboard
- The repo is prepared for organization-first tenancy, Google integrations,
  Stripe billing, AI providers, and modular Local SEO services

## Delivery Automation

- GitHub Actions CI and Vercel deployment scaffolding are included for the frontend
- GitHub Actions backend deployment hook scaffolding is included for Render-style API and worker deploys
- Backend API startup now auto-runs Alembic migrations before serving traffic
- `render.yaml` codifies the Render API, worker, and Redis blueprint setup
- Preview deployments are designed for non-`main` branches
- Production deployments are designed for `main`
- Stage release guidance lives in [deployment-automation.md](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/docs/deployment-automation.md)
- Backend deployment guidance lives in [backend-deployment.md](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/docs/backend-deployment.md)
- Neon database guidance lives in [neon-database-setup.md](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/docs/neon-database-setup.md)
- Frontend Vercel handoff guidance lives in [frontend-vercel-handoff.md](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/docs/frontend-vercel-handoff.md)
