import pytest
from fastapi.testclient import TestClient

from chess_api.dependencies import reset_singletons
from chess_api.main import app


@pytest.fixture()
def client():
    reset_singletons()  # aísla el estado en memoria entre tests
    with TestClient(app) as c:
        yield c
    reset_singletons()
