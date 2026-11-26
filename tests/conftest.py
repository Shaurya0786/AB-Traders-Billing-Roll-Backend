import os
import pathlib
import tempfile

# A throwaway SQLite database for every test run; set before the app is imported.
_db = pathlib.Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_db}"
os.environ.setdefault("ADMIN_API_KEY", "test-admin-key")
for k in ("GMAIL_SENDER", "GMAIL_APP_PASSWORD", "NOTIFY_EMAIL"):
    os.environ.pop(k, None)

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    from backend.main import app
    with TestClient(app) as c:
        yield c
