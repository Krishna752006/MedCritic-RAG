from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.dependencies import get_chat_workflow
from backend.app.models.schemas import ChatRequest, CreateChatRequest, RenameChatRequest
from backend.app.workflows.chat_workflow import ChatWorkflow

router = APIRouter(tags=["chat"])


@router.post("/chats")
async def create_chat(
    request: CreateChatRequest,
    workflow: ChatWorkflow = Depends(get_chat_workflow),
):
    return workflow.create_chat(request)


@router.get("/chats")
async def list_chats(
    user_id: str | None = Query(None),
    workflow: ChatWorkflow = Depends(get_chat_workflow),
):
    return workflow.list_chats(user_id=user_id)


@router.get("/chats/{chat_id}")
async def get_chat_history(
    chat_id: str,
    limit: int | None = Query(None),
    workflow: ChatWorkflow = Depends(get_chat_workflow),
):
    try:
        return workflow.get_chat_history(chat_id, limit=limit)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/chats/{chat_id}")
async def rename_chat(
    chat_id: str,
    request: RenameChatRequest,
    workflow: ChatWorkflow = Depends(get_chat_workflow),
):
    try:
        return workflow.rename_chat(chat_id, request.title)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/chats/{chat_id}")
async def delete_chat(
    chat_id: str,
    workflow: ChatWorkflow = Depends(get_chat_workflow),
):
    try:
        return workflow.delete_chat(chat_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/chat")
async def chat(request: ChatRequest, workflow: ChatWorkflow = Depends(get_chat_workflow)):
    try:
        return workflow.handle_chat(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat service failed: {str(exc)}")
