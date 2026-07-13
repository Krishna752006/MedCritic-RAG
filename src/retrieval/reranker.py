import importlib
from typing import List
from src.extraction.schema import MedicalGuideline

CROSS_ENCODER_AVAILABLE = False

try:
    if importlib.util.find_spec("sentence_transformers") is not None:
        sentence_module = importlib.import_module("sentence_transformers")
        CrossEncoder = sentence_module.CrossEncoder
        CROSS_ENCODER_AVAILABLE = True
except Exception:
    CROSS_ENCODER_AVAILABLE = False

EVIDENCE_TIER_WEIGHT = {
    "Tier 1": 3.0,
    "Tier 2": 2.0,
    "Tier 3": 1.0,
}

class HybridReranker:
    def __init__(self):
        self.available = CROSS_ENCODER_AVAILABLE
        self.model = None
        if self.available:
            try:
                self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            except Exception as e:
                print(f"Failed to load CrossEncoder reranker: {e}. Falling back.")
                self.available = False

    def _tier_weight(self, guideline: MedicalGuideline) -> float:
        for prefix, weight in EVIDENCE_TIER_WEIGHT.items():
            if guideline.evidence_tier and guideline.evidence_tier.startswith(prefix):
                return weight
        return 1.0

    def rerank(self, query: str, dense_results: List[MedicalGuideline], sparse_results: List[MedicalGuideline], top_k: int = 3) -> List[MedicalGuideline]:
        seen_ids = set()
        merged = []
        for guideline in dense_results + sparse_results:
            if guideline.id not in seen_ids:
                merged.append(guideline)
                seen_ids.add(guideline.id)

        if not merged:
            return []

        if self.available and self.model is not None:
            try:
                pairs = [[query, guideline.text_snippet] for guideline in merged]
                scores = self.model.predict(pairs)
                weighted = [
                    (score + self._tier_weight(guideline) * 0.1, guideline)
                    for score, guideline in zip(scores, merged)
                ]
                weighted.sort(key=lambda item: item[0], reverse=True)
                return [item[1] for item in weighted[:top_k]]
            except Exception as e:
                print(f"CrossEncoder reranking error: {e}. Using fusion fallback.")

        scored = []
        for guideline in merged:
            score = 0.0
            if guideline in dense_results:
                score += 1.0 / (dense_results.index(guideline) + 1)
            if guideline in sparse_results:
                score += 1.0 / (sparse_results.index(guideline) + 1)
            score += self._tier_weight(guideline) * 0.05
            scored.append((score, guideline))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
