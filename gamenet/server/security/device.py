import sqlite3

from fastapi import Header, HTTPException, status

from gamenet.server.security.passwords import verify_secret


def authenticate_device(conn: sqlite3.Connection, pc_id: str, token: str | None) -> dict:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Device authentication required")
    row = conn.execute(
        "SELECT p.id, p.status, d.secret_hash FROM pcs p JOIN device_credentials d ON d.pc_id = p.id WHERE p.id = ?",
        (pc_id,),
    ).fetchone()
    if not row or not verify_secret(token, row["secret_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device credentials")
    return dict(row)


def device_token(x_device_token: str | None = Header(default=None)) -> str | None:
    return x_device_token