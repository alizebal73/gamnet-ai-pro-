import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Use isolated test database before app imports settings-dependent modules
_test_db = Path(__file__).parent / "_test_gamenet.db"
if _test_db.exists():
    _test_db.unlink()

os.environ["DATABASE_PATH"] = str(_test_db)
os.environ["APP_ENV"] = "test"

from gamenet.server.main import app  # noqa: E402
from gamenet.server.db import get_connection, run_migrations  # noqa: E402
from gamenet.server.security.passwords import hash_secret  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    run_migrations()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO users
                (id, username, password_hash, display_name, status, created_at, updated_at)
            VALUES ('USER-TEST-OPERATOR', 'test_operator', ?, 'Test Operator', 'ACTIVE',
                    '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
            """,
            (hash_secret("test-password"),),
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO user_roles (user_id, role_id, assigned_at)
            VALUES ('USER-TEST-OPERATOR', 'ROLE-OPERATOR', '2026-01-01T00:00:00Z')
            """
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO users
                (id, username, password_hash, display_name, status, created_at, updated_at)
            VALUES ('USER-TEST-OWNER', 'test_owner', ?, 'Test Owner', 'ACTIVE',
                    '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
            """,
            (hash_secret("owner-password"),),
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO user_roles (user_id, role_id, assigned_at)
            VALUES ('USER-TEST-OWNER', 'ROLE-OWNER', '2026-01-01T00:00:00Z')
            """
        )
    yield
    if _test_db.exists():
        _test_db.unlink(missing_ok=True)


@pytest.fixture
def client() -> TestClient:
    test_client = TestClient(app)
    response = test_client.post(
        "/api/v1/auth/login",
        json={"username": "test_operator", "password": "test-password"},
    )
    assert response.status_code == 200
    test_client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )
    return test_client


@pytest.fixture
def admin_client() -> TestClient:
    test_client = TestClient(app)
    response = test_client.post(
        "/api/v1/auth/login",
        json={"username": "test_owner", "password": "owner-password"},
    )
    assert response.status_code == 200
    test_client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )
    return test_client
