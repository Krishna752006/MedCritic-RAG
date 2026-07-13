from fastapi import UploadFile

from backend.app.models.schemas import AnalyzeSampleRequest, DiagnosticReportAnalysis
from backend.app.services.report_service import ReportService


class ReportWorkflow:
    def __init__(self, report_service: ReportService | None = None):
        self.report_service = report_service or ReportService()

    def analyze_upload(self, file: UploadFile, lang: str = "en") -> DiagnosticReportAnalysis:
        return self.report_service.analyze_upload(file, lang)

    def analyze_sample(self, request: AnalyzeSampleRequest) -> DiagnosticReportAnalysis:
        return self.report_service.analyze_sample(request.sample_type, request.lang)

    def train_knowledge(self) -> dict:
        return self.report_service.train_knowledge()

    def upload_guideline(self, file: UploadFile) -> dict:
        return self.report_service.upload_guideline(file)

    def get_benchmarks(self) -> dict:
        return self.report_service.get_benchmarks()

    def get_knowledge_graph(self) -> dict:
        return self.report_service.get_knowledge_graph()
