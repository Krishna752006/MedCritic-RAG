from typing import List, Tuple
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.sparse_retriever import SparseRetriever
from src.retrieval.reranker import HybridReranker
from src.retrieval.context_builder import ContextBuilder
from src.extraction.schema import MedicalGuideline

class RetrievalManager:
    def __init__(self):
        self.dense = DenseRetriever()
        self.sparse = SparseRetriever()
        self.reranker = HybridReranker()
        self.context_builder = ContextBuilder()

    def retrieve(self, query: str, top_k: int = 4) -> Tuple[List[MedicalGuideline], List[dict]]:
        if not query:
            return [], []

        dense_results = self.dense.retrieve(query, top_k=top_k)
        sparse_results = self.sparse.retrieve(query, top_k=top_k)

        ranked_results = self.reranker.rerank(query, dense_results, sparse_results, top_k=top_k)
        evidence_context = self.context_builder.build_context(ranked_results, max_items=min(len(ranked_results), top_k))

        # Ensure the final output is ordered by reranker decisions while preserving evidence context.
        return ranked_results, evidence_context

    def _merge_results(self, dense_results: List[MedicalGuideline], sparse_results: List[MedicalGuideline]) -> List[MedicalGuideline]:
        merged = []
        seen_ids = set()
        for guideline in dense_results + sparse_results:
            if guideline.id not in seen_ids:
                merged.append(guideline)
                seen_ids.add(guideline.id)
        return merged
