from __future__ import annotations

from app.core.config import get_settings
from app.db.models.content_dna import ContentDNA
from app.schemas.content_dna import ContentDNAResponse
from app.schemas.search import SearchResult


def build_search_result_from_content_dna(content_dna: ContentDNA) -> SearchResult:
    raw_clip = content_dna.raw_clip
    return SearchResult(
        clip_id=content_dna.clip_id,
        source_url=content_dna.source_url,
        platform=content_dna.platform,
        title=raw_clip.title if raw_clip is not None else content_dna.hook or "Saved clip",
        author_handle=raw_clip.author_handle if raw_clip is not None else None,
        thumbnail_url=raw_clip.thumbnail_url if raw_clip is not None else None,
        posted_at=content_dna.posted_at,
        virality_score=content_dna.virality_score,
        transcript_excerpt=raw_clip.transcript_excerpt if raw_clip is not None else None,
        content_dna=ContentDNAResponse(
            schema_version=content_dna.schema_version,
            clip_id=content_dna.clip_id,
            source_url=content_dna.source_url,
            platform=content_dna.platform,
            virality_score=content_dna.virality_score,
            posted_at=content_dna.posted_at,
            niche=content_dna.niche,
            hook=content_dna.hook,
            format=content_dna.format,
            emotion=content_dna.emotion,
            structure=content_dna.structure,
            cta=content_dna.cta,
            replication_notes=content_dna.replication_notes,
            pattern_tags=[tag.value for tag in content_dna.pattern_tags],
        ),
    )
