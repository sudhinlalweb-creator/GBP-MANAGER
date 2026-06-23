# Codebase Refactoring Plan — 300-Line Limit + SOLID/DRY

**Goal**: Every source file stays under 300 lines. Each module has a single responsibility.
**Status**: 8 backend files and 0 frontend files currently exceed the limit.

---

## Current Violations (files > 300 lines)

| File | Lines | Priority |
|------|-------|----------|
| `backend/app/admin/service.py` | 493 | P1 |
| `backend/app/google/service.py` | 445 | P1 |
| `backend/app/api/v1/endpoints/projects.py` | 390 | P1 |
| `backend/app/api/v1/endpoints/agency.py` | 364 | P1 |
| `backend/app/ai/audit_service.py` | 358 | P1 |
| `backend/app/api/v1/endpoints/auth.py` | 349 | P1 |
| `backend/app/rank_tracking/service.py` | 334 | P1 |
| `backend/app/api/v1/endpoints/organizations.py` | 330 | P1 |

**Frontend files are all currently under 300 lines** — some are approaching the limit and are flagged below for pre-emptive splitting.

---

## Backend Refactoring

### 1. `admin/service.py` (493 → 3 files)

**Split by sub-concern (SRP):**

```
admin/
  user_service.py       — CRUD for users, role changes, suspension
  org_service.py        — org inspection, plan overrides
  health_service.py     — system health, stats aggregation
  service.py            — DELETED (re-export only if callers need it)
```

**SOLID note**: Admin endpoints in `api/v1/endpoints/admin.py` depend only on the service they need — not on the entire monolith.

---

### 2. `google/service.py` (445 → 3 files)

**Split by lifecycle stage (SRP + DRY):**

```
google/
  sync_service.py       — sync profiles/locations from GMB API
  profile_service.py    — profile CRUD, completeness scoring
  account_service.py    — connect/disconnect Google accounts, OAuth flow
  service.py            — thin re-exports (backwards compat, then delete)
```

**DRY note**: `scoring.py` (38 lines) already exists — `profile_service.py` should call it, not duplicate scoring logic.

---

### 3. `api/v1/endpoints/projects.py` (390 → 2 files)

**Split by resource (SRP):**

```
api/v1/endpoints/
  projects.py           — project CRUD only (< 150 lines)
  keywords.py           — keyword CRUD within projects (< 200 lines)
```

**Note**: Update `router.py` to register both sub-routers.

---

### 4. `api/v1/endpoints/agency.py` (364 → 2 files)

**Split by resource (SRP):**

```
api/v1/endpoints/
  agency_clients.py     — client org management
  agency_branding.py    — white-label branding settings
```

---

### 5. `ai/audit_service.py` (358 → 2 files)

**Split by layer (SRP):**

```
ai/
  audit_runner.py       — orchestrates audit: calls prompts, stores results
  audit_scoring.py      — pure functions: score calculation, category weighting
  audit_service.py      — DELETED (callers import from the above two)
```

**Note**: `audit_prompts.py` (38 lines) already exists — `audit_runner.py` imports from it directly. Do not copy prompts.

---

### 6. `api/v1/endpoints/auth.py` (349 → 3 files)

**Split by auth flow (SRP):**

```
api/v1/endpoints/auth/
  __init__.py           — aggregates sub-routers
  login.py              — /login, /refresh, /logout
  register.py           — /register, /verify-email
  password.py           — /forgot-password, /reset-password
```

**Note**: Update `router.py` to point at `auth/` package.

---

### 7. `rank_tracking/service.py` (334 → 2 files)

**Split by concern (SRP):**

```
rank_tracking/
  grid_service.py       — heatmap grid generation, SERP queries
  report_service.py     — trend aggregation, history reads
```

---

### 8. `api/v1/endpoints/organizations.py` (330 → 2 files)

**Split by resource (SRP):**

```
api/v1/endpoints/
  organizations.py      — org CRUD, settings (< 180 lines)
  org_members.py        — membership invite/accept/remove (< 150 lines)
```

---

## Frontend — Pre-emptive Splits (approaching 300)

These files are under 300 but will exceed it as features grow. Split now before the lint rule blocks development.

### `components/phase-two-dashboard.tsx` (282 lines)

This is a dead/legacy component. **Delete it** — it is not imported by any active page.

### `app/(protected)/agency/page.tsx` (279 lines)

Extract sub-components:

```
components/agency/
  AgencyDashboardTab.tsx   — stats, overview
  AgencyClientsTab.tsx     — client list, invite form
  AgencyBrandingTab.tsx    — white-label form
app/(protected)/agency/
  page.tsx                 — tab switcher only (< 60 lines)
```

### `app/(protected)/posts/page.tsx` (219 lines)

```
hooks/usePosts.ts            — useQuery + useMutation logic
components/posts/
  PostForm.tsx               — create post form
  PostCard.tsx               — single post display + delete
app/(protected)/posts/
  page.tsx                   — composes hooks + components (< 80 lines)
```

### `app/(protected)/reviews/page.tsx` (217 lines)

```
hooks/useReviews.ts          — useQuery + sync + reply mutations
components/reviews/
  ReviewCard.tsx             — review display, inline reply form
  Stars.tsx                  — star rating display
app/(protected)/reviews/
  page.tsx                   — composes hooks + components (< 80 lines)
```

### `app/(protected)/settings/page.tsx` (212 lines)

```
components/settings/
  OrgTab.tsx                 — org name/slug form
  BillingTab.tsx             — Stripe checkout/portal
  MembersTab.tsx             — member list + invite
app/(protected)/settings/
  page.tsx                   — tab switcher only (< 60 lines)
```

### `app/(protected)/profiles/[id]/page.tsx` (205 lines)

```
hooks/useProfile.ts          — profile fetch + sync mutation
components/profiles/
  ProfileHeader.tsx          — name, score ring, badges
  ProfileDetails.tsx         — address, hours, category, phone
app/(protected)/profiles/[id]/
  page.tsx                   — composes hooks + components (< 80 lines)
```

### `app/(protected)/keywords/page.tsx` (205 lines)

```
hooks/useKeywords.ts         — project + keyword queries/mutations
components/keywords/
  ProjectCard.tsx            — project + keyword list
  KeywordForm.tsx            — add keyword form
app/(protected)/keywords/
  page.tsx                   — composes (< 80 lines)
```

### `lib/types.ts` (202 lines)

```
lib/types/
  auth.ts         — User, AuthMe, OrganizationMembership
  google.ts       — GoogleBusinessProfile, GoogleAccount
  reviews.ts      — Review, ReviewListResponse
  posts.ts        — Post, PostListResponse
  keywords.ts     — Project, Keyword
  agency.ts       — Agency*, BrandingSettings
  billing.ts      — BillingInfo, PlanLimit
  index.ts        — re-exports all (for backwards compat)
```

---

## Execution Order

Execute in this order to minimise merge conflicts:

1. **Backend P1 violations** (8 files) — breaks CI right now
   - Start with `auth.py` (most self-contained)
   - Then `organizations.py`, `agency.py`, `projects.py`
   - Then `google/service.py`, `admin/service.py`
   - Then `ai/audit_service.py`, `rank_tracking/service.py`
2. **Delete `phase-two-dashboard.tsx`** (dead code)
3. **Frontend hooks extraction** — `useReviews`, `usePosts`, `useKeywords`, `useProfile`
4. **Frontend component splits** — one page at a time
5. **`lib/types.ts`** split — do last (most imports to update)

---

## Shared Patterns to Follow

### Backend: service split template

```python
# google/sync_service.py  — one concern only
from app.google.client import GMBClient
from app.google.models import GoogleBusinessProfile

class GoogleSyncService:
    def __init__(self, db: AsyncSession, client: GMBClient):
        self._db = db
        self._client = client   # injected, not global

    async def sync_profiles(self, account_id: str) -> list[GoogleBusinessProfile]: ...
```

### Frontend: page template (after split)

```tsx
// app/(protected)/reviews/page.tsx  — wires only
import { useReviews } from "@/hooks/useReviews"
import { ReviewCard } from "@/components/reviews/ReviewCard"

export default function ReviewsPage() {
  const { reviews, reply, deleteReply, sync } = useReviews()
  return <main>{ reviews.map(r => <ReviewCard key={r.id} review={r} onReply={reply} />) }</main>
}
```

### Frontend: hook template

```ts
// hooks/useReviews.ts  — data layer only
export function useReviews(profileId: string) {
  const reviews = useQuery({ queryKey: ["reviews", profileId], queryFn: ... })
  const reply   = useMutation({ mutationFn: ... })
  const sync    = useMutation({ mutationFn: ... })
  return { ...reviews, reply: reply.mutate, sync: sync.mutate }
}
```

---

## Verification

After each split, run:

```bash
python scripts/check_file_length.py
cd frontend && npm run lint
```

Both must pass before committing.
