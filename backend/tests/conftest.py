from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture()
def app() -> object:
    return create_app(Settings(database_url="sqlite:///:memory:", log_level="WARNING"))


@pytest.fixture()
def client(app: object) -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
