from src.chat.medical_chat import MedicalChatService


class IntentRouter:
    INTENT_TO_TASK = {
        "greeting": "greeting",
        "small_talk": "casual_conversation",
        "symptom": "symptom_triage_start",
        "follow_up": "symptom_triage_continue",
        "disease_info": "disease_info_lookup",
        "medicine_info": "medicine_info_lookup",
        "report_upload": "report_analysis_request",
        "emergency": "emergency_protocol",
        "comparison_request": "comparison_workflow",
        "general": "general_guidance",
        "goodbye": "session_close",
        "medical_query": "rag_evidence_lookup",
    }

    def __init__(self, chat_service: MedicalChatService, memory):
        self.chat_service = chat_service
        self.memory = memory

    def route(self, session_id: str, message: str) -> tuple[str, str]:
        intent = self.chat_service.detect_intent(message, session_id, self.memory)
        return intent, self.INTENT_TO_TASK.get(intent, "rag_evidence_lookup")

