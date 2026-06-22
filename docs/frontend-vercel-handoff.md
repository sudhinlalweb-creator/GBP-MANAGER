# Frontend Vercel Handoff

## Goal

Deploy the Next.js frontend on Vercel and connect it to the Render-hosted backend API and Neon-backed data layer.

## Deployment Split

- frontend: Vercel
- backend API: Render web service
- Celery worker: Render worker service
- Redis: Render key-value
- Postgres: Neon

## Production URL Mapping

Use these URL shapes in production:

- frontend app:

  ```text
  https://<your-vercel-domain>
  ```

- backend API base:

  ```text
  https://<your-render-api-domain>/api/v1
  ```

- backend health check:

  ```text
  https://<your-render-api-domain>/health
  ```

Example:

```text
Frontend: https://gbp-manager.vercel.app
API base: https://gbp-manager-api.onrender.com/api/v1
Health: https://gbp-manager-api.onrender.com/health
```

## Required Vercel Environment Variables

Set these in the Vercel project:

```env
NEXT_PUBLIC_APP_NAME=AI Local SEO Platform
NEXT_PUBLIC_API_BASE_URL=https://<your-render-api-domain>/api/v1
```

Current frontend env contract:

- [frontend/.env.example](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/frontend/.env.example)
- [env.ts](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/frontend/lib/env.ts)

## Required Backend Environment Variables

Set these on Render for the API service:

```env
DATABASE_URL=postgresql://<user>:<password>@<neon-host>/<database>?sslmode=require
ALEMBIC_DATABASE_URL=postgresql://<user>:<password>@<neon-host>/<database>?sslmode=require
CORS_ALLOW_ORIGINS=https://<your-vercel-domain>
CORS_ALLOW_ORIGIN_REGEX=https://.*\\.vercel\\.app
```

Notes:

- `CORS_ALLOW_ORIGINS` is for your stable production domain
- `CORS_ALLOW_ORIGIN_REGEX` is useful for Vercel preview deployments
- the backend now applies CORS in [main.py](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/backend/app/main.py)
- the settings are defined in [config.py](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/backend/app/core/config.py)

## Google OAuth Redirect URI

If you enable Google OAuth, the backend setting must point to your production API callback target.

Set:

```env
GOOGLE_REDIRECT_URI=https://<your-render-api-domain>/api/v1/google/callback
```

Important:

- confirm this exact callback path against your production OAuth flow before going live
- also register the same URL in Google Cloud Console

## Vercel Project Setup

Use these settings in Vercel:

- framework: `Next.js`
- root directory: `frontend`
- install command: `npm ci`
- build command: `npm run build`

The repo already includes:

- [vercel.json](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/frontend/vercel.json)
- [vercel-preview.yml](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/.github/workflows/vercel-preview.yml)
- [vercel-production.yml](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/.github/workflows/vercel-production.yml)

## Recommended Production Values

If your Render API service becomes:

```text
https://gbp-manager-api.onrender.com
```

Set these:

```env
NEXT_PUBLIC_API_BASE_URL=https://gbp-manager-api.onrender.com/api/v1
CORS_ALLOW_ORIGINS=https://gbp-manager.vercel.app
CORS_ALLOW_ORIGIN_REGEX=https://.*\\.vercel\\.app
GOOGLE_REDIRECT_URI=https://gbp-manager-api.onrender.com/api/v1/google/callback
```

## Smoke Test After Deploy

1. Open the Vercel frontend URL
2. Open the browser dev tools network tab
3. Confirm frontend requests target the Render API base URL
4. Confirm no CORS errors appear
5. Confirm the backend health URL returns:

   ```json
   {"status":"ok"}
   ```

## Handoff Checklist

- Vercel project created with root `frontend`
- `NEXT_PUBLIC_API_BASE_URL` set to the Render API
- Render blueprint or manual services applied
- Neon `DATABASE_URL` and `ALEMBIC_DATABASE_URL` set
- API CORS set for Vercel production and preview domains
- API health endpoint responding
- frontend loads without browser CORS failures
