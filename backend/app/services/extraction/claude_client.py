from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from app.core.config import Settings
from app.services.connectors.base import NormalizedClip

try:  # pragma: no cover - optional runtime dependency
    from anthropic import Anthropic
except Exception:  # pragma: no cover - fallback if SDK is unavailable
    Anthropic = None


class ClaudeClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self._client = Anthropic(api_key=settings.anthropic_api_key) if Anthropic and settings.anthropic_api_key else None

    async def generate(self, clip: NormalizedClip) -> dict[str, Any] | None:
        if self._client is None:
            return None

        prompt = self._build_prompt(clip)
        try:
            response = await asyncio.to_thread(
                self._client.messages.create,
                model=self.settings.anthropic_model,
                max_tokens=1024,
                temperature=0.0,
                system=(
                    "You extract structured ContentDNA from short-form video clips. "
                    "Return only valid JSON matching the requested schema."
                ),
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception:  # pragma: no cover - network/client failure fallback
            self.logger.warning("anthropic extraction failed, falling back to deterministic extraction")
            return None

        text = "".join(getattr(block, "text", "") for block in getattr(response, "content", []))
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _build_prompt(self, clip: NormalizedClip) -> str:
        return json.dumps(
            {
                "clip_id": clip.platform_clip_id,
                "platform": clip.platform.value,
                "source_url": clip.source_url,
                "title": clip.title,
                "description": clip.description,
                "transcript": clip.transcript,
                "frame_samples": clip.frame_samples,
                "view_count": clip.view_count,
                "like_count": clip.like_count,
                "comment_count": clip.comment_count,
                "share_count": clip.share_count,
            },
            sort_keys=True,
        )

