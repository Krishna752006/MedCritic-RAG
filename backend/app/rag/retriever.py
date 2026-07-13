from src.retrieval.retriever import RetrievalManager


class Retriever:
    def __init__(self):
        self.manager = RetrievalManager()

    def retrieve(self, query: str, top_k: int = 3):
        results, _ = self.manager.retrieve(query, top_k=top_k)
        return results

