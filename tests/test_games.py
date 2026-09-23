from gamenet.server.db import get_connection
from gamenet.server.security.passwords import hash_secret


def register_game_pc():
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO pcs (id, device_code, display_name, status, created_at, updated_at) VALUES ('PC-GAME-01', 'PC-GAME-01', 'Game PC', 'READY', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO device_credentials (pc_id, secret_hash, created_at) VALUES ('PC-GAME-01', ?, '2026-01-01T00:00:00Z')",
            (hash_secret("game-secret"),),
        )


def test_game_launch_requires_active_authorized_session(client, admin_client):
    register_game_pc()
    game = admin_client.post(
        "/api/v1/games",
        json={
            "name": "Test Arena", "slug": "test-arena", "platform": "WINDOWS",
            "launch_type": "DIRECT_EXE", "executable_path": "C:/Games/TestArena/game.exe",
            "process_names": ["game.exe"],
        },
    )
    assert game.status_code == 201
    game_id = game.json()["id"]
    assert any(item["id"] == game_id for item in client.get("/api/v1/games").json())

    customer = client.post(
        "/api/v1/customers", json={"name": "Game Customer", "pin": "1234"}
    ).json()
    grant = admin_client.post(
        f"/api/v1/customers/{customer['id']}/credit",
        json={"credit_type": "PAID", "seconds": 3600, "source": "GAME-TEST", "request_id": "GAME-GRANT-1"},
    )
    assert grant.status_code == 201
    session = admin_client.post(
        "/api/v1/sessions",
        json={"customer_id": customer["id"], "pc_id": "PC-GAME-01", "request_id": "GAME-SESSION-1"},
    ).json()

    authorized = client.post(
        f"/api/v1/devices/PC-GAME-01/games/{game_id}/authorize",
        headers={"X-Device-Token": "game-secret"},
        json={"session_id": session["id"]},
    )
    assert authorized.status_code == 200
    assert authorized.json()["authorized"] is True

    ended = admin_client.post(
        f"/api/v1/sessions/{session['id']}/end",
        json={"request_id": "GAME-END-1", "reason": "Test complete"},
    )
    assert ended.status_code == 200
    rejected = client.post(
        f"/api/v1/devices/PC-GAME-01/games/{game_id}/authorize",
        headers={"X-Device-Token": "game-secret"},
        json={"session_id": session["id"]},
    )
    assert rejected.status_code == 403