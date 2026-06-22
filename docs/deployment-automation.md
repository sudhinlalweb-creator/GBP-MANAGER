# Deployment Automation

## Goal

Automate the delivery loop for each completed stage:

1. Commit and push the stage to GitHub
2. Run CI checks automatically
3. Deploy a Vercel preview for non-`main` branches
4. Deploy production from `main`

## Current Scope

- `frontend/` is prepared for automated Vercel deployment
- `backend/` is validated in GitHub Actions and prepared for Render-style deploy hook automation
- backend API startup now auto-applies Alembic migrations before serving traffic
- `render.yaml` now codifies the Render API, worker, and Redis blueprint setup
- `backend/` is **not** deployed to Vercel
- Backend deployment details live in [backend-deployment.md](file:///Users/sudhinlal/Documents/trae_projects/gbp-manager/docs/backend-deployment.md)

## Files Added

- `.github/workflows/ci.yml`
- `.github/workflows/vercel-preview.yml`
- `.github/workflows/vercel-production.yml`
- `.github/workflows/backend-render-deploy.yml`
- `render.yaml`
- `frontend/vercel.json`
- `scripts/release-stage.sh`
- `scripts/db-upgrade.sh`
- `docs/frontend-vercel-handoff.md`

## GitHub Secrets

Add these repository secrets in GitHub:

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `RENDER_API_DEPLOY_HOOK_URL`
- `RENDER_WORKER_DEPLOY_HOOK_URL`

## Vercel Project Setup

Create a Vercel project for the frontend and configure:

- Root Directory: `frontend`
- Framework Preset: `Next.js`
- Build Command: `npm run build`
- Install Command: `npm ci`

Set the required Vercel environment variables:

- `NEXT_PUBLIC_API_BASE_URL`
- any future public frontend variables you add under `frontend/.env.example`

For production, `NEXT_PUBLIC_API_BASE_URL` should point to the deployed backend API, not localhost.

## Workflow Behavior

### CI

`ci.yml` runs on every push and pull request.

- Frontend:
  - `npm ci`
  - `npm run typecheck`
  - `npm run build`
- Backend:
  - install Python dependencies
  - `python -m compileall app`

### Preview Deployments

`vercel-preview.yml` runs on every push to non-`main` branches and on manual dispatch.

- pulls Vercel preview environment
- builds the frontend with Vercel CLI
- deploys a preview URL

### Production Deployments

`vercel-production.yml` runs on pushes to `main` and on manual dispatch.

- pulls Vercel production environment
- builds a production artifact
- deploys to the production Vercel project

## Stage Release Helper

Use the helper script when you finish a stage:

```bash
bash scripts/release-stage.sh phase-4-admin "admin panel actions"
```

This script:

- stages all changes
- creates a commit
- creates an annotated tag
- pushes the branch
- pushes the tag

## Recommended Stage Flow

1. Finish a stage locally
2. If this folder is not a Git repository yet, bootstrap it once:

   ```bash
   git init
   git branch -M main
   git add -A
   git commit -m "chore: initial platform baseline"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

3. Validate the app
4. Run:

   ```bash
   bash scripts/release-stage.sh <stage-slug> "<message>"
   ```

5. GitHub Actions runs CI
6. Vercel preview deploys automatically from the pushed branch
7. Merge to `main` when approved
8. Vercel production deploys automatically from `main`

## Notes

- The frontend currently uses `typecheck + build` in CI because `next lint` is still waiting for initial ESLint setup.
- If you want stricter frontend CI next, add a committed ESLint config and then switch CI to `npm run lint`.
- For local/manual schema upgrades, run `bash scripts/db-upgrade.sh`.
