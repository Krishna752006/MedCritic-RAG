from typing import Dict, Optional
import uuid

from src.chat.conversation_memory import ConversationMemory
from src.chat.medical_chat import MedicalChatService
from src.chat.task_router import ClinicalTaskRouter
from src.recommendation.decision_support import ClinicalDecisionSupport
from src.verification.evidence_verifier import EvidenceVerifier


class ClinicalAgent:
    """AI Clinical Agent orchestrating intent, memory, routing, reasoning, and verification."""

    def __init__(self):
        self.chat_service = MedicalChatService()
        self.memory = ConversationMemory()
        self.task_router = ClinicalTaskRouter(chat_service=self.chat_service, memory=self.memory)
        self.verifier = EvidenceVerifier()
        self.decision_support = ClinicalDecisionSupport()

    def create_session_id(self) -> str:
        return str(uuid.uuid4())

    def handle_message(self, session_id: str, message: str, context_summary: Optional[str] = None, lang: str = "en") -> Dict[str, object]:
        if not session_id:
            session_id = self.create_session_id()

        self.memory.add_message(session_id, "user", message)
        response_payload = self.task_router.route(session_id, message, context_summary, lang)
        response_text = response_payload.get("response", "")

        evidence = self.verifier.verify_sources(response_text, response_payload.get("sources", []))
        risk = self.verifier.assess_hallucination_risk(response_text, response_payload.get("sources", []))
        clinical_advice = self.decision_support.assess(message, response_payload.get("sources", []))

        # Capture explainability fields if present in response_payload
        why = response_payload.get("why", None)
        evidence_snippet = response_payload.get("evidence", None)
        source = response_payload.get("source", None)
        confidence = response_payload.get("confidence", 0.95)
        evidence_ranking = response_payload.get("evidence_ranking", "★★★ PubMed")
        health_risk_score = response_payload.get("health_risk_score", None)

        self.memory.add_message(session_id, "assistant", response_text)

        metadata = self.memory.get_metadata(session_id)

        return {
            "session_id": session_id,
            "intent": response_payload.get("intent", "unknown"),
            "task": response_payload.get("task", "unknown"),
            "response": response_text,
            "sources": response_payload.get("sources", []),
            "verified": evidence["verified"],
            "source_count": evidence["source_count"],
            "evidence_notes": evidence["evidence_notes"],
            "hallucination_risk": risk,
            "clinical_recommendation": clinical_advice["recommendation"],
            "clinical_reasoning": clinical_advice["reasoning"],
            "recommended_specialist": clinical_advice.get("specialist"),
            "memory_summary": self.memory.summarize_history(session_id),
            "metadata": metadata,
            # Explainability metrics
            "why": why,
            "evidence_snippet": evidence_snippet,
            "source": source,
            "confidence": confidence,
            "evidence_ranking": evidence_ranking,
            "health_risk_score": health_risk_score
        }
