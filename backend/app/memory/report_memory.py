class ReportMemory:
    def __init__(self):
        self._reports: dict[str, list[dict]] = {}

    def add_report(self, chat_id: str, report: dict) -> None:
        self._reports.setdefault(chat_id, []).append(report)

    def latest_report(self, chat_id: str) -> dict | None:
        reports = self._reports.get(chat_id, [])
        return reports[-1] if reports else None

    def list_reports(self, chat_id: str) -> list[dict]:
        return self._reports.get(chat_id, [])

