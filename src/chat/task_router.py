from typing import Optional
from src.chat.conversation_memory import ConversationMemory
from src.chat.medical_chat import MedicalChatService


class ClinicalTaskRouter:
    """
    VeriMedX task router: maps 9 intents to named tasks and delegates
    to the chat service while preserving triage workflow continuity.
    """

    INTENT_TO_TASK = {
        "greeting":       "greeting",
        "small_talk":     "casual_conversation",
        "symptom":        "symptom_triage_start",
        "follow_up":      "symptom_triage_continue",
        "disease_info":   "disease_info_lookup",
        "medicine_info":  "medicine_info_lookup",
        "report_upload":  "report_analysis_request",
        "emergency":      "emergency_protocol",
        "comparison_request": "comparison_workflow",
        "general":        "general_guidance",
        "goodbye":        "session_close",
        "medical_query":  "rag_evidence_lookup",
    }

    def __init__(
        self,
        chat_service: Optional[MedicalChatService] = None,
        memory: Optional[ConversationMemory] = None,
    ):
        self.chat_service = chat_service or MedicalChatService()
        self.memory = memory or ConversationMemory()

    def route(
        self,
        session_id: str,
        message: str,
        context_summary: Optional[str] = None,
        lang: str = "en",
    ) -> dict:
        intent = self.chat_service.detect_intent(message, session_id, self.memory)
        task = self.INTENT_TO_TASK.get(intent, "rag_evidence_lookup")

        response_payload = self.chat_service.chat(
            session_id, message, context_summary, lang, self.memory
        )

        return {
            "intent": intent,
            "task": task,
            "response": response_payload["response"],
            "sources": response_payload.get("sources", []),
            "why": response_payload.get("why"),
            "evidence": response_payload.get("evidence"),
            "source": response_payload.get("source"),
            "confidence": response_payload.get("confidence", 0.95),
            "evidence_ranking": response_payload.get("evidence_ranking", "★★★ PubMed"),
            "health_risk_score": response_payload.get("health_risk_score", "Low"),
        }
