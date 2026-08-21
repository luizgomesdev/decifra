"""Chat endpoints."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from decifra.features.chat.schemas import ChatAnswer, HistoryTurn
from decifra.features.chat.service import ask, history, summarise_conversation
from decifra.features.chat.streaming import stream_answer
from decifra.shared.db import new_session_id

router = APIRouter(prefix="/patients/{patient_id}", tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


@router.post("/chat")
def post_chat(patient_id: str, request: ChatRequest) -> ChatAnswer:
    return ask(request.question, patient_id, request.session_id)


@router.get("/sessions/{session_id}/messages")
def get_history(patient_id: str, session_id: str) -> list[HistoryTurn]:
    return history(patient_id, session_id)


@router.get("/sessions/{session_id}/summary")
def get_session_summary(patient_id: str, session_id: str) -> dict:
    return summarise_conversation(patient_id, session_id)


@router.post("/chat/stream")
def post_chat_stream(patient_id: str, request: ChatRequest) -> StreamingResponse:
    session_id = request.session_id or new_session_id()
    return StreamingResponse(
        stream_answer(request.question, patient_id, session_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
