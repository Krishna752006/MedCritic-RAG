from backend.app.chat.prompt_builder import PromptBuilder


class ContextBuilder:
    def __init__(self, memory):
        self.memory = memory
        self.prompt_builder = PromptBuilder()

    def build(self, session_id: str) -> str:
        return self.memory.build_personalized_prompt_context(session_id)

    def build_prompt(
        self,
        session_id: str,
        user_message: str,
        rag_context: list[dict] | None = None,
        conversation_summary: str | None = None,
    ) -> str:
        return self.prompt_builder.build(
            user_message=user_message,
            memory_context=self.build(session_id),
            rag_context=rag_context,
            conversation_summary=conversation_summary,
        )
