from typing import List
from src.extraction.schema import MedicalGuideline

EVIDENCE_TIER_WEIGHT = {
    "Tier 1": 3,
    "Tier 2": 2,
    "Tier 3": 1,
}

class ContextBuilder:
    def __init__(self, max_snippet_chars: int = 320):
        self.max_snippet_chars = max_snippet_chars

    def build_context(self, documents: List[MedicalGuideline], max_items: int = 4) -> List[dict]:
        seen_ids = set()
        context = []

        for rank, guideline in enumerate(documents, start=1):
            if guideline.id in seen_ids:
                continue
            seen_ids.add(guideline.id)

            snippet = self._clean_snippet(guideline.text_snippet)
            context.append({
                "id": guideline.id,
                "source_name": guideline.source_name,
                "title": guideline.guideline_name,
                "category": guideline.category,
                "year": guideline.year,
                "evidence_tier": guideline.evidence_tier,
                "url": guideline.url,
                "snippet": snippet,
                "rank": rank,
                "source_type": guideline.source_type,
            })

            if len(context) >= max_items:
                break

        return context

    def _clean_snippet(self, text: str) -> str:
        if not text:
            return ""

        cleaned = " ".join(text.split())
        if len(cleaned) <= self.max_snippet_chars:
            return cleaned

        truncated = cleaned[: self.max_snippet_chars].rstrip()
        if " " in truncated:
            truncated = truncated.rsplit(" ", 1)[0]
        return f"{truncated}..."
