from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from backend.app.dependencies import get_document_service
from backend.app.models.schemas import DocumentUploadResponse
from backend.app.services.document_service import DocumentService

router = APIRouter(tags=["documents"])


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    chat_id: str | None = Query(None),
    service: DocumentService = Depends(get_document_service),
):
    try:
        return service.upload_document(file, chat_id=chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(exc)}")


@router.get("/documents")
def list_documents(
    chat_id: str | None = Query(None),
    service: DocumentService = Depends(get_document_service),
):
    return service.list_documents(chat_id=chat_id)


@router.get("/documents/{document_id}")
def get_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
):
    try:
        return service.get_document(document_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/documents/{document_id}/text")
def get_document_text(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
):
    try:
        return service.get_extracted_text(document_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
