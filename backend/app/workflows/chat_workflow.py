import time
from typing import Any

from backend.app.chat.conversation import Conversation
from backend.app.memory.chat_memory import ChatMemory
from backend.app.memory.summary_memory import SummaryMemory
from backend.app.services.chat_service import ChatSessionService
from src.chat.clinical_agent import ClinicalAgent
from src.evaluation.benchmark_tracker import BenchmarkTracker

from backend.app.models.schemas import ChatRequest, CreateChatRequest


class ChatWorkflow:
    def __init__(
        self,
        clinical_agent: ClinicalAgent | None = None,
        benchmark_tracker: BenchmarkTracker | None = None,
    ):
        self.clinical_agent = clinical_agent or ClinicalAgent()
        self.conversation = Conversation(
            chat_service=self.clinical_agent.chat_service,
            memory=ChatMemory(),
        )
        self.clinical_agent.memory = self.conversation.memory
        self.benchmark_tracker = benchmark_tracker or BenchmarkTracker()
        self.chat_sessions = ChatSessionService()
        self.summary_memory = SummaryMemory()

    def create_chat(self, request: CreateChatRequest) -> dict:
        chat = self.chat_sessions.create_chat(
            title=request.title,
            user_id=request.user_id,
            metadata=request.metadata,
        )
        if request.metadata:
            self.conversation.memory.update_metadata(chat["id"], request.metadata)
        return chat

    def list_chats(self, user_id: str | None = None) -> list[dict]:
        return self.chat_sessions.list_chats(user_id=user_id)

    def rename_chat(self, chat_id: str, title: str) -> dict:
        if not title.strip():
            raise ValueError("Chat title must not be empty.")
        return self.chat_sessions.rename_chat(chat_id, title)

    def delete_chat(self, chat_id: str) -> dict:
        self.chat_sessions.delete_chat(chat_id)
        self.conversation.memory.clear_session(chat_id)
        return {"status": "deleted", "chat_id": chat_id}

    def get_chat_history(self, chat_id: str, limit: int | None = None) -> dict:
        chat = self.chat_sessions.get_chat(chat_id)
        messages = self.chat_sessions.get_messages(chat_id, limit=limit)
        return {
            "chat": chat,
            "messages": messages,
            "metadata": self.conversation.memory.get_metadata(chat_id),
            "summary": chat.get("summary"),
        }

    def handle_chat(self, request: ChatRequest) -> dict[str, Any]:
        if not request.message.strip():
            raise ValueError("Chat message must not be empty.")

        start_time = time.time()
        chat = self.chat_sessions.ensure_chat(request.chat_id or request.session_id)
        session_id = chat["id"]

        if request.profile:
            self.conversation.memory.update_metadata(session_id, request.profile)
            self.chat_sessions.update_metadata(session_id, request.profile)

        self.conversation.memory.add_message(session_id, "user", request.message)
        self.chat_sessions.add_message(session_id, "user", request.message)
        response_payload = self.conversation.respond(
            session_id=session_id,
            message=request.message,
            context_summary=request.context_summary or chat.get("summary"),
            lang=request.lang,
        )
        response_text = response_payload.get("response", "")
        evidence = self.clinical_agent.verifier.verify_sources(response_text, response_payload.get("sources", []))
        risk = self.clinical_agent.verifier.assess_hallucination_risk(response_text, response_payload.get("sources", []))
        clinical_advice = self.clinical_agent.decision_support.assess(request.message, response_payload.get("sources", []))
        self.conversation.memory.add_message(session_id, "assistant", response_text)
        self.chat_sessions.add_message(
            session_id,
            "assistant",
            response_text,
            metadata={
                "intent": response_payload.get("intent"),
                "task": response_payload.get("task"),
                "sources": response_payload.get("sources", []),
                "confidence": response_payload.get("confidence", 0.95),
            },
        )
        stored_messages = self.chat_sessions.get_messages(session_id, limit=12)
        summary = self.summary_memory.summarize(stored_messages)
        self.chat_sessions.update_summary(session_id, summary)
        response = {
            "session_id": session_id,
            "chat_id": session_id,
            **response_payload,
            "verified": evidence["verified"],
            "source_count": evidence["source_count"],
            "evidence_notes": evidence["evidence_notes"],
            "hallucination_risk": risk,
            "clinical_recommendation": clinical_advice["recommendation"],
            "clinical_reasoning": clinical_advice["reasoning"],
            "memory_summary": summary,
            "metadata": self.conversation.memory.get_metadata(session_id),
            "short_term_memory": self.conversation.memory.get_short_term_memory(session_id),
            "evidence_snippet": response_payload.get("evidence"),
        }

        latency_ms = (time.time() - start_time) * 1000
        verified = response.get("verified", False)
        hallucinated = response.get("hallucination_risk", "").startswith("High")
        confidence = response.get("confidence", 0.95)
        has_sources = len(response.get("sources", [])) > 0

        self.benchmark_tracker.log_run(
            latency_ms=latency_ms,
            hallucinated=hallucinated,
            retrieved_correct=has_sources,
            confidence=confidence,
            verified=verified,
        )
        return response
