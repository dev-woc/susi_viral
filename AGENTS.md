# AGENTS.md

This repository is being used as a planning scaffold for the Viral Content Agent. The source of truth for product scope is the PRD PDF at `.claude/viral-content-agent-prd.md.pdf`.

## Working Agreement

- Treat `.claude/` as project context, not dead Claude-only metadata.
- When a user references a command name that matches a file in `.claude/commands/`, read that command file first and follow its workflow as closely as possible in Codex.
- When a user references a skill name that matches a directory in `.claude/skills/`, read that skill's `SKILL.md` and use it for that turn.
- Prefer adapting existing `.claude` workflows over inventing parallel conventions.
- Use `AGENTS.md` as the Codex-facing equivalent of a repo `CLAUDE.md`.

## Local Skill Mapping

If the user explicitly names one of these skills, open the matching file and follow it:

- `agent-browser` -> `.claude/skills/agent-browser/SKILL.md`
- `e2e-test` -> `.claude/skills/e2e-test/SKILL.md`
- `senior-prompt-engineer` -> `.claude/skills/senior-prompt-engineer/SKILL.md`
- `webapp-testing` -> `.claude/skills/webapp-testing/SKILL.md`

Do not preload all skill references. Load only the skill that is actually referenced by the user or clearly required by the task.

## Command Mapping

If the user references one of these command names, use the corresponding file as the task contract:

- `prime` -> `.claude/commands/prime.md`
- `plan-feature` -> `.claude/commands/plan-feature.md`
- `execute` -> `.claude/commands/execute.md`
- `create-prd` -> `.claude/commands/create-prd.md`
- `create-rules` -> `.claude/commands/create-rules.md`
- `init-project` -> `.claude/commands/init-project.md`
- `commit` -> `.claude/commands/commit.md`

For `plan-feature`, write a concrete plan document under `plans/` unless the user asks for another location.

## Project Context

- Product: Viral Content Agent
- Current phase to prioritize: Phase 1 MVP from the PRD
- Phase 1 goal: on-demand search plus element extraction for TikTok and YouTube Shorts
- Intended stack from the PRD:
  - Backend: FastAPI
  - Agent orchestration: LangGraph
  - Database: Postgres, with Neon recommended
  - Queue: Celery plus Redis
  - Frontend: Next.js with Tailwind
  - Auth: Clerk or Supabase Auth
  - LLM extraction: Claude Sonnet via API

## Planning Rules For This Repo

- The repo currently contains planning assets only. Do not assume an application already exists.
- Plans should distinguish between existing assets and proposed files to create.
- When external docs are needed, prefer official documentation.
- When the PRD and a command template disagree, the PRD wins on product scope and the command template wins on document shape.
