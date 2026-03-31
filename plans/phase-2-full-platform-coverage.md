# Feature: Phase 2 Full Platform Coverage And Scheduled Reports

The following plan is based on the PRD at `.claude/viral-content-agent-prd.md.pdf`, the Phase 1 execution plan in `plans/phase-1-mvp.md`, and the planning contract in `.claude/commands/plan-feature.md`.

This workspace already contains the Phase 1 planning scaffold and, in this branch of work, Phase 1 implementation assets under `backend/` and `frontend/`. This document defines the next product phase target, the incremental repository changes required, and the mandatory references for the implementation pass.

## Feature Description

Phase 2 turns the Phase 1 on-demand search product into a broader research workflow. Users should be able to search and schedule across all five PRD platforms, receive recurring digest reports, and search the saved pattern library by extracted element fields instead of only browsing raw saved clips.

The user-facing value is straightforward: a creator or strategist can run one search workflow for TikTok, Instagram Reels, YouTube Shorts, Twitter/X, and Reddit; save time by receiving scheduled email or dashboard digests; and reuse the library as a searchable pattern system rather than a static clip archive.

## User Story

As a creator, strategist, or agency operator
I want to monitor all target platforms on a schedule and search my saved patterns by element field
So that I can track repeatable creative mechanics over time without manually rebuilding the same research workflow each week

## Problem Statement

Phase 1 solves on-demand discovery for two platforms, but it still leaves three core product gaps from the PRD:

- platform coverage is incomplete for the planned research footprint
- reports are manual instead of recurring
- saved content is not yet organized for fast retrieval by element fields

Without these capabilities, the product still behaves like a point-in-time search tool instead of a research system that accumulates reusable intelligence.

## Solution Statement

Build a Phase 2 expansion that:

- adds Instagram Reels, Twitter/X, and Reddit connectors behind the existing backend connector interface
- adds scheduled report configuration, execution, persistence, and delivery
- adds library search and filtering by `ContentDNA` fields and pattern tags
- extends the existing search graph so report generation and library retrieval reuse the same normalized data path
- keeps scheduled jobs isolated behind Celery and Redis so recurrence does not complicate the on-demand search path

The phase should preserve the Phase 1 architecture choices: FastAPI for APIs, LangGraph for orchestration, Postgres as the system of record, and Next.js for the UI.

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: High
**Primary Systems Affected**: backend API, connector layer, scheduled job pipeline, report persistence, library query UX, frontend dashboard
**Dependencies**: FastAPI, LangGraph, Celery, Redis, Postgres, Neon, Next.js, Tailwind CSS, Clerk, email delivery provider, PDF generation library

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

The repo currently contains Phase 1 planning material and a Phase 1 scaffold. These are the files that matter for the next phase:

- `.claude/viral-content-agent-prd.md.pdf` - Product roadmap, Phase 2 scope, report requirements, and phase exit criteria
- `.claude/commands/plan-feature.md` - Required shape and expectations for planning artifacts
- `AGENTS.md` - Repo workflow rules and stack guidance
- `plans/phase-1-mvp.md` - Phase 1 scope, architecture assumptions, data model, and validation strategy
- `backend/app/services/connectors/base.py` - Existing normalized connector contract to extend for additional platforms
- `backend/app/services/search_service.py` - Existing orchestration entry point and persistence path for search results
- `backend/app/services/graph/search_graph.py` - Existing search pipeline structure that should be reused for scheduled runs
- `backend/app/schemas/search.py` - Search request/response contract that scheduled report generation should remain compatible with
- `backend/app/db/models/search_query.py` - Search history record shape and status model
- `backend/app/db/models/library_item.py` - Saved clip persistence model and workspace linkage
- `frontend/app/search/page.tsx` - Existing search UX and current result rendering pattern
- `frontend/app/library/page.tsx` - Current saved-clips experience that Phase 2 will extend with field filters
- `frontend/components/results-table.tsx` - Result-card/table composition pattern and partial-failure handling
- `frontend/lib/api.ts` - Frontend API client and backend contract surface

### New Files to Create

Recommended Phase 2 additions, assuming the Phase 1 scaffold remains in place:

- `backend/app/api/routes/reports.py` - scheduled report configuration, listing, and delivery metadata endpoints
- `backend/app/api/routes/collections.py` - library search and collection-style retrieval endpoints
- `backend/app/db/models/scheduled_report.py` - scheduled report configuration and run history
- `backend/app/db/models/report_delivery.py` - email/dashboard delivery status and retry metadata
- `backend/app/db/models/collection.py` - named library collection model if the implementation groups saved items
- `backend/app/db/models/collection_item.py` - many-to-many join for collections and saved clips
- `backend/app/services/connectors/instagram_reels.py` - Instagram Reels connector implementation
- `backend/app/services/connectors/twitter_x.py` - Twitter/X connector implementation
- `backend/app/services/connectors/reddit.py` - Reddit connector implementation
- `backend/app/services/reports/report_graph.py` - scheduled report orchestration graph
- `backend/app/services/reports/report_builder.py` - summary, pattern-delta, and top-clips report assembly
- `backend/app/services/reports/delivery.py` - email and dashboard delivery adapter
- `backend/app/services/library_search.py` - full-text and field-based library filtering logic
- `backend/app/tasks/reports.py` - Celery task entry points for scheduled report runs
- `backend/tests/test_reports_api.py` - report configuration and run-history tests
- `backend/tests/test_library_search.py` - filter and search tests for saved clips and element fields
- `frontend/app/reports/page.tsx` - scheduled report management UI
- `frontend/app/library/search/page.tsx` - library search and filter UI if kept separate from the main library page
- `frontend/components/report-builder-form.tsx` - report configuration form
- `frontend/components/report-history-table.tsx` - delivery and execution history view
- `frontend/components/library-filter-panel.tsx` - element-field filter controls
- `frontend/lib/reports.ts` - typed report client helpers
- `frontend/lib/library-search.ts` - typed library search helpers

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- [LangGraph docs](https://docs.langchain.com/oss/python/langgraph)
  - Specific section: stateful graphs, branching, and retry behavior
  - Why: Phase 2 reuses the orchestration layer for scheduled report generation
- [FastAPI async docs](https://fastapi.tiangolo.com/async/)
  - Specific section: async I/O handlers and dependency injection
  - Why: connector, report, and library endpoints will remain network and database heavy
- [Celery user guide](https://docs.celeryq.dev/en/stable/userguide/index.html)
  - Specific section: task definition, routing, retries, and beat scheduling
  - Why: scheduled report execution needs reliable recurrence and bounded retries
- [Celery periodic tasks guide](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html)
  - Specific section: beat schedules and crontab configuration
  - Why: Phase 2 includes daily, weekly, and custom scheduled report runs
- [Clerk organizations guide](https://clerk.com/docs/guides/organizations/create-and-manage)
  - Specific section: organization creation and workspace switching
  - Why: the PRD keeps team-ready workspace semantics in the data model even if the UI stays mostly personal
- [Next.js Server Actions docs](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)
  - Specific section: server actions for mutations
  - Why: report configuration and library filter mutations should not be handled through unnecessary client fetch plumbing
- [Next.js backend-for-frontend guide](https://nextjs.org/docs/app/guides/backend-for-frontend)
  - Specific section: server components for reads
  - Why: library browsing and report history are read-heavy and should stay server-rendered where practical
- [PostgreSQL full text search docs](https://www.postgresql.org/docs/current/textsearch.html)
  - Specific section: text search and tsvector/tsquery basics
  - Why: library search by `ContentDNA` fields and pattern tags should not require a vector DB yet

### Patterns to Follow

Use the Phase 1 implementation and plan as the starting point, and keep these patterns consistent:

**Naming Conventions:** snake_case for Python modules, PascalCase for React components, singular model names for domain entities, and explicit connector names per platform

**Error Handling:** platform connectors should continue returning partial-failure metadata instead of failing the whole request; scheduled report runs should record retryable failures separately from permanent ones

**Logging Pattern:** include `search_id` for on-demand runs and `scheduled_report_id` or `report_run_id` for recurrence; propagate those identifiers through connector, ranking, aggregation, and delivery logs

**Other Relevant Patterns:**

- keep platform-specific fetch logic isolated behind the existing connector abstraction
- keep raw payloads, extracted `ContentDNA`, and report artifacts separately persisted
- treat report generation as a reusable orchestration workflow instead of duplicating search logic
- maintain workspace-ready schema fields even if the UI remains single-user for now
- prefer deterministic summary fields and stored snapshots for scheduled reports so the same run can be re-opened later

---

## IMPLEMENTATION PLAN

### Architecture Decisions

1. Reuse the Phase 1 connector abstraction and search graph instead of creating a parallel report-only pipeline.
2. Add new platform connectors behind the same interface used by TikTok and YouTube Shorts so report and search code paths stay normalized.
3. Keep scheduled reports in Celery and Redis, not inside request handlers, so report delivery can retry independently of the UI.
4. Store report definitions, executions, and deliveries in Postgres so users can inspect history and delivery status later.
5. Implement library search using Postgres field filters and full-text search before considering vector similarity or embeddings.
6. Keep the UI report-centric but defer team collaboration features such as shared workspaces, annotations, and shared collections to the next phase unless the PRD item is explicitly required for report setup.

### Scope For Phase 2

In scope:

- Instagram Reels, Twitter/X, and Reddit connectors
- scheduled report creation, update, listing, and deletion
- report execution history and delivery tracking
- daily, weekly, and custom-interval report recurrence
- email and dashboard delivery for reports
- pattern aggregation across clips and across repeated scheduled runs
- library search by `ContentDNA` fields, platform, hook type, format type, and pattern tags
- PDF export for report outputs if the delivery pipeline can support it without blocking the core recurrence flow

Out of scope:

- vector search over `ContentDNA`
- similarity search like “find clips like this one”
- team workspaces beyond schema readiness
- annotation/note UX for saved clips
- benchmark or scoring modes against the user’s own clips
- audio transcription and browser extensions

### Data Model v2

Add these first-class entities on top of the Phase 1 model set:

1. `ScheduledReport`
2. `ReportRun`
3. `ReportDelivery`
4. `Collection`
5. `CollectionItem`

Minimum relationships:

- a `ScheduledReport` belongs to a `Workspace`
- a `ReportRun` belongs to a `ScheduledReport`
- a `ReportDelivery` belongs to a `ReportRun`
- a `Collection` belongs to a `Workspace`
- a `CollectionItem` links a `Collection` to a saved `ContentDNA`
- `ScheduledReport` references the target platforms, keywords, accounts, frequency, and delivery channels

Phase 2 simplification:

- keep a single workspace in the UI if auth is still personal-only
- model report history as immutable runs so a user can inspect previous output even if the schedule changes later
- use stored snapshots for the top N clips and pattern summary so the UI does not depend on recomputation

### API Surface

Initial backend endpoints for Phase 2:

- `POST /api/reports`
  - creates a scheduled report definition
- `GET /api/reports`
  - lists configured reports
- `GET /api/reports/{report_id}`
  - returns a report definition and latest run status
- `POST /api/reports/{report_id}/run`
  - triggers a manual report run
- `GET /api/reports/{report_id}/runs`
  - returns execution history
- `GET /api/library/items`
  - extends existing library listing with field filters
- `GET /api/library/search`
  - full-text search across saved `ContentDNA` and pattern tags
- `POST /api/library/collections`
  - creates a named collection
- `GET /api/library/collections`
  - lists collections and their metadata
- `GET /api/health`
  - service health

### Report Pipeline

Implement the scheduled-report workflow as a graph or task chain that reuses the search path:

1. `ReportSelector`
2. `PlatformFetcher`
3. `Normalizer`
4. `ViralityRanker`
5. `ContentSampler`
6. `ElementExtractor`
7. `PatternAggregator`
8. `ReportFormatter`
9. `DeliveryDispatcher`

Node expectations:

1. `ReportSelector`
   - loads report configuration, recurrence cadence, delivery targets, and filter criteria
2. `PlatformFetcher`
   - runs the requested platform connectors in parallel and records per-platform failures
3. `Normalizer`
   - converts platform-specific metrics into a shared ranking input contract
4. `ViralityRanker`
   - scores clips per platform and filters by report thresholds
5. `ContentSampler`
   - chooses the top N clips and reuses cached raw clip metadata where possible
6. `ElementExtractor`
   - calls the extraction service for the selected clips and validates schema output
7. `PatternAggregator`
   - compares current results against previous report snapshots and builds simple pattern deltas
8. `ReportFormatter`
   - creates dashboard-ready and email-ready report payloads
9. `DeliveryDispatcher`
   - sends the report to email and persists the dashboard copy and delivery status

### Frontend Experience

Phase 2 UI should include:

1. Report builder page
   - name, platforms, niche or account filters, cadence, top N, and delivery channels
2. Reports dashboard
   - list of scheduled reports and latest run state
   - run history with delivery status
3. Library search experience
   - filter by platform, hook type, format type, element tag, and recency
4. Report detail view
   - top clips, pattern summary, and delivery links

Frontend guidance:

- keep report lists and library filters server-rendered where practical
- use client components only for forms and interactive filters
- avoid re-implementing ranking or aggregation logic in the Next.js layer

### Testing Strategy

Backend tests:

1. connector contract tests for Instagram Reels, Twitter/X, and Reddit with mocked responses
2. report scheduling and recurrence unit tests
3. report execution tests with mocked connectors and mocked delivery adapters
4. library search tests covering field filters, tag filters, and text search
5. persistence tests for report definitions, runs, deliveries, and collections

Frontend tests:

1. report builder form validation tests
2. reports dashboard rendering tests for empty, scheduled, and failed-run states
3. library filter interaction tests
4. auth-gate tests for any protected report pages

End-to-end tests:

1. sign in
2. create a scheduled report
3. trigger a manual report run
4. inspect the report detail output
5. search the library by element field
6. verify a delivery record or dashboard snapshot appears

### Validation Commands

Define these commands during implementation and make them pass before Phase 2 is considered complete:

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

### Delivery Sequence

1. Extend the backend data model for reports, deliveries, and collections.
2. Add the remaining platform connectors behind the existing connector abstraction.
3. Implement report scheduling, execution, and delivery persistence in the backend.
4. Add pattern aggregation and report snapshot formatting.
5. Expose report and library-search APIs.
6. Build the report builder and reports dashboard in the frontend.
7. Extend the library page with searchable/filterable saved pattern views.
8. Add observability, retry handling, and delivery-state visibility.
9. Finish backend, frontend, and e2e coverage.

### Risks And Mitigations

1. Platform APIs may diverge or rate limit more aggressively than TikTok and YouTube Shorts.
   - Mitigation: keep all platform adapters behind the same connector interface and preserve partial-failure behavior.
2. Scheduled report delivery can become a retry and duplication problem.
   - Mitigation: persist report runs and delivery state separately, and make report execution idempotent per run key.
3. Library search can become slow if it relies on broad text scans only.
   - Mitigation: start with Postgres text search and indexed element fields, then revisit embeddings in Phase 3 if needed.
4. PDF export can delay the core feature if treated as a first-class dependency.
   - Mitigation: make PDF export optional in the delivery pipeline and do not let it block dashboard or email delivery.
5. Cross-clip pattern detection can drift toward a complex intelligence layer too early.
   - Mitigation: keep Phase 2 aggregation shallow and deterministic, leaving semantic intelligence for Phase 3.

### Exit Criteria

Phase 2 is complete when:

1. A signed-in user can run searches across all five PRD platforms.
2. The user can configure a recurring report for a niche or account list.
3. The system generates and stores scheduled report runs with delivery status.
4. The user can search the saved library by element fields or pattern tags.
5. The UI shows report history and report detail output without manual recomputation.
6. Core backend, frontend, and e2e validation commands pass.
