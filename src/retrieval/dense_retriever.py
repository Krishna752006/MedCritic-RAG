import importlib
from typing import List

import numpy as np
from src.retrieval.index_builder import GuidelineIndexBuilder
from src.extraction.schema import MedicalGuideline

SENTENCE_TRANSFORMER_AVAILABLE = False
FAISS_AVAILABLE = False

try:
    if importlib.util.find_spec("sentence_transformers") is not None:
        sentence_module = importlib.import_module("sentence_transformers")
        SentenceTransformer = sentence_module.SentenceTransformer
        SENTENCE_TRANSFORMER_AVAILABLE = True
    if importlib.util.find_spec("faiss") is not None:
        faiss = importlib.import_module("faiss")
        FAISS_AVAILABLE = True
except Exception:
    SENTENCE_TRANSFORMER_AVAILABLE = False
    FAISS_AVAILABLE = False

class DenseRetriever:
    def __init__(self):
        builder = GuidelineIndexBuilder()
        self.guidelines = builder.get_all_guidelines()
        self.available = SENTENCE_TRANSFORMER_AVAILABLE
        self.index_available = FAISS_AVAILABLE and SENTENCE_TRANSFORMER_AVAILABLE
        self.encoder = None
        self.index = None
        self.embeddings = None

        if self.available:
            try:
                self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
                texts = [g.text_snippet for g in self.guidelines]
                self.embeddings = self.encoder.encode(
                    texts,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                    normalize_embeddings=True,
                )

                if self.index_available:
                    dimension = self.embeddings.shape[1]
                    self.index = faiss.IndexFlatIP(dimension)
                    self.index.add(self.embeddings.astype("float32"))
            except Exception as e:
                print(f"Failed to initialize DenseRetriever: {e}. Falling back to lexical similarity.")
                self.available = False
                self.index_available = False

    def _score_lexical(self, query: str, guideline: MedicalGuideline) -> float:
        query_tokens = set(query.lower().split())
        snippet_tokens = set(guideline.text_snippet.lower().split())
        intersection = query_tokens.intersection(snippet_tokens)
        score = len(intersection) / max(len(query_tokens), 1)
        if guideline.evidence_tier:
            if guideline.evidence_tier.startswith("Tier 1"):
                score += 0.8
            elif guideline.evidence_tier.startswith("Tier 2"):
                score += 0.4
        return score

    def retrieve(self, query: str, top_k: int = 3) -> List[MedicalGuideline]:
        if not query:
            return []

        if self.available and self.encoder is not None:
            try:
                query_vector = self.encoder.encode(
                    [query],
                    convert_to_numpy=True,
                    show_progress_bar=False,
                    normalize_embeddings=True,
                ).astype("float32")

                if self.index_available and self.index is not None:
                    _, indices = self.index.search(query_vector, top_k)
                else:
                    similarity = np.dot(self.embeddings, query_vector[0])
                    indices = np.argsort(-similarity)[:top_k][None, :]

                results = [self.guidelines[idx] for idx in indices[0] if 0 <= idx < len(self.guidelines)]
                return results
            except Exception as e:
                print(f"Dense search encountered error: {e}. Falling back to lexical retrieval.")

        scored = [(self._score_lexical(query, g), g) for g in self.guidelines]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
