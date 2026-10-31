
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "AI Document Search Backend Running"
    )


def test_chat_rejects_empty_question():
    response = client.post(
        "/chat",
        json={"question": ""}
    )

    assert response.status_code == 422


def test_chat_endpoint():
    with patch(
        "app.main.chat",
        return_value=(
            "This is a test answer.",
            [{"filename": "sample.pdf", "page": 1}]
        )
    ):
        response = client.post(
            "/chat",
            json={"question": "What is AI?"}
        )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "This is a test answer."
    assert data["sources"][0]["filename"] == "sample.pdf"
    assert data["sources"][0]["page"] == 1
