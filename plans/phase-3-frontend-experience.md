# Feature: Phase 3 Frontend Experience

The following plan should be complete, but its important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Build the missing Phase 3 product surface in the Next.js app so users can actually use the backend intelligence features that already exist: similarity search, content briefs, workspace switching, and competitor monitoring. The backend now exposes routes and schemas for these flows, but the frontend still tops out at Phase 2 reports and field-based library search.

The goal of this feature is not to invent new backend capability. It is to turn the existing intelligence APIs into a coherent user workflow inside the product, with the same server-rendered and graceful-fallback patterns already used by the current search, library, and reports pages.

## User Story

As a creator, strategist, or agency operator
I want to explore similar saved clips, generate and review briefs, and manage workspace context from the UI
So that the product feels like a real planning tool instead of a backend-complete but frontend-incomplete scaffold

## Problem Statement

The repo has already moved beyond the original planning-only state. There are working backend contracts for:

- `POST /api/similarity/search`
- `GET /api/similarity/clips/{content_dna_id}`
- `POST /api/briefs`
- `GET /api/briefs`
- `GET /api/briefs/{brief_id}`
- `GET /api/workspaces`
- `POST /api/workspaces/switch`
- `POST /api/monitor-targets`
- `GET /api/monitor-targets`

But the frontend currently exposes only:

- `/`
- `/search`
- `/library`
- `/library/search`
- `/reports`

There are no Phase 3 pages, no typed frontend clients for the new APIs, no navigation entry points, and no tests covering the new intelligence workflows. That leaves the product in an awkward state where core backend value is unreachable from the UI.

## Solution Statement

Add a Phase 3 frontend slice that exposes the existing intelligence backend through server-rendered pages and focused client components:

- add typed client modules for similarity, briefs, and workspaces/monitor targets
- add new pages for briefs, workspaces, and clip similarity
- extend reports and library search with Phase 3 panels rather than replacing the Phase 2 layout
- update global navigation so the new product areas are reachable
- preserve current fallback behavior when the backend is unavailable, but prefer live API data when `NEXT_PUBLIC_API_BASE_URL` is configured

## Feature Metadata

**Feature Type**: Enhancement
**Estimated Complexity**: Medium
**Primary Systems Affected**: Next.js app router pages, client-side form components, typed frontend API helpers, nav, frontend tests
**Dependencies**: Next.js 14 app router, existing FastAPI routes, existing backend env wiring, Testing Library, Vitest

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

- `AGENTS.md`
  - Why: repo-specific workflow and command expectations
- `.claude/commands/plan-feature.md`
  - Why: required plan shape for this repo
- `plans/phase-3-intelligence-layer.md`
  - Why: original Phase 3 scope and rationale; this feature executes the missing frontend half of that plan
- `frontend/app/reports/page.tsx`
  - Why: current server-rendered page pattern for a mixed summary + form + history view
- `frontend/app/library/search/page.tsx`
  - Why: current server-rendered filter-driven retrieval page pattern to extend for semantic search
- `frontend/components/report-builder-form.tsx`
  - Why: existing client form conventions for async submit, optimistic messaging, and UI styling
- `frontend/components/library-filter-panel.tsx`
  - Why: current router-push filter pattern that the new similarity and workspace controls should mirror
- `frontend/components/site-nav.tsx`
  - Why: navigation entry point that must expose new Phase 3 routes
- `frontend/lib/reports.ts`
  - Why: current frontend API helper pattern with backend-aware fetch and local fallback behavior
- `frontend/lib/library-search.ts`
  - Why: current server-safe API origin handling and search-param helpers
- `backend/app/api/routes/similarity.py`
  - Why: exact similarity route surface the frontend should target
- `backend/app/api/routes/briefs.py`
  - Why: exact content brief route surface the frontend should target
- `backend/app/api/routes/workspaces.py`
  - Why: exact workspace and monitor-target route surface the frontend should target
- `backend/app/schemas/similarity.py`
  - Why: request/response shape for semantic search and "find similar clips"
- `backend/app/schemas/brief.py`
  - Why: request/response shape for content briefs
- `backend/app/schemas/workspace.py`
  - Why: request/response shape for workspace switching and monitor targets
- `frontend/tests/report-builder-form.test.tsx`
  - Why: example of mocking typed API helpers in form tests
- `frontend/tests/library-filter-panel.test.tsx`
  - Why: example of router-driven component tests

### New Files to Create

- `frontend/app/briefs/page.tsx`
  - Brief list and create experience
- `frontend/app/library/similar/[clipId]/page.tsx`
  - Similarity results page for a selected saved clip
- `frontend/app/workspaces/page.tsx`
  - Workspace switcher and monitor target management page
- `frontend/components/content-brief-builder.tsx`
  - Brief creation form bound to selected clip ids
- `frontend/components/monitor-target-form.tsx`
  - Create competitor monitoring target form
- `frontend/components/similarity-search-panel.tsx`
  - Semantic query form for freeform pattern search
- `frontend/components/workspace-switcher.tsx`
  - Active workspace selection form
- `frontend/components/brief-card.tsx`
  - Shared rendering for persisted briefs
- `frontend/components/monitor-target-list.tsx`
  - Shared rendering for monitoring targets
- `frontend/lib/briefs.ts`
  - Typed fetch helpers and fallback data for briefs
- `frontend/lib/similarity.ts`
  - Typed fetch helpers and fallback data for semantic search
- `frontend/lib/workspaces.ts`
  - Typed fetch helpers and fallback data for workspace and monitor target flows
- `frontend/tests/content-brief-builder.test.tsx`
  - Brief creation form test
- `frontend/tests/similarity-search-panel.test.tsx`
  - Similarity form test
- `frontend/tests/workspace-switcher.test.tsx`
  - Workspace switching form test
- `frontend/tests/monitor-target-form.test.tsx`
  - Monitor target form test

### Existing Files Likely To Update

- `frontend/app/reports/page.tsx`
  - Add links or panels for brief generation and trend-to-brief flow
- `frontend/app/library/search/page.tsx`
  - Add semantic-search entry point and "find similar" CTAs
- `frontend/components/site-nav.tsx`
  - Add `Reports`, `Briefs`, and `Workspaces`
- `frontend/lib/types.ts`
  - Only if shared UI types need to be centralized rather than duplicated

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- [Next.js App Router Data Fetching](https://nextjs.org/docs/app/building-your-application/data-fetching)
  - Specific section: server component fetch behavior
  - Why: the current app uses server-rendered route pages and should keep that pattern
- [FastAPI Async Docs](https://fastapi.tiangolo.com/async/)
  - Specific section: async/concurrency model
  - Why: helpful for understanding why the frontend should expect network-backed routes and partial degradation rather than blocking orchestration
- [Qdrant Filtering](https://qdrant.tech/documentation/concepts/filtering/)
  - Specific section: payload filtering
  - Why: informs frontend filter language for workspace- and collection-bounded semantic search
- [Clerk Organizations Guide](https://clerk.com/docs/guides/organizations/create-and-manage)
  - Specific section: organization switching and membership mental model
  - Why: the current backend models workspaces; eventual real auth/workspace sync should map cleanly to this UX
- [Claude Prompt Engineering Overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  - Specific section: structured prompting and best-practice prompting references
  - Why: useful context for how the brief-generation UI should frame inputs and outputs without exposing raw prompt complexity

### Patterns to Follow

**Naming Conventions:**

- snake_case for `frontend/lib/*.ts` helpers
- PascalCase for React components
- route segment names should stay short and product-facing: `/briefs`, `/workspaces`, `/library/similar/[clipId]`

**Data Fetching Pattern:**

- follow `frontend/lib/reports.ts` and `frontend/lib/library-search.ts`
- prefer `getApiOrigin()` plus `buildUrl()` helpers
- return fallback/demo data when backend origin is absent or request fails
- keep route pages server-rendered and let client components handle mutation forms

**Form Pattern:**

- mirror `frontend/components/report-builder-form.tsx`
- local state via `useState`
- async submit with simple success/error message
- no global client state library

**Navigation Pattern:**

- update `frontend/components/site-nav.tsx` incrementally
- preserve existing visual language and spacing rather than redesigning the shell

**Testing Pattern:**

- mock `next/navigation` for router-driven forms
- mock the relevant `frontend/lib/*` helper module rather than stubbing `fetch` directly
- keep tests focused on submit payload, route push behavior, and visible success state

**Fallback Behavior:**

- do not hard-fail the page if a Phase 3 API is unavailable
- keep dummy/default data for briefs, workspaces, and similarity results just as reports and library search do now
- the UI should make backend connectivity visible but not block local development

---

## IMPLEMENTATION PLAN

### Phase 1: Frontend Contracts

Create the typed frontend helpers first so all new pages and components build against one consistent API layer.

**Tasks:**

- add `frontend/lib/similarity.ts`
- add `frontend/lib/briefs.ts`
- add `frontend/lib/workspaces.ts`
- mirror the `buildUrl()` and fallback strategy already used in reports and library search
- define minimal mock/default payloads that match backend schema shape
- add search-param helpers only where they materially improve page URLs

### Phase 2: Core Pages And Components

Build the Phase 3 product surface as small, composable components rather than monolithic route files.

**Tasks:**

- create `frontend/app/briefs/page.tsx`
- create `frontend/components/content-brief-builder.tsx`
- create `frontend/components/brief-card.tsx`
- create `frontend/app/workspaces/page.tsx`
- create `frontend/components/workspace-switcher.tsx`
- create `frontend/components/monitor-target-form.tsx`
- create `frontend/components/monitor-target-list.tsx`
- create `frontend/app/library/similar/[clipId]/page.tsx`
- create `frontend/components/similarity-search-panel.tsx`

### Phase 3: Integration Into Existing Flows

Connect the new routes to the parts of the app where users already discover patterns and reports.

**Tasks:**

- update `frontend/components/site-nav.tsx` to expose the new routes
- add "find similar" links from `frontend/app/library/search/page.tsx` cards
- add a path from `frontend/app/reports/page.tsx` into brief creation
- ensure route labels and page copy reflect Phase 3 rather than Phase 2-only wording

### Phase 4: Testing And Validation

Lock in the new UI slice with the same lightweight but meaningful test posture used by the current frontend.

**Tasks:**

- add component tests for brief creation, similarity search, workspace switching, and monitor target creation
- rerun all frontend tests
- run a production build
- manually validate the happy path with the backend running on `localhost:8000`

---

## DETAILED IMPLEMENTATION NOTES

### Page Design Intent

This repo already has a strong visual direction: dark shell, large rounded panels, amber highlights, and server-rendered summaries. Keep that. The new Phase 3 pages should feel like a continuation of the existing product, not a redesign.

Recommended page responsibilities:

- `/briefs`
  - top: create brief form
  - bottom: persisted briefs list
- `/workspaces`
  - top: active workspace and switcher
  - middle: current memberships
  - bottom: monitor target creation and list
- `/library/similar/[clipId]`
  - top: source clip summary
  - main: similarity results
  - side/top panel: freeform semantic query

### API Mapping

Frontend helpers should map exactly to these endpoints:

- `listBriefs()` -> `GET /api/briefs`
- `createBrief()` -> `POST /api/briefs`
- `getSimilarClips(contentDnaId, limit)` -> `GET /api/similarity/clips/{id}?limit=n`
- `searchSimilarity(payload)` -> `POST /api/similarity/search`
- `listWorkspaces()` -> `GET /api/workspaces`
- `switchWorkspace(payload)` -> `POST /api/workspaces/switch`
- `listMonitorTargets()` -> `GET /api/monitor-targets`
- `createMonitorTarget(payload)` -> `POST /api/monitor-targets`

Do not invent alternate frontend-only endpoint shapes.

### UX Constraints

- workspace switching is temporarily backend-driven, not auth-provider-driven
- signin is currently bypassed, so avoid UI assumptions that depend on Clerk session objects
- show concise feedback after mutations
- make source selection explicit in the brief builder; do not hide selected clip ids behind uncontrolled state

### Risks And Edge Cases

- the similarity results page needs a clear empty state when no matching clip exists
- workspace switching may return a newly created workspace as active; the UI should treat that as valid
- monitor targets combine account handles and freeform query text; validation copy should explain that both are not always required semantically, even if `query_text` is required by schema
- if backend data is unavailable, demo data should be visually obvious enough that users do not mistake it for live production output

### Anti-Patterns To Avoid

- do not add client-side global stores for these flows
- do not scatter raw `fetch` calls across components
- do not couple route pages directly to backend schema details when a typed helper can absorb the shape
- do not redesign existing pages just to accommodate one new button or panel

---

## VALIDATION COMMANDS

Run these after implementation:

```bash
cd /Users/jordanmason/WOC/2026/susi_viral/frontend && corepack pnpm test
```

```bash
cd /Users/jordanmason/WOC/2026/susi_viral/frontend && corepack pnpm build
```

```bash
cd /Users/jordanmason/WOC/2026/susi_viral/backend && python3.13 -m pytest -q
```

```bash
cd /Users/jordanmason/WOC/2026/susi_viral && npm run dev
```

Manual checks:

1. Open `/briefs` and create a brief from valid selected clip ids.
2. Open `/workspaces`, switch workspaces, and create a monitor target.
3. Open `/library/search`, navigate into a similar-clips route, and verify results render.
4. Confirm the nav exposes all new pages and the app still works with the current signin bypass.

---

## EXIT CRITERIA

This feature is complete when:

- the frontend has pages for briefs, workspaces, and similar clips
- the new pages use typed frontend API helpers rather than ad hoc fetch calls
- navigation exposes the new Phase 3 areas
- the existing reports and library flows contain sensible entry points into the new features
- the frontend test suite passes
- the frontend production build passes
- the backend test suite still passes after integration

