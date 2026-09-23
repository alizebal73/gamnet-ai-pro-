import hashlib
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from gamenet.server.config import settings
from gamenet.server.db import get_connection, utc_now_iso
from gamenet.server.security.passwords import verify_secret

_bearer = HTTPBearer(auto_error=False)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(conn: sqlite3.Connection, user_id: str) -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    created_at = datetime.now(UTC).replace(microsecond=0)
    expires_at = created_at + timedelta(hours=settings.auth_session_hours)
    conn.execute(
        """
        INSERT INTO auth_sessions (token_hash, user_id, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (_hash_token(token), user_id, created_at.isoformat().replace("+00:00", "Z"), expires_at.isoformat().replace("+00:00", "Z")),
    )
    return token, expires_at.isoformat().replace("+00:00", "Z")


def login(conn: sqlite3.Connection, username: str, password: str) -> tuple[str, str, dict] | None:
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND status = 'ACTIVE'", (username,)
    ).fetchone()
    if not row or not verify_secret(password, row["password_hash"]):
        return None

    roles = conn.execute(
        """
        SELECT r.name FROM roles r
        JOIN user_roles ur ON ur.role_id = r.id
        WHERE ur.user_id = ?
        ORDER BY r.name
        """,
        (row["id"],),
    ).fetchall()
    token, expires_at = create_session(conn, row["id"])
    return token, expires_at, {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "roles": [role["name"] for role in roles],
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    now = utc_now_iso()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.username, u.display_name
            FROM auth_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = ?
              AND s.revoked_at IS NULL
              AND s.expires_at > ?
              AND u.status = 'ACTIVE'
            """,
            (_hash_token(credentials.credentials), now),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

        roles = conn.execute(
            """
            SELECT r.name FROM roles r
            JOIN user_roles ur ON ur.role_id = r.id
            WHERE ur.user_id = ?
            """,
            (row["id"],),
        ).fetchall()
        return {
            "id": row["id"],
            "username": row["username"],
            "display_name": row["display_name"],
            "roles": [role["name"] for role in roles],
        }


def require_permission(permission_name: str):
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        with get_connection() as conn:
            allowed = conn.execute(
                """
                SELECT 1
                FROM user_roles ur
                JOIN role_permissions rp ON rp.role_id = ur.role_id
                JOIN permissions p ON p.id = rp.permission_id
                WHERE ur.user_id = ? AND p.name = ?
                LIMIT 1
                """,
                (user["id"], permission_name),
            ).fetchone()
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return user

    return dependency