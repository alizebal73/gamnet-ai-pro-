import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from gamenet.server.api.devices import _heartbeat
from gamenet.server.db import get_connection
from gamenet.server.models.heartbeat import HeartbeatRequest
from gamenet.server.security.device import authenticate_device

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/devices/{pc_id}")
async def device_websocket(websocket: WebSocket, pc_id: str) -> None:
    await websocket.accept()
    authenticated = False
    try:
        auth_message = await websocket.receive_json()
        if auth_message.get("message_type") != "AUTH" or not auth_message.get("device_token"):
            await websocket.close(code=4401, reason="Device authentication required")
            return
        with get_connection() as conn:
            authenticate_device(conn, pc_id, auth_message["device_token"])
        authenticated = True
        await websocket.send_json({"message_type": "AUTH_ACK", "message_id": str(uuid.uuid4())})

        while True:
            message = await websocket.receive_json()
            if message.get("message_type") != "HEARTBEAT":
                await websocket.send_json({"message_type": "ERROR", "error_code": "GN-WS-001", "message": "Unsupported message"})
                continue
            payload = HeartbeatRequest(**message.get("payload", {}))
            with get_connection() as conn:
                response = _heartbeat(conn, pc_id, payload, auth_message["device_token"])
            await websocket.send_json({
                "message_type": "HEARTBEAT_ACK",
                "message_id": str(uuid.uuid4()),
                "request_id": message.get("request_id"),
                "payload": response.model_dump(),
            })
    except WebSocketDisconnect:
        return
    except Exception:
        if authenticated:
            await websocket.close(code=1011, reason="Internal server error")
        else:
            await websocket.close(code=4401, reason="Device authentication failed")