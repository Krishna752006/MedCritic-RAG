"""Train the medical knowledge base from free online resources.

This script downloads open medical text from Wikipedia and builds a local BM25 corpus
used by the backend chat assistant.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.chat.medical_chat import MedicalKnowledgeTrainer


def main():
    trainer = MedicalKnowledgeTrainer()
    result = trainer.train()
    print("Knowledge base training complete:")
    print(result)


if __name__ == "__main__":
    main()
