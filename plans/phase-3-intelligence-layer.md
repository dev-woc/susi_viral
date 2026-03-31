# Feature: Phase 3 Intelligence Layer

The following plan is based on the PRD at `.claude/viral-content-agent-prd.md.pdf`, the completed planning artifacts in `plans/phase-1-mvp.md` and `plans/phase-2-full-platform-coverage.md`, and the planning contract in `.claude/commands/plan-feature.md`.

The PRD explicitly names the next roadmap step as Phase 3, "Intelligence Layer." This plan assumes the current repository already contains the Phase 1 and Phase 2 scaffolds and focuses on the next increment that makes the pattern library smarter over time rather than merely broader.

## Feature Description

Phase 3 turns the saved library and scheduled reports into an intelligence product. Users should be able to embed `ContentDNA` objects into a vector index, run similarity search against saved patterns, detect meaningful pattern movement over time, generate ready-to-shoot content briefs from selected patterns, and collaborate through shared workspaces and shared collections.

The user-facing change is material: instead of manually filtering a library and reading reports one run at a time, the user can ask the system for analogous clips, detect which mechanics are rising, and generate an actionable brief from the patterns they chose to reuse.

## User Story

As a creator, strategist, or agency operator
I want the system to find similar patterns, explain what is trending, and generate a usable content brief inside a shared workspace
So that I can move from research to planning without rebuilding the same analysis by hand

## Problem Statement

Phase 2 solves breadth and recurrence, but it still leaves the core "intelligence" gaps from the PRD:

- the library is searchable by fields, but not by semantic similarity
- reports show pattern counts, but not meaningful upward or downward movement over time
- the product stores patterns, but does not transform them into a planning artifact such as a content brief
- collaboration remains schema-ready rather than product-ready

Without those capabilities, the system is still a good research dashboard, but not yet a reusable planning assistant.

## Solution Statement

Build a Phase 3 expansion that:

- adds vector embeddings for `ContentDNA` and report snapshots using Qdrant
- adds similarity search for saved clips and saved patterns
- upgrades scheduled reports with persistent pattern-delta logic and trend summaries
- adds LLM-generated content briefs from selected saved patterns and report outputs
- adds shared workspaces and shared collections as the first real team feature
- adds competitor account monitoring as a saved monitoring target that feeds the existing report path

This phase should build on the existing FastAPI, LangGraph, Postgres, Celery, and Next.js architecture rather than replacing it.

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: High
**Primary Systems Affected**: backend intelligence services, vector indexing pipeline, report pipeline, workspace/auth model, library search UX, reports UX, content brief generation
**Dependencies**: FastAPI, LangGraph, Postgres, Qdrant, Celery, Redis, Next.js, Clerk Organizations, Anthropic API

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

These existing files define the current foundation Phase 3 must extend:

- `.claude/viral-content-agent-prd.md.pdf` - Source of truth for the Phase 3 roadmap: vector search, pattern delta, content briefs, team workspaces, and competitor monitoring
- `.claude/commands/plan-feature.md` - Required document shape for implementation plans
- `AGENTS.md` - Repo workflow rules and stack guidance
- `plans/phase-1-mvp.md` - Original Phase 1 scope and system constraints
- `plans/phase-2-full-platform-coverage.md` - Current phase assumptions and Phase 2 boundaries that Phase 3 now picks up
- `backend/app/services/library_search.py` - Current field-based and full-text library retrieval path that Phase 3 should augment, not replace
- `backend/app/api/routes/collections.py` - Current collection and library-search API surface
- `backend/app/services/reports/service.py` - Existing scheduled report lifecycle and snapshot persistence
- `backend/app/services/reports/report_graph.py` - Existing report orchestration path where trend and brief generation should plug in
- `backend/app/schemas/report.py` - Current report contracts and snapshot structures
- `backend/app/db/models/content_dna.py` - Current normalized pattern record that will require embeddings and reuse metadata
- `backend/app/db/models/collection.py` - Existing collection model that Phase 3 should make shareable
- `backend/app/db/models/scheduled_report.py` - Existing report definition and run-history model
- `frontend/app/reports/page.tsx` - Current reports landing experience to extend with trend and brief outputs
- `frontend/app/library/search/page.tsx` - Current library-search experience that Phase 3 should enhance with semantic search
- `frontend/lib/reports.ts` - Current report client contract
- `frontend/lib/library-search.ts` - Current library-search client contract

### New Files to Create

Recommended Phase 3 additions on top of the current scaffold:

- `backend/app/api/routes/similarity.py` - semantic search and "find similar clips" endpoints
- `backend/app/api/routes/briefs.py` - content brief creation and retrieval endpoints
- `backend/app/api/routes/workspaces.py` - workspace membership, switching, and shared collection endpoints
- `backend/app/db/models/embedding_job.py` - async embedding/indexing job records
- `backend/app/db/models/content_brief.py` - generated brief persistence
- `backend/app/db/models/workspace_membership.py` - user-to-workspace membership records if Clerk org membership is mirrored locally
- `backend/app/db/models/monitor_target.py` - competitor account and saved monitoring targets
- `backend/app/schemas/similarity.py` - request and response contracts for vector search
- `backend/app/schemas/brief.py` - brief generation contracts
- `backend/app/schemas/workspace.py` - shared workspace and membership contracts
- `backend/app/services/embeddings/encoder.py` - embedding generation wrapper
- `backend/app/services/embeddings/qdrant_client.py` - vector index bootstrap and CRUD wrapper
- `backend/app/services/embeddings/indexer.py` - `ContentDNA` upsert and reindex orchestration
- `backend/app/services/similarity_search.py` - semantic retrieval and result ranking
- `backend/app/services/reports/trend_analyzer.py` - stronger pattern-delta and trend movement logic
- `backend/app/services/briefs/content_brief_service.py` - LLM brief generation from selected patterns
- `backend/app/services/workspaces/service.py` - workspace switching and shared collection access rules
- `backend/app/services/monitoring/competitor_monitor.py` - saved competitor target execution path
- `backend/app/tasks/embeddings.py` - Celery tasks for indexing and reindexing
- `backend/app/tasks/briefs.py` - optional async brief-generation tasks
- `backend/tests/test_similarity_search.py` - vector search and fallback tests
- `backend/tests/test_content_briefs.py` - brief-generation tests
- `backend/tests/test_workspaces.py` - shared workspace access tests
- `backend/tests/test_trend_analyzer.py` - trend-delta logic tests
- `frontend/app/briefs/page.tsx` - content brief list/create view
- `frontend/app/library/similar/[clipId]/page.tsx` - similarity results view
- `frontend/app/workspaces/page.tsx` - workspace selection and membership view
- `frontend/components/similarity-search-panel.tsx` - semantic query and similar-clips panel
- `frontend/components/content-brief-builder.tsx` - selected-pattern to brief UI
- `frontend/components/trend-delta-panel.tsx` - trend movement visualization for reports
- `frontend/components/workspace-switcher.tsx` - shared workspace selector
- `frontend/lib/briefs.ts` - typed brief client helpers
- `frontend/lib/similarity.ts` - typed similarity client helpers
- `frontend/lib/workspaces.ts` - typed workspace client helpers

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- [Qdrant Collections](https://qdrant.tech/documentation/concepts/collections/)
  - Specific section: vector configuration, metrics, and collection setup
  - Why: Phase 3 adds a persistent vector index for `ContentDNA`
- [Qdrant Filtering](https://qdrant.tech/documentation/concepts/filtering/)
  - Specific section: payload filters and hybrid filtering
  - Why: semantic search should still honor workspace, platform, and collection boundaries
- [FastAPI async docs](https://fastapi.tiangolo.com/async/)
  - Specific section: async I/O handlers and concurrency model
  - Why: similarity retrieval, brief generation, and indexing orchestration remain network-heavy
- [Clerk Organization management](https://clerk.com/docs/guides/organizations/create-and-manage)
  - Specific section: organization creation, membership, and switching
  - Why: Phase 3 is the first phase that should expose shared workspaces in the product
- [Anthropic prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  - Specific section: reliable structured prompting for generation tasks
  - Why: content briefs should be generated from selected patterns in a constrained, reusable format

### Patterns to Follow

Phase 3 should extend the current implementation rather than fork it:

**Naming Conventions:** keep snake_case Python modules, PascalCase React components, singular model names, and explicit service names for each intelligence capability

**Error Handling:** semantic search, brief generation, and competitor monitoring should degrade gracefully; vector-index or LLM failures should not make the saved library unreadable or reports unretrievable

**Logging Pattern:** continue propagating `search_id`, `report_run_id`, and `scheduled_report_id`; add `brief_id`, `embedding_job_id`, and `workspace_id` where relevant

**Other Relevant Patterns:**

- keep Postgres as the system of record and treat Qdrant as a derived index
- keep indexing idempotent for a given `ContentDNA` revision
- preserve current report snapshots; add richer trend metadata instead of changing prior runs in place
- continue returning partial failures instead of failing whole workflows when one subsystem degrades
- preserve workspace isolation in both SQL queries and vector search filters

---

## IMPLEMENTATION PLAN

### Architecture Decisions

1. Keep Postgres as the source of truth and use Qdrant as a derived retrieval layer for embeddings and similarity.
2. Add embeddings asynchronously through Celery so search and save flows do not block on vector indexing.
3. Reuse the existing `ContentDNA` contract as the embedding source instead of inventing a second pattern schema.
4. Make semantic search hybrid: vector similarity first, then filter by workspace, platform, collection, or pattern metadata.
5. Treat content briefs as persisted artifacts linked to saved patterns and report runs, not ephemeral chat responses.
6. Model shared workspaces explicitly in the backend and mirror Clerk org context into local authorization checks.
7. Implement competitor monitoring as configuration that feeds the existing report pipeline, not as a separate crawler subsystem.

### Scope For Phase 3

In scope:

- vector embeddings for `ContentDNA`
- Qdrant-backed similarity search
- "find clips like this one" flow
- stronger pattern-delta analysis in report runs
- LLM-generated content briefs from selected patterns
- shared workspaces and shared collections
- competitor account monitoring targets

Out of scope:

- browser extension support
- benchmark mode for uploading and scoring a user’s own clips
- white-label client reporting
- audio transcription
- API productization for third-party developers

### Data Model v3

Add these first-class entities on top of the current model set:

1. `EmbeddingJob`
2. `ContentBrief`
3. `WorkspaceMembership`
4. `MonitorTarget`

Recommended additions to existing entities:

- add `embedding_status`, `embedding_model`, and `embedding_updated_at` to `ContentDNA`
- add `times_reused` and `last_reused_at` to `ContentDNA` or `LibraryItem`
- add `shared` or equivalent access metadata to `Collection`
- add richer trend metadata to `ReportRun.report_snapshot`

Minimum relationships:

- a `WorkspaceMembership` links a `User` to a `Workspace`
- an `EmbeddingJob` targets one `ContentDNA`
- a `ContentBrief` belongs to a `Workspace` and references one or more `ContentDNA` items or a `ReportRun`
- a `MonitorTarget` belongs to a `Workspace` and can feed one or more `ScheduledReport` definitions

### API Surface

Initial backend endpoints for Phase 3:

- `POST /api/similarity/search`
  - semantic search against saved `ContentDNA`
- `GET /api/similarity/clips/{content_dna_id}`
  - returns similar clips to a chosen saved pattern
- `POST /api/briefs`
  - generates and stores a content brief from selected pattern ids
- `GET /api/briefs`
  - lists generated briefs
- `GET /api/briefs/{brief_id}`
  - returns a persisted brief
- `GET /api/workspaces`
  - lists available workspaces and memberships
- `POST /api/workspaces/switch`
  - switches the active workspace context
- `POST /api/monitor-targets`
  - creates a competitor account or saved monitoring target
- `GET /api/monitor-targets`
  - lists monitoring targets

### Intelligence Pipeline

Implement the Phase 3 intelligence workflow in these paths:

1. `EmbeddingIndexer`
2. `SimilaritySearch`
3. `TrendAnalyzer`
4. `BriefBuilder`
5. `WorkspaceAccessControl`
6. `CompetitorMonitor`

Node expectations:

1. `EmbeddingIndexer`
   - converts `ContentDNA` to embedding text
   - writes vectors to Qdrant with workspace and collection payload filters
2. `SimilaritySearch`
   - resolves vector neighbors
   - re-ranks with SQL metadata filters and current access rules
3. `TrendAnalyzer`
   - compares report runs over time and outputs trend deltas with stable semantics
4. `BriefBuilder`
   - turns selected patterns into a structured, ready-to-shoot content brief
5. `WorkspaceAccessControl`
   - enforces visibility for shared collections, reports, and briefs
6. `CompetitorMonitor`
   - stores account targets and reuses the report path to watch them over time

### Frontend Experience

Phase 3 UI should include:

1. Similarity search
   - "find similar clips" from a saved item
   - semantic query over the saved library
2. Report intelligence
   - trend-delta panel
   - clearer "up / down / new" pattern movement
3. Brief generation
   - select saved patterns
   - generate and save a content brief
4. Workspace experience
   - workspace switcher
   - shared collections and shared briefs
5. Competitor monitoring
   - manage saved competitor accounts and monitor targets

Frontend guidance:

- keep list and detail reads server-rendered where practical
- use client components for selection flows, brief generation, and workspace switching
- preserve the existing App Router structure and typed helper pattern

### Testing Strategy

Backend tests:

1. embedding job and Qdrant client tests with mocked vector responses
2. similarity search tests with workspace and collection filters
3. trend analyzer tests across multiple report runs
4. content brief generation tests with canned Anthropic responses
5. workspace membership and authorization tests
6. competitor monitor persistence and report-trigger tests

Frontend tests:

1. similarity search panel interaction tests
2. brief builder selection and submission tests
3. workspace switcher tests
4. trend-delta rendering tests for positive, negative, and new-pattern states

End-to-end tests:

1. sign in and switch workspace
2. save clips to a shared collection
3. run similarity search on a saved clip
4. generate a brief from selected patterns
5. create a competitor monitor target
6. verify a report displays trend deltas in the workspace

### Validation Commands

Use the current repo command set and extend it if new tools are added:

```bash
# backend
cd backend && pytest
cd backend && ruff check .
cd backend && mypy app

# frontend
cd frontend && pnpm lint
cd frontend && pnpm test
cd frontend && pnpm build

# e2e
pnpm test:e2e
```

If Qdrant is introduced through local infra, add a deterministic local validation path such as:

```bash
docker compose up -d qdrant
cd backend && pytest tests/test_similarity_search.py
```

### Delivery Sequence

1. Add the embedding and workspace data-model extensions.
2. Introduce Qdrant client setup and asynchronous indexing jobs.
3. Embed existing `ContentDNA` records and add reindex logic.
4. Expose semantic similarity endpoints and backend tests.
5. Upgrade report analysis with stronger trend-delta logic.
6. Add content brief generation and persistence.
7. Add shared workspaces and shared collection access control.
8. Add competitor monitoring targets that reuse the report pipeline.
9. Build the new frontend views and flows.
10. Finish validation, e2e coverage, and local developer setup.

### Risks And Mitigations

1. Embedding drift can make similarity search unstable across schema revisions.
   - Mitigation: version the embedding model and store reindex metadata per `ContentDNA`.
2. Qdrant can become a second source of truth if writes are not controlled.
   - Mitigation: keep SQL authoritative and rebuild vectors from SQL when necessary.
3. Shared workspaces increase authorization complexity.
   - Mitigation: centralize workspace resolution and apply filters consistently in SQL and vector queries.
4. Content brief quality can become generic or repetitive.
   - Mitigation: constrain prompts with selected patterns, desired outputs, and structured response contracts.
5. Competitor monitoring can widen scope too aggressively.
   - Mitigation: treat it as saved report input configuration, not a brand-new scraping framework.

### Exit Criteria

Phase 3 is complete when:

1. A user can run semantic similarity search across saved `ContentDNA`.
2. A user can choose a saved clip and see similar patterns in the library.
3. Scheduled reports show meaningful pattern deltas across runs.
4. A user can select saved patterns and generate a persisted content brief.
5. Shared workspaces and shared collections function for at least the core read/write flows.
6. Competitor monitoring targets can be configured and feed the report workflow.
7. Core backend, frontend, and e2e validation commands pass.
