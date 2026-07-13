from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "MedCritic-RAG++ Engine",
        "components": {
            "pdf_parser": "ready",
            "ocr_engine": "ready",
            "retriever": "ready",
            "confidence_calibrator": "ready",
        },
    }

