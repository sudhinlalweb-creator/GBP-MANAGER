# GBP Manager — Agent Rules

These rules are **non-negotiable** and apply to every agent, PR, and commit in this repository. Never override, disable, or work around them.

---

## 1. 300-Line Hard Limit

**Every source file must stay under 300 lines.** This includes `.ts`, `.tsx`, and `.py` files in tracked source directories.

- **Never raise the limit**, comment it out, or add `// eslint-disable max-lines`.
- When a file approaches the limit, split it proactively along SOLID boundaries (Single Responsibility).
- The check runs automatically:
  - **Frontend**: `npm run lint` (ESLint `max-lines` rule, error-level)
  - **Backend + Frontend**: `python scripts/check_file_length.py`
  - Both run in `ci:check` — the build will fail if violated.

**Why**: Files over 300 lines are almost always doing too many things. The limit forces early decomposition before the debt becomes painful.

---

## 2. No `--no-verify` Commits

**Never commit with `git commit --no-verify`** or any flag that bypasses hooks (`-n`, `--no-verify`).

If a pre-commit hook fails, fix the underlying issue — do not bypass it.

**Why**: Hooks are the last line of defense before bad code hits the branch. Bypassing them silently breaks contracts other engineers depend on.

---

## 3. SOLID & DRY Principles

Apply these at every level of the codebase:

| Principle | What it means here |
|-----------|-------------------|
| **S** — Single Responsibility | One file = one concern. Endpoints, services, schemas, types live in separate files. |
| **O** — Open/Closed | Extend via new files / subclasses, not by editing stable interfaces. |
| **L** — Liskov Substitution | Subtypes must be drop-in replacements for their base. |
| **I** — Interface Segregation | Small, focused interfaces/types. No god-objects. |
| **D** — Dependency Inversion | Inject dependencies (db session, clients) — don't import globals inside functions. |
| **DRY** | Extract shared logic into `lib/`, `utils/`, or `services/` — never copy-paste. |

---

## 4. Module Boundaries

### Backend (`backend/app/`)
```
api/v1/endpoints/<domain>/   — thin HTTP handlers only (< 300 lines per file)
<domain>/service.py          — business logic (split by sub-concern if needed)
<domain>/models.py           — SQLAlchemy models
schemas/<domain>.py          — Pydantic request/response schemas
```

### Frontend (`frontend/`)
```
app/(protected)/<page>/      — page entry (< 300 lines)
  page.tsx                   — wires hooks → view, no business logic
components/<domain>/         — reusable presentational components
hooks/use<Domain>.ts         — data fetching / mutation hooks (TanStack Query)
lib/                         — pure utilities, API client, type definitions
```

---

## 5. Naming Conventions

- **Python**: `snake_case` files and functions, `PascalCase` classes.
- **TypeScript**: `camelCase` files for hooks/utils, `PascalCase` for components, `kebab-case` for page directories.
- Hook files: `useReviews.ts`, `useProfiles.ts` — one hook per domain.
- Component files: one exported component per file.

---

## 6. CI Gate

Before any commit, ensure these pass locally:

```bash
# Frontend
cd frontend && npm run lint && npm run typecheck

# Backend
cd backend && python3 -m ruff check app/

# Both (run from repo root)
python3 scripts/check_file_length.py
```

A commit that breaks `ci:check` must not be merged.
