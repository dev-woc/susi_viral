# Feature: Phase 1 MVP Search And Extraction

The following plan is based on the PRD at `.claude/viral-content-agent-prd.md.pdf` and the `plan-feature` workflow in `.claude/commands/plan-feature.md`.

This repository does not yet contain application code, so this document defines the Phase 1 implementation target, the initial repository shape, and the mandatory references for the implementation pass.

## Feature Description

Phase 1 delivers the first usable version of the Viral Content Agent: a user can enter a niche, keyword, hashtag, or account query, run an on-demand search across TikTok and YouTube Shorts, receive a ranked top-10 result set, inspect a structured `ContentDNA` breakdown for each clip, and manually save a clip to a library for later reuse.

## User Story

As a creator or strategist
I want to search TikTok and YouTube Shorts for viral clips in my niche and receive structured `ContentDNA` breakdowns
So that I can identify repeatable creative patterns without manually reviewing large volumes of content

## Problem Statement

Manual viral-content research is slow, inconsistent, and difficult to reuse. Topic-level trend tools do not explain why specific clips worked, and they do not store those mechanics in a structured library that can be searched later.

## Solution Statement

Build a Phase 1 MVP with:

- two platform connectors: TikTok and YouTube Shorts
- a FastAPI backend that executes a LangGraph search pipeline
- a Claude-powered extraction service that fills a normalized `ContentDNA` schema
- a Next.js dashboard for on-demand search and result review
- a Postgres-backed save-to-library flow for manually preserving extracted clips

The system should prioritize correctness, observability, and a clean connector abstraction so additional platforms and scheduled workflows can be added in Phase 2.

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: High
**Primary Systems Affected**: frontend dashboard, backend API, platform connector layer, ranking pipeline, LLM extraction service, persistence layer
**Dependencies**: FastAPI, LangGraph, Anthropic API, Next.js, Tailwind CSS, Postgres, Neon, SQLAlchemy or SQLModel, Alembic, Clerk, Redis, Celery

---

## CONTEXT REFERENCES

### Relevant Codebase Files IMPORTANT: YOU MUST READ THESE FILES BEFORE IMPLEMENTING!

The repo is currently planning-only. These are the mandatory context files that exist today:

- `.claude/viral-content-agent-prd.md.pdf` - Product scope, roadmap, risks, data model, and Phase 1 exit criteria
- `.claude/commands/plan-feature.md` - Required structure and expectations for planning artifacts
- `AGENTS.md` - Codex-specific workflow rules for this repository

### New Files to Create

Recommended initial repository layout for implementation:

- `backend/pyproject.toml` - Python dependency and tooling configuration
- `backend/app/main.py` - FastAPI entry point
- `backend/app/api/routes/search.py` - On-demand search endpoint
- `backend/app/api/routes/library.py` - Save-to-library and list-library endpoints
- `backend/app/core/config.py` - environment loading and settings
- `backend/app/core/logging.py` - structured logging setup
- `backend/app/db/base.py` - SQLAlchemy metadata and session setup
- `backend/app/db/models/raw_clip.py` - raw connector result persistence
- `backend/app/db/models/content_dna.py` - extracted clip schema persistence
- `backend/app/db/models/library_item.py` - saved clip/library records
- `backend/app/db/models/search_query.py` - search history records
- `backend/app/db/migrations/` - Alembic migrations
- `backend/app/schemas/search.py` - request and response models
- `backend/app/schemas/content_dna.py` - typed `ContentDNA` contract
- `backend/app/services/connectors/base.py` - common connector interface
- `backend/app/services/connectors/tiktok.py` - TikTok connector implementation
- `backend/app/services/connectors/youtube_shorts.py` - YouTube Shorts connector implementation
- `backend/app/services/ranking/virality.py` - per-platform score normalization and ranking
- `backend/app/services/extraction/claude_client.py` - Anthropic client wrapper
- `backend/app/services/extraction/content_dna_extractor.py` - schema-driven extraction logic
- `backend/app/services/graph/search_graph.py` - LangGraph pipeline definition
- `backend/app/services/graph/state.py` - graph state types
- `backend/app/tasks/` - Celery bootstrap only; scheduled jobs can remain stubbed in Phase 1
- `backend/tests/` - backend unit and integration tests
- `frontend/package.json` - Next.js app package configuration
- `frontend/app/page.tsx` - search landing page
- `frontend/app/search/page.tsx` - results page if separate from landing
- `frontend/app/library/page.tsx` - saved clips page
- `frontend/app/layout.tsx` - global shell and auth provider
- `frontend/components/search-form.tsx` - search input UI
- `frontend/components/results-table.tsx` - ranked clip list
- `frontend/components/content-dna-card.tsx` - structured breakdown display
- `frontend/components/save-to-library-button.tsx` - manual save action
- `frontend/lib/api.ts` - typed backend fetch client
- `frontend/middleware.ts` or `frontend/proxy.ts` - Clerk route protection depending on Next.js version
- `docker-compose.yml` - local Postgres and Redis for development
- `.env.example` - required environment variables
- `README.md` - local setup and architecture overview

### Relevant Documentation YOU SHOULD READ THESE BEFORE IMPLEMENTING!

- [FastAPI async docs](https://fastapi.tiangolo.com/async/)
  - Specific section: using `async def` for I/O-bound handlers
  - Why: the search pipeline will be network-heavy and should use async request flow
- [Next.js backend-for-frontend guide](https://nextjs.org/docs/app/guides/backend-for-frontend)
  - Specific section: use Server Components for reads and avoid unnecessary Route Handler hops
  - Why: prevents duplicating backend orchestration inside the frontend
- [Next.js Server Actions docs](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)
  - Specific section: use Server Actions only for mutations
  - Why: supports save-to-library without overloading the frontend with client-side fetch logic
- [LangGraph docs](https://docs.langchain.com/oss/python/langgraph)
  - Specific section: stateful graphs and parallel execution
  - Why: the PRD explicitly calls for a graph pipeline from fetch to format
- [Anthropic tool use docs](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use)
  - Specific section: JSON-schema tool definitions and tool prompting
  - Why: useful if extraction is implemented through schema-constrained tool calls
- [Anthropic vision docs](https://docs.anthropic.com/en/docs/build-with-claude/vision)
  - Specific section: image limits and image-first prompting
  - Why: Phase 1 extraction may need frame samples when transcript text is unavailable
- [Clerk Next.js App Router quickstart](https://clerk.com/docs/nextjs/getting-started/quickstart)
  - Specific section: middleware and provider setup
  - Why: PRD requires personal and team-ready auth, and Clerk is the fastest path
- [Clerk organizations guide](https://clerk.com/docs/guides/organizations/create-and-manage)
  - Specific section: organization creation and switching
  - Why: Phase 1 should avoid blocking future team workspaces
- [Neon connection guide](https://neon.com/docs/get-started-with-neon/connect-neon)
  - Specific section: pooled vs direct Postgres connection strings
  - Why: informs production-ready database configuration

### Patterns to Follow

Because there is no existing app code yet, establish these project patterns at implementation start and keep them consistent:

**Naming Conventions:** snake_case for Python modules, kebab-case only where a tool requires it, PascalCase for React component names, singular model names like `ContentDNA` and `LibraryItem`

**Error Handling:** connector failures should degrade per platform and return partial results with explicit platform error metadata instead of failing the full search request

**Logging Pattern:** assign a `search_id` to every request and include it in connector, ranking, extraction, and persistence logs

**Other Relevant Patterns:**

- keep platform connectors behind a single interface with normalized output
- persist raw platform payloads separately from extracted `ContentDNA`
- treat LLM extraction as idempotent for a given `raw_clip`
- version the `ContentDNA` schema so extraction improvements do not silently break saved records
- keep virality scoring per-platform and configurable, even if Phase 1 exposes only minimal weight tuning

---

## IMPLEMENTATION PLAN

### Architecture Decisions

1. Use a split frontend and backend layout from day one.
2. Keep all platform-specific fetch logic inside backend connectors.
3. Use LangGraph only for the search orchestration path, not for simple CRUD endpoints.
4. Use Postgres as the system of record for searches, raw clips, extracted `ContentDNA`, and library saves.
5. Include Redis and Celery setup in Phase 1 only as scaffolding for scheduled reports; do not let scheduled jobs delay MVP delivery.
6. Use Clerk for authentication because the PRD already anticipates personal and team workspaces, and Clerk provides a direct Next.js integration path.

### Scope For Phase 1

In scope:

- user auth
- search form with query, platforms, timeframe, and minimum virality threshold
- TikTok connector
- YouTube Shorts connector
- normalized virality ranking
- top-10 result formatting
- `ContentDNA` extraction per returned clip
- manual save to library
- library list view
- search history persistence
- basic observability and retry handling

Out of scope:

- Instagram Reels, X, Reddit connectors
- scheduled report execution
- email delivery
- PDF report export
- vector search
- pattern delta tracking
- auto-generated content briefs
- team collaboration UX beyond selecting an auth provider that can support organizations later

### Data Model v1

Create these first-class entities:

1. `User`
2. `Workspace`
3. `SearchQuery`
4. `RawClip`
5. `ContentDNA`
6. `LibraryItem`
7. `PatternTag`

Minimum relationships:

- a `User` belongs to one active `Workspace`
- a `SearchQuery` belongs to a `Workspace`
- a `RawClip` belongs to a `SearchQuery`
- a `ContentDNA` belongs one-to-one to a `RawClip`
- a `LibraryItem` references a `ContentDNA` and a `Workspace`
- `PatternTag` is many-to-many with `ContentDNA`

Phase 1 simplification:

- support a single personal workspace per user in the UI
- keep schema workspace-ready so organizations can be added without migration churn

### API Surface

Initial backend endpoints:

- `POST /api/search`
  - accepts query, platforms, timeframe, virality threshold, optional format filters
  - returns ranked clips and extracted `ContentDNA`
- `GET /api/search/{search_id}`
  - returns stored search results and status
- `POST /api/library/items`
  - saves a clip extraction to the library
- `GET /api/library/items`
  - lists saved items with filters
- `GET /api/health`
  - service health

### Search Pipeline

Implement the LangGraph workflow as:

1. `PlatformFetcher`
2. `Normalizer`
3. `ViralityRanker`
4. `ContentSampler`
5. `ElementExtractor`
6. `PatternAggregatorLite`
7. `ResultFormatter`

Node expectations:

1. `PlatformFetcher`
   - runs TikTok and YouTube fetches in parallel
   - returns normalized connector payloads and per-platform failures
2. `Normalizer`
   - maps platform-specific metrics into a shared scoring input contract
3. `ViralityRanker`
   - computes platform-relative virality scores
   - filters out clips under the threshold
4. `ContentSampler`
   - selects top clips for extraction
   - caches clip metadata to avoid duplicate reprocessing
5. `ElementExtractor`
   - calls Anthropic with transcript text when available
   - includes frame samples when text is missing or weak
   - validates output against the `ContentDNA` schema
6. `PatternAggregatorLite`
   - derives simple summary counts such as repeated hook and format types
7. `ResultFormatter`
   - prepares a UI-ready response

### `ContentDNA` Schema Requirements

The schema must include at minimum:

- `clip_id`
- `source_url`
- `platform`
- `virality_score`
- `posted_at`
- `niche`
- `hook`
- `format`
- `emotion`
- `structure`
- `cta`
- `replication_notes`
- `pattern_tags`

Implementation rule:

- treat all extraction fields as explicit nullable or required values
- never rely on free-form JSON without schema validation

### Frontend Experience

Phase 1 UI should include:

1. Search page
   - query input
   - timeframe select
   - platform toggles
   - virality threshold input
2. Results experience
   - ranked result list
   - clip metadata summary
   - expandable `ContentDNA` card
   - save-to-library action
3. Library page
   - saved clips
   - filter by platform and hook type

Frontend guidance:

- keep reads server-rendered where practical
- use client components only for interactive controls
- avoid duplicating backend business logic in the Next.js layer

### Testing Strategy

Backend tests:

1. connector contract tests with mocked external APIs
2. virality scoring unit tests per platform
3. extraction schema-validation tests with canned model responses
4. search pipeline integration tests with mocked connectors and mocked Anthropic responses
5. persistence tests for library saves and search history

Frontend tests:

1. search form validation tests
2. result rendering tests for populated and partial-result states
3. save-to-library interaction tests
4. auth gate tests for protected pages

End-to-end tests:

1. sign in
2. run search
3. inspect ranked results
4. open a `ContentDNA` card
5. save a clip to library
6. verify library entry appears

### Validation Commands

Define these commands during implementation and make them pass before Phase 1 is considered complete:

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

1. Scaffold backend, frontend, local infrastructure, and environment configuration.
2. Define database schema and run first migration.
3. Build auth and workspace plumbing.
4. Implement connector interface and YouTube Shorts connector first.
5. Implement TikTok connector behind the same contract.
6. Build virality scorer and LangGraph search flow.
7. Add `ContentDNA` extraction and schema validation.
8. Expose search API and persist search results.
9. Build search UI and results rendering.
10. Add manual save-to-library flow and library page.
11. Add observability, retries, and partial-failure handling.
12. Finish test coverage and e2e verification.

### Risks And Mitigations

1. TikTok data access may be unstable or gated.
   - Mitigation: design the TikTok connector behind a replaceable adapter and keep fallback ingestion options isolated from the rest of the system.
2. LLM extraction quality may vary on short or low-context clips.
   - Mitigation: validate against a strict schema, store extraction confidence, and allow re-extraction without mutating raw clip data.
3. Virality scores can be misleading across platforms.
   - Mitigation: normalize within platform and timeframe, not globally.
4. Search latency may exceed the PRD target of under two minutes.
   - Mitigation: parallelize fetch and extraction, cap top-N extraction set, and cache recent raw clips.
5. Premature Phase 2 scaffolding can slow MVP delivery.
   - Mitigation: include only minimal Redis and Celery bootstrap and defer scheduled job behavior.

### Exit Criteria

Phase 1 is complete when:

1. A signed-in user can run an on-demand search against TikTok and YouTube Shorts.
2. The system returns up to 10 ranked clips with per-clip `ContentDNA`.
3. The UI shows a usable results list and detailed `ContentDNA` cards.
4. A user can manually save a result to the library and retrieve it later.
5. Connector failures surface as partial-result warnings instead of full-request failures.
6. Core backend, frontend, and e2e validation commands pass.
