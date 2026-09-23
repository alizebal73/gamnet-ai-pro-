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
from gamenet.server.db import run_migrations  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    run_migrations()
    yield
    if _test_db.exists():
        _test_db.unlink(missing_ok=True)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
