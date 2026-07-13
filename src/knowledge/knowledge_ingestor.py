import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = WORKSPACE_ROOT / "data" / "knowledge"
SOURCE_DIR = KNOWLEDGE_DIR / "sources"
CORPUS_FILE = KNOWLEDGE_DIR / "bm25_corpus.json"
EMBEDDING_FILE = KNOWLEDGE_DIR / "knowledge_embeddings.npz"

try:
    import numpy as np
    import importlib
    if importlib.util.find_spec("sentence_transformers") is not None:
        from sentence_transformers import SentenceTransformer
        EMBEDDING_AVAILABLE = True
    else:
        EMBEDDING_AVAILABLE = False
except ImportError:
    EMBEDDING_AVAILABLE = False

CATEGORY_HINTS = {
    "sepsis": "emergency_criteria",
    "stroke": "emergency_criteria",
    "myocardial_infarction": "emergency_criteria",
    "heart_failure": "disease_guideline",
    "hypertension": "disease_guideline",
    "diabetes_mellitus": "disease_guideline",
    "pneumonia": "disease_guideline",
    "asthma": "disease_guideline",
    "coronary_artery_disease": "disease_guideline",
    "chronic_kidney_disease": "disease_guideline",
}

class KnowledgeIngestor:
    def __init__(self):
        os.makedirs(SOURCE_DIR, exist_ok=True)
        os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip())

    def _extract_header_metadata(self, text: str, title: str) -> Dict[str, str]:
        metadata: Dict[str, str] = {
            "title": title.replace("_", " ").title(),
            "source_name": title.replace("_", " ").title(),
            "version": "1.0",
            "category": CATEGORY_HINTS.get(title.lower(), "general_guideline"),
            "source_type": "guideline",
        }

        for line in text.splitlines()[:12]:
            if not line.strip():
                continue
            match = re.match(r"^([^:]+)\s*:\s*(.+)$", line.strip())
            if not match:
                continue
            key, value = match.group(1).strip().lower(), match.group(2).strip()
            if key in {"title", "name"}:
                metadata["title"] = value
            elif key in {"source", "source_name"}:
                metadata["source_name"] = value
            elif key in {"version", "edition", "release"}:
                metadata["version"] = value
            elif key == "category":
                metadata["category"] = value.replace(" ", "_").lower()
            elif key == "type":
                metadata["source_type"] = value.replace(" ", "_").lower()

        year_match = re.search(r"\b(20\d{2})\b", text)
        if metadata["version"] == "1.0" and year_match:
            metadata["version"] = year_match.group(1)

        return metadata

    def _chunk_text(self, text: str, max_tokens: int = 180) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: List[str] = []
        current: List[str] = []
        count = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            tokens = sentence.split()
            if count + len(tokens) > max_tokens and current:
                chunks.append(" ".join(current))
                current = []
                count = 0
            current.append(sentence)
            count += len(tokens)
        if current:
            chunks.append(" ".join(current))
        return chunks

    def read_source_files(self) -> List[Dict[str, object]]:
        entries: List[Dict[str, object]] = []
        for fp in sorted(SOURCE_DIR.glob("*.txt")):
            raw_text = self._normalize(fp.read_text(encoding="utf-8"))
            if not raw_text:
                continue
            metadata = self._extract_header_metadata(raw_text, fp.stem)
            chunks = self._chunk_text(raw_text)
            for idx, chunk in enumerate(chunks, start=1):
                entries.append({
                    "id": f"{fp.stem}-{idx}",
                    "title": metadata["title"],
                    "source": metadata["source_name"],
                    "text": chunk,
                    "version": metadata["version"],
                    "category": metadata["category"],
                    "source_type": metadata["source_type"],
                    "metadata": metadata,
                })
        return entries

    def save_corpus(self, corpus: List[Dict[str, object]]) -> None:
        CORPUS_FILE.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_corpus(self) -> List[Dict[str, object]]:
        if CORPUS_FILE.exists():
            try:
                return json.loads(CORPUS_FILE.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return []
        return []

    def create_embeddings(self, corpus: List[Dict[str, object]]) -> Optional[str]:
        if not EMBEDDING_AVAILABLE or not corpus:
            return None

        try:
            encoder = SentenceTransformer("all-MiniLM-L6-v2")
            texts = [item["text"] for item in corpus]
            embeddings = encoder.encode(texts)
            np.savez(EMBEDDING_FILE, ids=[item["id"] for item in corpus], embeddings=embeddings)
            return str(EMBEDDING_FILE)
        except Exception:
            return None

    def train(self, use_local_sources: bool = True) -> Dict[str, object]:
        corpus = []
        if use_local_sources:
            corpus = self.read_source_files()

        if not corpus:
            corpus = self.load_corpus()

        if corpus:
            self.save_corpus(corpus)
            embedding_path = self.create_embeddings(corpus)
            return {
                "status": "trained",
                "knowledge_chunks": len(corpus),
                "source_files": len({item["source"] for item in corpus}),
                "embedding_path": embedding_path,
            }

        return {"status": "empty", "knowledge_chunks": 0, "source_files": 0}
