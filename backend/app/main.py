from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import auth, chat, documents, health, medical, reports
from backend.app.config.logging import configure_logging
from backend.app.config.settings import settings
from backend.app.utils.exception_handlers import register_exception_handlers

configure_logging()
settings.temp_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

for router in (health.router, chat.router, reports.router, documents.router, medical.router, auth.router):
    app.include_router(router, prefix=settings.api_v1_prefix)

# Legacy unversioned routes stay mounted while the frontend migrates to /api/v1.
for router in (health.router, chat.router, reports.router, documents.router, medical.router, auth.router):
    app.include_router(router)
