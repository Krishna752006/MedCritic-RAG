from src.chat.conversation_memory import ConversationMemory


class ChatMemory(ConversationMemory):
    """Stores recent chat messages and triage metadata for each session."""

    def get_short_term_memory(self, session_id: str, limit: int = 10):
        return self.get_history(session_id, limit=limit)

    def update_report_metadata(
        self,
        session_id: str,
        uploaded_reports: list[dict] | None = None,
        previous_findings: list[dict] | None = None,
        active_medications: list[str] | None = None,
        user_preferences: dict | None = None,
    ) -> None:
        self.update_metadata(
            session_id,
            {
                "uploaded_reports": uploaded_reports,
                "previous_findings": previous_findings,
                "active_medications": active_medications,
                "user_preferences": user_preferences,
            },
        )
