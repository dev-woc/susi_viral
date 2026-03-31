from __future__ import annotations

from app.schemas.report import ReportContentDNAData, ReportPlatform
from app.services.reports.base import ReportNormalizedClip


class ReportContentDNAExtractor:
    async def extract(
        self,
        clip: ReportNormalizedClip,
        *,
        query_text: str,
        virality_score: float,
    ) -> ReportContentDNAData:
        combined_text = " ".join(
            part
            for part in [clip.title, clip.description or "", clip.transcript or "", query_text]
            if part
        ).lower()
        hook = self._select_hook(clip)
        format_name = clip.format_hint or self._select_format(combined_text)
        emotion = self._select_emotion(combined_text)
        structure = self._select_structure(clip, format_name)
        cta = self._select_cta(combined_text)
        pattern_tags = self._build_pattern_tags(clip, hook, format_name, emotion)
        niche = self._select_niche(query_text, combined_text)
        confidence = 0.82 if clip.transcript else 0.65
        return ReportContentDNAData(
            clip_id=clip.platform_clip_id,
            source_url=clip.source_url,
            platform=ReportPlatform(clip.platform.value),
            virality_score=virality_score,
            posted_at=clip.posted_at,
            niche=niche,
            hook=hook,
            format=format_name,
            emotion=emotion,
            structure=structure,
            cta=cta,
            replication_notes=(
                f"Replicate the pacing, framing, and opening beat of {clip.platform.value} clip "
                f"{clip.platform_clip_id}."
            ),
            pattern_tags=pattern_tags,
            confidence=confidence,
        )

    def _select_niche(self, query_text: str, combined_text: str) -> str | None:
        query_terms = [term for term in query_text.replace("#", " ").split() if term]
        if query_terms:
            return query_terms[0].lower()[:48]
        words = [word for word in combined_text.replace("#", " ").split() if word.isalnum()]
        if words:
            return words[0][:48]
        return None

    def _select_hook(self, clip: ReportNormalizedClip) -> str:
        if clip.transcript:
            sentence = clip.transcript.split(".")[0].strip()
            if sentence:
                return sentence[:200]
        return f"{clip.title} - open with a clear payoff in the first second."

    def _select_format(self, text: str) -> str:
        candidates = [
            "listicle",
            "before_after",
            "tutorial",
            "screen_recording",
            "storytime",
            "talking_head",
            "voiceover_b_roll",
        ]
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
            "humor": ["funny", "laugh", "joke", "silly"],
            "inspiration": ["motivated", "inspire", "dream", "build"],
        }
        for emotion, keywords in mapping.items():
            if any(keyword in text for keyword in keywords):
                return emotion
        return "curiosity"

    def _select_structure(self, clip: ReportNormalizedClip, format_name: str) -> str:
        if clip.transcript:
            return "hook -> context -> proof -> payoff -> CTA"
        return f"hook -> {format_name} -> proof -> CTA"

    def _select_cta(self, text: str) -> str:
        if "comment" in text:
            return "Ask viewers to comment with their own version."
        if "save" in text:
            return "Tell viewers to save the clip for later."
        if "follow" in text:
            return "Invite viewers to follow for the next part."
        if "share" in text:
            return "Invite viewers to share it with a teammate."
        return "Use a soft CTA that points to the next action."

    def _build_pattern_tags(
        self,
        clip: ReportNormalizedClip,
        hook: str,
        format_name: str,
        emotion: str,
    ) -> list[str]:
        first_hook_token = hook.split(" ")[0].lower() if hook else "unknown"
        return [
            f"platform:{clip.platform.value}",
            f"format:{format_name}",
            f"emotion:{emotion}",
            f"hook:{first_hook_token}",
        ]
