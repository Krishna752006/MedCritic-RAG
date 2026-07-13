from backend.app.llm.prompts import MEDICAL_SYSTEM_PROMPT


class PromptBuilder:
    SAFETY_INSTRUCTIONS = (
        "Medical safety: do not diagnose with certainty, do not recommend unsafe medication changes, "
        "flag red symptoms, state uncertainty, and advise qualified clinical care when needed."
    )

    def build(
        self,
        user_message: str,
        memory_context: str | None = None,
        rag_context: list[dict] | None = None,
        conversation_summary: str | None = None,
    ) -> str:
        parts = [MEDICAL_SYSTEM_PROMPT, self.SAFETY_INSTRUCTIONS]

        if conversation_summary:
            parts.append(f"Conversation summary: {conversation_summary}")
        if memory_context:
            parts.append(f"Patient memory: {memory_context}")
        if rag_context:
            evidence = "\n".join(
                f"[{idx}] {item.get('source', 'source')}: {item.get('text', item)}"
                for idx, item in enumerate(rag_context, 1)
            )
            parts.append(f"Evidence context:\n{evidence}")

        parts.append(f"User message: {user_message}")
        return "\n\n".join(parts)
