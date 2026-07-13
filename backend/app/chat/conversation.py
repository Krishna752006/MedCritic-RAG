from backend.app.chat.context_builder import ContextBuilder
from backend.app.chat.intent_router import IntentRouter
from backend.app.chat.response_builder import ResponseBuilder
from backend.app.memory.chat_memory import ChatMemory
from src.chat.medical_chat import MedicalChatService


class Conversation:
    def __init__(
        self,
        chat_service: MedicalChatService | None = None,
        memory: ChatMemory | None = None,
    ):
        self.chat_service = chat_service or MedicalChatService()
        self.memory = memory or ChatMemory()
        self.intent_router = IntentRouter(self.chat_service, self.memory)
        self.context_builder = ContextBuilder(self.memory)
        self.response_builder = ResponseBuilder()

    def respond(self, session_id: str, message: str, context_summary: str | None = None, lang: str = "en") -> dict:
        intent, task = self.intent_router.route(session_id, message)
        context = context_summary or self.context_builder.build(session_id)
        payload = self.chat_service.chat(session_id, message, context, lang, self.memory)
        return self.response_builder.build(intent, task, payload)

