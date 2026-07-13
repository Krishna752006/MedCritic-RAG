import uuid
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChatSessionService:
    """Application-level chat store for V1. Replace with repositories when DB persistence is enabled."""

    def __init__(self):
        self._chats: dict[str, dict] = {}
        self._messages: dict[str, list[dict]] = {}

    def create_chat(
        self,
        title: str | None = None,
        user_id: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        chat_id = str(uuid.uuid4())
        timestamp = _now()
        chat = {
            "id": chat_id,
            "title": title or "New chat",
            "user_id": user_id,
            "summary": None,
            "metadata": metadata or {},
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        self._chats[chat_id] = chat
        self._messages[chat_id] = []
        return chat

    def ensure_chat(self, chat_id: str | None = None, title: str | None = None) -> dict:
        if chat_id and chat_id in self._chats:
            return self._chats[chat_id]
        return self.create_chat(title=title)

    def rename_chat(self, chat_id: str, title: str) -> dict:
        chat = self.get_chat(chat_id)
        chat["title"] = title.strip() or chat["title"]
        chat["updated_at"] = _now()
        return chat

    def delete_chat(self, chat_id: str) -> None:
        self.get_chat(chat_id)
        self._chats.pop(chat_id, None)
        self._messages.pop(chat_id, None)

    def get_chat(self, chat_id: str) -> dict:
        chat = self._chats.get(chat_id)
        if not chat:
            raise KeyError(f"Chat not found: {chat_id}")
        return chat

    def list_chats(self, user_id: str | None = None) -> list[dict]:
        chats = list(self._chats.values())
        if user_id:
            chats = [chat for chat in chats if chat.get("user_id") == user_id]
        return sorted(chats, key=lambda chat: chat["updated_at"], reverse=True)

    def add_message(self, chat_id: str, role: str, content: str, metadata: dict | None = None) -> dict:
        self.get_chat(chat_id)
        message = {
            "id": str(uuid.uuid4()),
            "chat_id": chat_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "created_at": _now(),
        }
        self._messages.setdefault(chat_id, []).append(message)
        self._chats[chat_id]["updated_at"] = message["created_at"]
        return message

    def get_messages(self, chat_id: str, limit: int | None = None) -> list[dict]:
        self.get_chat(chat_id)
        messages = self._messages.get(chat_id, [])
        return messages[-limit:] if limit else messages

    def update_summary(self, chat_id: str, summary: str | None) -> None:
        chat = self.get_chat(chat_id)
        chat["summary"] = summary
        chat["updated_at"] = _now()

    def update_metadata(self, chat_id: str, updates: dict) -> dict:
        chat = self.get_chat(chat_id)
        chat["metadata"].update({key: value for key, value in updates.items() if value is not None})
        chat["updated_at"] = _now()
        return chat["metadata"]
