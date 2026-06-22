# Architecture Overview

## Platform Layers

1. `frontend/` renders the multi-tenant SaaS dashboard with Next.js, TypeScript,
   Tailwind CSS, and TanStack Query.
2. `backend/` exposes versioned FastAPI endpoints and houses domain modules.
3. `postgres` stores tenant, billing, SEO, reporting, and audit data.
4. `redis` provides broker and cache capabilities for asynchronous work.
5. `worker` runs Celery jobs for sync, tracking, reporting, AI, and automation.
6. `nginx` fronts the local workspace and provides a production-like entrypoint.

## Tenant Model

- `Organization` is the top-level tenant boundary.
- `OrganizationMembership` controls user access to an organization.
- All business data must eventually attach to `organization_id`.
- Local SEO entities such as locations, GBP profiles, reviews, keywords,
  rank history, heatmaps, and reports should never exist outside a tenant.

## Engineering Principles

- Keep route handlers thin.
- Put product logic in service modules.
- Isolate persistence behind repository-style modules as the codebase grows.
- Keep provider logic isolated behind integration clients.
- Reuse service logic from Celery tasks rather than duplicating workflows.
