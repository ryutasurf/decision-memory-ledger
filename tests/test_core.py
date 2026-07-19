from src.db import vector_literal
from src.embeddings import VECTOR_DIMENSIONS, _local_embedding
from fastapi.testclient import TestClient
from src.app import app


def test_local_embedding_is_deterministic_and_sized():
    first = _local_embedding("same decision evidence")
    second = _local_embedding("same decision evidence")
    assert first == second
    assert len(first) == VECTOR_DIMENSIONS


def test_vector_literal():
    assert vector_literal([0.1, -0.2]) == "[0.10000000,-0.20000000]"


def test_health_and_home():
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"
    assert "Decisions should remember why they changed" in client.get("/").text
