from backend.app.rag.retriever import Retriever


class RetrievalService:
    def __init__(self):
        self.retriever = Retriever()

    def retrieve(self, query: str, top_k: int = 3):
        return self.retriever.retrieve(query, top_k=top_k)
