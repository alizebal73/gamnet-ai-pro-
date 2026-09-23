import json
import uuid

from fastapi import APIRouter, Depends, HTTPException

from gamenet.server.db import get_connection, utc_now_iso
from gamenet.server.models.game import GameCreateRequest, GameResponse, LaunchAuthorizationResponse, LaunchRequest
from gamenet.server.security.auth import require_permission
from gamenet.server.security.device import authenticate_device, device_token
from gamenet.server.services.audit_service import AuditService

router = APIRouter(tags=["games"])


def _game_response(row: dict) -> GameResponse:
    return GameResponse(
        id=row["id"], name=row["name"], slug=row["slug"], platform=row["platform"], launch_type=row["launch_type"],
        executable_path=row["executable_path"], working_directory=row["working_directory"], launch_arguments=row["launch_arguments"],
        process_names=json.loads(row["process_names"]), enabled=bool(row["enabled"]),
    )


@router.get("/games", response_model=list[GameResponse])
def list_games(_user: dict = Depends(require_permission("games.view"))) -> list[GameResponse]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM games WHERE enabled = 1 ORDER BY display_order, name").fetchall()
    return [_game_response(dict(row)) for row in rows]


@router.get("/devices/{pc_id}/games", response_model=list[GameResponse])
def list_device_games(pc_id: str, token: str | None = Depends(device_token)) -> list[GameResponse]:
    with get_connection() as conn:
        authenticate_device(conn, pc_id, token)
        rows = conn.execute(
            """
            SELECT g.* FROM games g
            LEFT JOIN game_device_config c ON c.game_id = g.id AND c.pc_id = ?
            WHERE g.enabled = 1 AND (c.game_id IS NULL OR c.enabled = 1)
            ORDER BY g.display_order, g.name
            """,
            (pc_id,),
        ).fetchall()
    return [_game_response(dict(row)) for row in rows]


@router.post("/games", response_model=GameResponse, status_code=201)
def create_game(payload: GameCreateRequest, user: dict = Depends(require_permission("games.manage"))) -> GameResponse:
    game_id = f"GAME-{uuid.uuid4().hex[:12].upper()}"
    now = utc_now_iso()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO games (id, name, slug, platform, launch_type, executable_path, working_directory, launch_arguments, process_names, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (game_id, payload.name, payload.slug, payload.platform, payload.launch_type, payload.executable_path, payload.working_directory, payload.launch_arguments, json.dumps(payload.process_names), now, now),
        )
        AuditService.record(conn, action="GAME_CREATED", entity_type="GAME", entity_id=game_id, user_id=user["id"], new_value=payload.model_dump())
        row = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    return _game_response(dict(row))


@router.post("/devices/{pc_id}/games/{game_id}/authorize", response_model=LaunchAuthorizationResponse)
def authorize_launch(pc_id: str, game_id: str, payload: LaunchRequest, token: str | None = Depends(device_token)) -> LaunchAuthorizationResponse:
    with get_connection() as conn:
        authenticate_device(conn, pc_id, token)
        game = conn.execute("SELECT * FROM games WHERE id = ? AND enabled = 1", (game_id,)).fetchone()
        session = conn.execute("SELECT id, status, pc_id FROM sessions WHERE id = ?", (payload.session_id,)).fetchone()
        if not game or not session or session["pc_id"] != pc_id or session["status"] != "ACTIVE":
            raise HTTPException(status_code=403, detail="Game launch is not authorized")
        config = conn.execute("SELECT * FROM game_device_config WHERE game_id = ? AND pc_id = ?", (game_id, pc_id)).fetchone()
        if config and not config["enabled"]:
            raise HTTPException(status_code=403, detail="Game is unavailable on this device")
        return LaunchAuthorizationResponse(
            authorized=True, game_id=game_id, session_id=payload.session_id,
            launch_type=game["launch_type"], executable_path=(config["executable_path"] if config and config["executable_path"] else game["executable_path"]),
            working_directory=(config["working_directory"] if config and config["working_directory"] else game["working_directory"]),
            launch_arguments=(config["launch_arguments"] if config and config["launch_arguments"] else game["launch_arguments"]),
            process_names=json.loads(game["process_names"]),
        )