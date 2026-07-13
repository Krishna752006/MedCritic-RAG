class SummaryMemory:
    def summarize(self, messages: list[dict]) -> str:
        if not messages:
            return ""
        return " ".join(str(message.get("content", "")) for message in messages[-6:]).strip()

