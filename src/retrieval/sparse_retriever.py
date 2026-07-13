import importlib
import re
from typing import List
from src.retrieval.index_builder import GuidelineIndexBuilder
from src.extraction.schema import MedicalGuideline

BM25_AVAILABLE = False

try:
    if importlib.util.find_spec("rank_bm25") is not None:
        from rank_bm25 import BM25Okapi
        BM25_AVAILABLE = True
except Exception:
    BM25_AVAILABLE = False

class SparseRetriever:
    def __init__(self):
        builder = GuidelineIndexBuilder()
        self.guidelines = builder.get_all_guidelines()
        self.available = BM25_AVAILABLE
        self.bm25 = None
        self.corpus_tokens = []

        if self.available:
            self.corpus_tokens = [self._tokenize(g.text_snippet) for g in self.guidelines]
            self.bm25 = BM25Okapi(self.corpus_tokens)

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    def retrieve(self, query: str, top_k: int = 3) -> List[MedicalGuideline]:
        if not query:
            return []

        query_tokens = self._tokenize(query)
        if self.available and self.bm25 is not None:
            try:
                doc_scores = self.bm25.get_scores(query_tokens)
                ranked = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)
                return [self.guidelines[i] for i in ranked[:top_k] if doc_scores[i] > 0]
            except Exception:
                self.available = False

        query_lower = query.lower()
        fallback = []
        for guideline in self.guidelines:
            score = 0
            text = guideline.text_snippet.lower()
            for token in query_tokens:
                if len(token) > 2 and token in text:
                    score += 1
            if query_lower in text:
                score += 4
            if score > 0:
                fallback.append((score, guideline))

        fallback.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in fallback[:top_k]]
