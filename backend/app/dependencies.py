from functools import lru_cache

from backend.app.config.settings import Settings, settings
from backend.app.services.document_service import DocumentService
from backend.app.services.entity_service import EntityService
from backend.app.workflows.chat_workflow import ChatWorkflow
from backend.app.workflows.report_workflow import ReportWorkflow


@lru_cache
def get_settings() -> Settings:
    return settings


@lru_cache
def get_chat_workflow() -> ChatWorkflow:
    return ChatWorkflow()


@lru_cache
def get_report_workflow() -> ReportWorkflow:
    return ReportWorkflow()


@lru_cache
def get_document_service() -> DocumentService:
    return DocumentService()


@lru_cache
def get_entity_service() -> EntityService:
    return EntityService()
