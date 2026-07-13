from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/status")
def auth_status():
    return {
        "enabled": False,
        "message": "Authentication module placeholder. Current API runs without auth.",
    }

