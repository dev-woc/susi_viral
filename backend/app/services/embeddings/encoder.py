from __future__ import annotations

from hashlib import sha256

from app.db.models.content_dna import ContentDNA


class EmbeddingEncoder:
    def __init__(self, dimension: int = 16) -> None:
        self.dimension = dimension

    def build_text(self, content_dna: ContentDNA) -> str:
        parts = [
            content_dna.platform,
            content_dna.niche or "",
            content_dna.hook or "",
            content_dna.format or "",
            content_dna.emotion or "",
            content_dna.structure or "",
            content_dna.cta or "",
            content_dna.replication_notes or "",
            " ".join(tag.name for tag in content_dna.pattern_tags),
        ]
        return " | ".join(part for part in parts if part)

    def encode_text(self, text: str) -> list[float]:
        vector = [0.0 for _ in range(self.dimension)]
        for token in text.lower().split():
            digest = sha256(token.encode("utf-8")).digest()
            for index in range(self.dimension):
                vector[index] += digest[index] / 255.0
        norm = sum(value * value for value in vector) ** 0.5 or 1.0
        return [round(value / norm, 6) for value in vector]

    def encode_content_dna(self, content_dna: ContentDNA) -> list[float]:
        return self.encode_text(self.build_text(content_dna))
