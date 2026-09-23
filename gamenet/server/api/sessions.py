from fastapi import APIRouter, Depends

from gamenet.server.db import get_connection
from gamenet.server.models.session import SessionActionRequest, SessionConsumeRequest, SessionResponse, SessionStartRequest
from gamenet.server.security.auth import require_permission
from gamenet.server.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
def start_session(payload: SessionStartRequest, user: dict = Depends(require_permission("sessions.manage"))) -> SessionResponse:
    with get_connection() as conn:
        return SessionService(conn).start(payload, user["id"])


@router.post("/{session_id}/pause", response_model=SessionResponse)
def pause_session(session_id: str, payload: SessionActionRequest, user: dict = Depends(require_permission("sessions.manage"))) -> SessionResponse:
    with get_connection() as conn:
        return SessionService(conn).action(session_id, payload, user["id"], "pause")


@router.post("/{session_id}/resume", response_model=SessionResponse)
def resume_session(session_id: str, payload: SessionActionRequest, user: dict = Depends(require_permission("sessions.manage"))) -> SessionResponse:
    with get_connection() as conn:
        return SessionService(conn).action(session_id, payload, user["id"], "resume")


@router.post("/{session_id}/end", response_model=SessionResponse)
def end_session(session_id: str, payload: SessionActionRequest, user: dict = Depends(require_permission("sessions.manage"))) -> SessionResponse:
    with get_connection() as conn:
        return SessionService(conn).action(session_id, payload, user["id"], "end")


@router.post("/{session_id}/consume", response_model=SessionResponse)
def consume_session(session_id: str, payload: SessionConsumeRequest, _user: dict = Depends(require_permission("sessions.manage"))) -> SessionResponse:
    with get_connection() as conn:
        return SessionService(conn).consume(session_id, payload)