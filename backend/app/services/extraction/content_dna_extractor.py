from __future__ import annotations

from collections import Counter
from typing import Any

from pydantic import ValidationError

from app.core.config import Settings
from app.schemas.content_dna import ContentDNAData, PatternTagData
from app.services.connectors.base import NormalizedClip
from app.services.extraction.claude_client import ClaudeClient


class ContentDNAExtractor:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.claude_client = ClaudeClient(settings)

    async def extract(self, clip: NormalizedClip, virality_score: float) -> ContentDNAData:
        payload = await self.claude_client.generate(clip)
        if payload is not None:
            candidate = self._coerce_payload(payload, clip, virality_score)
            if candidate is not None:
                return candidate
        return self._fallback_extract(clip, virality_score)

    def _coerce_payload(
        self, payload: dict[str, Any], clip: NormalizedClip, virality_score: float
    ) -> ContentDNAData | None:
        try:
            payload.setdefault("schema_version", "1.0")
            payload.setdefault("clip_id", clip.platform_clip_id)
            payload.setdefault("source_url", clip.source_url)
            payload.setdefault("platform", clip.platform.value)
            payload.setdefault("virality_score", virality_score)
            payload.setdefault("posted_at", clip.posted_at)
            payload.setdefault("pattern_tags", [])
            payload.setdefault("confidence", 0.85)
            return ContentDNAData.model_validate(payload)
        except ValidationError:
            return None

    def _fallback_extract(self, clip: NormalizedClip, virality_score: float) -> ContentDNAData:
        transcript = clip.transcript or ""
        combined_text = " ".join(part for part in [clip.title, clip.description or "", transcript] if part).lower()
        niche = self._select_niche(combined_text)
        hook = self._select_hook(clip, transcript)
        format_name = clip.format_hint or self._select_format(combined_text)
        emotion = self._select_emotion(combined_text)
        structure = self._select_structure(clip, transcript, format_name)
        cta = self._select_cta(combined_text)
        pattern_tags = self._build_pattern_tags(clip, hook, format_name, emotion)
        confidence = 0.74 if transcript else 0.61
        return ContentDNAData(
            schema_version="1.0",
            clip_id=clip.platform_clip_id,
            source_url=clip.source_url,
            platform=clip.platform,
            virality_score=virality_score,
            posted_at=clip.posted_at,
            niche=niche,
            hook=hook,
            format=format_name,
            emotion=emotion,
            structure=structure,
            cta=cta,
            replication_notes=(
                f"Replicate the pacing and framing of {clip.platform.value} clip {clip.platform_clip_id}."
            ),
            pattern_tags=pattern_tags,
            confidence=confidence,
        )

    def _select_niche(self, text: str) -> str | None:
        words = [word for word in text.replace("#", " ").split() if word.isalnum()]
        if not words:
            return None
        return words[0][:48]

    def _select_hook(self, clip: NormalizedClip, transcript: str) -> str:
        if transcript:
            sentence = transcript.split(".")[0].strip()
            if sentence:
                return sentence[:200]
        return f"{clip.title} - open with a clear payoff in the first second."

    def _select_format(self, text: str) -> str:
        candidates = ["listicle", "before_after", "tutorial", "screen_recording", "storytime"]
        for candidate in candidates:
            if candidate.replace("_", " ") in text:
                return candidate
        return "tutorial"

    def _select_emotion(self, text: str) -> str:
        mapping = {
            "curiosity": ["secret", "hidden", "why", "how", "unexpected"],
            "urgency": ["now", "today", "before", "fast"],
            "delight": ["easy", "simple", "quick", "win"],
            "confidence": ["proven", "guaranteed", "worked"],
            "surprise": ["shock", "wild", "crazy", "insane"],
        }
        for emotion, keywords in mapping.items():
            if any(keyword in text for keyword in keywords):
                return emotion
        return "curiosity"

    def _select_structure(self, clip: NormalizedClip, transcript: str, format_name: str) -> str:
        if transcript:
            return "hook -> context -> proof -> payoff -> CTA"
        return f"hook -> {format_name} -> proof -> CTA"

    def _select_cta(self, text: str) -> str:
        if "comment" in text:
            return "Ask viewers to comment with their own version."
        if "save" in text:
            return "Tell viewers to save the clip for later."
        if "follow" in text:
            return "Invite viewers to follow for the next part."
        return "Use a soft CTA that points to the next action."

    def _build_pattern_tags(
        self, clip: NormalizedClip, hook: str, format_name: str, emotion: str
    ) -> list[PatternTagData]:
        _ = Counter(
            [
                f"platform:{clip.platform.value}",
                f"format:{format_name}",
                f"emotion:{emotion}",
                f"hook:{hook.split(' ')[0].lower() if hook else 'unknown'}",
            ]
        )
        return [
            PatternTagData(name=f"platform:{clip.platform.value}", category="platform"),
            PatternTagData(name=f"format:{format_name}", category="format"),
            PatternTagData(name=f"emotion:{emotion}", category="emotion"),
            PatternTagData(name=f"hook:{hook.split(' ')[0].lower() if hook else 'unknown'}", category="hook"),
        ]

