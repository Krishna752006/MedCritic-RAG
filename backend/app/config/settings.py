import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


WORKSPACE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(WORKSPACE_DIR / ".env")


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    env: str = os.getenv("ENV", "development")
    app_name: str = os.getenv("APP_NAME", "MedCritic-RAG++ Backend Service")
    app_description: str = "Multimodal verified RAG engine for medical report analysis."
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")
    cors_origins: list[str] = None
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/medcritic",
    )
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "25"))
    workspace_dir: Path = WORKSPACE_DIR
    temp_dir: Path = WORKSPACE_DIR / "data" / "temp"
    document_storage_dir: Path = WORKSPACE_DIR / "data" / "documents"
    allowed_report_extensions: set[str] = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "cors_origins",
            _csv(os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:4173,http://localhost:3000")),
        )
        object.__setattr__(
            self,
            "allowed_report_extensions",
            {".pdf", ".png", ".jpg", ".jpeg", ".tiff"},
        )


settings = Settings()

APP_NAME = settings.app_name
APP_DESCRIPTION = settings.app_description
APP_VERSION = settings.app_version
TEMP_DIR = settings.temp_dir
ALLOWED_REPORT_EXTENSIONS = settings.allowed_report_extensions
