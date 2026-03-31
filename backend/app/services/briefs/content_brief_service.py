from __future__ import annotations

import asyncio
import json
import logging
from collections import Counter
from functools import lru_cache
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.bootstrap import ensure_default_user, ensure_default_workspace
from app.db.models.content_brief import ContentBrief
from app.db.models.content_dna import ContentDNA
from app.db.models.raw_clip import RawClip
from app.db.models.report_delivery import ReportDelivery
from app.db.models.search_query import SearchQuery
from app.db.models.scheduled_report import ReportRun
from app.db.models.workspace_membership import WorkspaceMembership
from app.schemas.brief import ContentBriefCreateRequest, ContentBriefListResponse, ContentBriefRead
from app.schemas.content_dna import ContentDNARead, PatternTagData, PlatformName
from app.services.identity import RequestIdentity

try:  # pragma: no cover - optional runtime dependency
    from anthropic import Anthropic
except Exception:  # pragma: no cover - fallback if SDK is unavailable
    Anthropic = None

logger = logging.getLogger(__name__)


class ContentBriefService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = (
            Anthropic(api_key=self.settings.anthropic_api_key)
            if Anthropic and self.settings.anthropic_api_key
            else None
        )

    def create_brief(
        self,
        session: Session,
        payload: ContentBriefCreateRequest,
        identity: RequestIdentity | None = None,
    ) -> ContentBriefRead:
        workspace, user = self._resolve_identity(session, identity)
        selected_clips = self._load_selected_clips(session, workspace.id, payload.selected_content_dna_ids)
        report_run = self._load_report_run(session, workspace.id, payload.report_run_id)
        generation = asyncio.run(
            self._generate_brief(
                payload=payload,
                workspace_name=workspace.name,
                selected_clips=selected_clips,
                report_run=report_run,
            )
        )

        brief = ContentBrief(
            brief_id=uuid4().hex,
            workspace_id=workspace.id,
            user_id=user.id,
            report_run_id=report_run.id if report_run is not None else None,
            title=payload.title,
            objective=payload.objective,
            audience=payload.audience,
            tone=payload.tone,
            summary=generation["summary"],
            recommended_shots=generation["recommended_shots"],
            selected_content_dna_ids=payload.selected_content_dna_ids,
            pattern_tags=generation["pattern_tags"],
            prompt_snapshot=generation["prompt_snapshot"],
            source_snapshot=generation["source_snapshot"],
        )
        session.add(brief)
        session.commit()
        session.refresh(brief)
        return self._brief_read(brief, selected_clips)

    def list_briefs(
        self,
        session: Session,
        identity: RequestIdentity | None = None,
    ) -> ContentBriefListResponse:
        workspace, _ = self._resolve_identity(session, identity)
        rows = list(
            session.scalars(
                select(ContentBrief)
                .where(ContentBrief.workspace_id == workspace.id)
                .order_by(ContentBrief.created_at.desc())
            )
        )
        return ContentBriefListResponse(items=[self._brief_read(row) for row in rows])

    def get_brief(
        self,
        session: Session,
        brief_id: str,
        identity: RequestIdentity | None = None,
    ) -> ContentBriefRead | None:
        workspace, _ = self._resolve_identity(session, identity)
        brief = session.scalar(
            select(ContentBrief).where(
                ContentBrief.workspace_id == workspace.id,
                ContentBrief.brief_id == brief_id,
            )
        )
        if brief is None:
            return None
        selected_clips = self._load_selected_clips(session, workspace.id, list(brief.selected_content_dna_ids))
        return self._brief_read(brief, selected_clips)

    async def _generate_brief(
        self,
        *,
        payload: ContentBriefCreateRequest,
        workspace_name: str,
        selected_clips: list[ContentDNARead],
        report_run: ReportRun | None,
    ) -> dict[str, object]:
        if self._client is not None:
            try:
                return await asyncio.to_thread(
                    self._generate_via_anthropic,
                    payload,
                    workspace_name,
                    selected_clips,
                    report_run,
                )
            except Exception as exc:  # pragma: no cover - network/client failure fallback
                logger.warning("anthropic brief generation failed, falling back to deterministic brief", extra={"error": str(exc)})

        return self._generate_deterministic_brief(payload, workspace_name, selected_clips, report_run)

    def _generate_via_anthropic(
        self,
        payload: ContentBriefCreateRequest,
        workspace_name: str,
        selected_clips: list[ContentDNARead],
        report_run: ReportRun | None,
    ) -> dict[str, object]:
        prompt = self._build_prompt(payload, workspace_name, selected_clips, report_run)
        response = self._client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=1200,
            temperature=0.0,
            system=(
                "Generate a structured content brief from saved short-form video patterns. "
                "Return only valid JSON with summary, recommended_shots, pattern_tags, and notes."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(getattr(block, "text", "") for block in getattr(response, "content", []))
        if not text:
            raise ValueError("anthropic brief response was empty")
        payload_data = json.loads(text)
        return self._normalize_generation_payload(payload_data, payload, workspace_name, selected_clips, report_run)

    def _generate_deterministic_brief(
        self,
        payload: ContentBriefCreateRequest,
        workspace_name: str,
        selected_clips: list[ContentDNARead],
        report_run: ReportRun | None,
    ) -> dict[str, object]:
        return self._normalize_generation_payload(
            {},
            payload,
            workspace_name,
            selected_clips,
            report_run,
        )

    def _normalize_generation_payload(
        self,
        payload_data: dict[str, object],
        payload: ContentBriefCreateRequest,
        workspace_name: str,
        selected_clips: list[ContentDNARead],
        report_run: ReportRun | None,
    ) -> dict[str, object]:
        pattern_counts: Counter[str] = Counter()
        platform_counts: Counter[str] = Counter()
        hook_fragments: list[str] = []
        format_fragments: list[str] = []
        for clip in selected_clips:
            platform_counts[clip.platform.value] += 1
            if clip.hook:
                hook_fragments.append(clip.hook)
            if clip.format:
                format_fragments.append(clip.format)
            for tag in clip.pattern_tags:
                pattern_counts[tag.name] += 1

        report_summary = {}
        report_patterns = {}
        if report_run is not None:
            report_summary = dict(report_run.pattern_summary or {})
            report_patterns = dict(report_run.pattern_deltas or {})

        top_tags = [tag for tag, _count in pattern_counts.most_common(5)]
        if not top_tags and report_summary:
            top_tags = sorted(report_summary, key=report_summary.get, reverse=True)[:5]

        summary = payload_data.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            summary = self._build_summary(
                payload=payload,
                workspace_name=workspace_name,
                selected_clips=selected_clips,
                top_tags=top_tags,
                report_summary=report_summary,
                report_patterns=report_patterns,
            )

        recommended_shots = payload_data.get("recommended_shots")
        if not isinstance(recommended_shots, list) or not recommended_shots:
            recommended_shots = self._build_recommended_shots(
                payload=payload,
                selected_clips=selected_clips,
                top_tags=top_tags,
                hook_fragments=hook_fragments,
                format_fragments=format_fragments,
                report_patterns=report_patterns,
            )

        pattern_tags = payload_data.get("pattern_tags")
        if not isinstance(pattern_tags, list) or not pattern_tags:
            pattern_tags = top_tags or [
                *(f"platform:{platform}" for platform in platform_counts.keys()),
                *(f"format:{value}" for value in sorted(set(format_fragments))[:2]),
            ]

        prompt_snapshot = payload_data.get("prompt_snapshot")
        if not isinstance(prompt_snapshot, dict):
            prompt_snapshot = {
                "workspace_name": workspace_name,
                "selected_content_dna_ids": list(payload.selected_content_dna_ids),
                "report_run_id": report_run.id if report_run is not None else None,
            }

        source_snapshot = payload_data.get("source_snapshot")
        if not isinstance(source_snapshot, dict):
            source_snapshot = {
                "selected_clips": [clip.model_dump(mode="json") for clip in selected_clips],
                "report_summary": report_summary,
                "report_pattern_deltas": report_patterns,
            }

        return {
            "summary": summary,
            "recommended_shots": [str(item) for item in recommended_shots],
            "pattern_tags": [str(item) for item in pattern_tags],
            "prompt_snapshot": prompt_snapshot,
            "source_snapshot": source_snapshot,
        }

    def _build_summary(
        self,
        *,
        payload: ContentBriefCreateRequest,
        workspace_name: str,
        selected_clips: list[ContentDNARead],
        top_tags: list[str],
        report_summary: dict[str, int],
        report_patterns: dict[str, int],
    ) -> str:
        platform_counts = Counter(clip.platform.value for clip in selected_clips)
        platform_text = ", ".join(
            f"{platform} ({count})" for platform, count in platform_counts.most_common()
        )
        tag_text = ", ".join(top_tags[:3]) if top_tags else "the strongest saved patterns"
        trend_text = ""
        if report_patterns:
            positive = [key for key, value in report_patterns.items() if value > 0][:3]
            if positive:
                trend_text = f" Trend lift is visible in {', '.join(positive)}."
        elif report_summary:
            trend_text = f" Report history highlights {len(report_summary)} recurring pattern signal(s)."
        return (
            f"{payload.title} for {workspace_name} targets {payload.audience} using "
            f"{len(selected_clips)} clip(s) across {platform_text or 'no platform data'}."
            f" The draft centers on {tag_text}.{trend_text}"
        )

    def _build_recommended_shots(
        self,
        *,
        payload: ContentBriefCreateRequest,
        selected_clips: list[ContentDNARead],
        top_tags: list[str],
        hook_fragments: list[str],
        format_fragments: list[str],
        report_patterns: dict[str, int],
    ) -> list[str]:
        lead_hook = hook_fragments[0] if hook_fragments else f"State the payoff for {payload.audience}"
        lead_format = format_fragments[0] if format_fragments else "voiceover or talking-head"
        top_tag = top_tags[0] if top_tags else "the clearest recurring hook"
        shots = [
            f"Open with: {lead_hook[:120]}",
            f"Frame the body as a {lead_format} that foregrounds {top_tag}.",
            "Cut to proof quickly and keep the first reveal before the 5-second mark.",
            f"Close with a light CTA aligned to {payload.objective.lower()[:80]}.",
        ]
        if report_patterns:
            rising = sorted(report_patterns, key=report_patterns.get, reverse=True)[:2]
            if rising:
                shots.append(f"Borrow the current upward signals: {', '.join(rising)}.")
        if selected_clips:
            shots.append(f"Reuse the pacing and structure from {selected_clips[0].clip_id}.")
        return shots

    def _build_prompt(
        self,
        payload: ContentBriefCreateRequest,
        workspace_name: str,
        selected_clips: list[ContentDNARead],
        report_run: ReportRun | None,
    ) -> str:
        return json.dumps(
            {
                "workspace_name": workspace_name,
                "title": payload.title,
                "objective": payload.objective,
                "audience": payload.audience,
                "tone": payload.tone,
                "selected_content_dna_ids": payload.selected_content_dna_ids,
                "report_run_id": report_run.id if report_run is not None else None,
                "selected_clips": [clip.model_dump(mode="json") for clip in selected_clips],
                "report_summary": dict(report_run.pattern_summary or {}) if report_run else {},
                "report_pattern_deltas": dict(report_run.pattern_deltas or {}) if report_run else {},
            },
            sort_keys=True,
        )

    def _load_selected_clips(
        self,
        session: Session,
        workspace_id: int,
        selected_content_dna_ids: list[int],
    ) -> list[ContentDNARead]:
        if not selected_content_dna_ids:
            return []
        rows = list(
            session.scalars(
                select(ContentDNA)
                .join(RawClip)
                .join(SearchQuery)
                .where(
                    SearchQuery.workspace_id == workspace_id,
                    ContentDNA.id.in_(selected_content_dna_ids),
                )
            )
        )
        selected: list[ContentDNARead] = []
        for row in rows:
            selected.append(
                ContentDNARead(
                    id=row.id,
                    raw_clip_id=row.raw_clip_id,
                    schema_version=row.schema_version,
                    clip_id=row.clip_id,
                    source_url=row.source_url,
                    platform=PlatformName(row.platform),
                    virality_score=row.virality_score,
                    posted_at=row.posted_at,
                    niche=row.niche,
                    hook=row.hook,
                    format=row.format,
                    emotion=row.emotion,
                    structure=row.structure,
                    cta=row.cta,
                    replication_notes=row.replication_notes,
                    pattern_tags=[
                        PatternTagData(name=tag.name, category=tag.category)
                        for tag in row.pattern_tags
                    ],
                    confidence=row.confidence,
                    created_at=row.created_at,
                )
            )
        return selected

    def _load_report_run(
        self,
        session: Session,
        workspace_id: int,
        report_run_id: int | None,
    ) -> ReportRun | None:
        if report_run_id is None:
            return None
        return (
            session.query(ReportRun)
            .join(ReportRun.scheduled_report)
            .filter(
                ReportRun.id == report_run_id,
                ReportRun.scheduled_report.has(workspace_id=workspace_id),
            )
            .one_or_none()
        )

    def _brief_read(
        self,
        brief: ContentBrief,
        selected_clips: list[ContentDNARead] | None = None,
    ) -> ContentBriefRead:
        return ContentBriefRead(
            id=brief.id,
            brief_id=brief.brief_id,
            workspace_id=brief.workspace_id,
            user_id=brief.user_id,
            report_run_id=brief.report_run_id,
            title=brief.title,
            objective=brief.objective,
            audience=brief.audience,
            tone=brief.tone,
            summary=brief.summary,
            recommended_shots=list(brief.recommended_shots or []),
            selected_content_dna_ids=list(brief.selected_content_dna_ids or []),
            pattern_tags=list(brief.pattern_tags or []),
            prompt_snapshot=dict(brief.prompt_snapshot or {}),
            source_snapshot=dict(brief.source_snapshot or {}),
            created_at=brief.created_at,
            updated_at=brief.updated_at,
            selected_clips=selected_clips or [],
        )

    def _resolve_identity(
        self,
        session: Session,
        identity: RequestIdentity | None,
    ) -> tuple[object, object]:
        if identity is not None:
            workspace = session.scalar(
                select(type(ensure_default_workspace(session, self.settings))).where(
                    type(ensure_default_workspace(session, self.settings)).id == identity.workspace_id
                )
            )
            if workspace is None:
                workspace = ensure_default_workspace(session, self.settings)
            user = session.get(type(ensure_default_user(session, self.settings, workspace)), identity.user_id)
            if user is None:
                user = ensure_default_user(session, self.settings, workspace)
            self._ensure_membership(session, workspace.id, user.id)
            return workspace, user

        workspace = ensure_default_workspace(session, self.settings)
        user = ensure_default_user(session, self.settings, workspace)
        self._ensure_membership(session, workspace.id, user.id)
        return workspace, user

    def _ensure_membership(self, session: Session, workspace_id: int, user_id: int) -> None:
        membership = session.scalar(
            select(WorkspaceMembership).where(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.user_id == user_id,
            )
        )
        if membership is None:
            session.add(
                WorkspaceMembership(workspace_id=workspace_id, user_id=user_id, role="owner")
            )
            session.commit()


@lru_cache(maxsize=1)
def get_content_brief_service() -> ContentBriefService:
    return ContentBriefService()
