from pydantic import BaseModel

from src.extraction.schema import DiagnosticReportAnalysis
from src.extraction.schema import MedicalFinding


class CreateChatRequest(BaseModel):
    title: str | None = None
    user_id: str | None = None
    metadata: dict | None = None


class RenameChatRequest(BaseModel):
    title: str


class AnalyzeSampleRequest(BaseModel):
    sample_type: str
    lang: str = "en"


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    chat_id: str | None = None
    context_summary: str | None = None
    lang: str = "en"
    profile: dict | None = None


class ChatSummary(BaseModel):
    id: str
    title: str
    user_id: str | None = None
    summary: str | None = None
    metadata: dict = {}
    created_at: str
    updated_at: str


class ChatHistoryResponse(BaseModel):
    chat: ChatSummary
    messages: list[dict]
    metadata: dict
    summary: str | None = None


class DocumentUploadResponse(BaseModel):
    id: str
    chat_id: str | None = None
    filename: str
    content_type: str | None = None
    size_bytes: int
    storage_path: str
    extracted_text_path: str
    metadata: dict


class MedicalUnderstandingRequest(BaseModel):
    text: str


class MedicalUnderstandingResponse(BaseModel):
    report_type: str
    entities: dict
    findings: list[MedicalFinding]
    lab_tests: list[MedicalFinding]
    vital_signs: list[MedicalFinding]
    normalized_codes: list[dict]


__all__ = [
    "AnalyzeSampleRequest",
    "ChatHistoryResponse",
    "ChatRequest",
    "ChatSummary",
    "CreateChatRequest",
    "DiagnosticReportAnalysis",
    "DocumentUploadResponse",
    "MedicalUnderstandingRequest",
    "MedicalUnderstandingResponse",
    "RenameChatRequest",
]
