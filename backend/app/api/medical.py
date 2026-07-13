from fastapi import APIRouter, Depends, HTTPException

from backend.app.dependencies import get_entity_service
from backend.app.models.schemas import MedicalUnderstandingRequest, MedicalUnderstandingResponse
from backend.app.services.entity_service import EntityService

router = APIRouter(tags=["medical-understanding"])


@router.post("/medical/understand", response_model=MedicalUnderstandingResponse)
async def understand_medical_text(
    request: MedicalUnderstandingRequest,
    service: EntityService = Depends(get_entity_service),
):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text must not be empty.")
    return service.understand(request.text)
