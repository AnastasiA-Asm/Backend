import pytest
from fastapi.testclient import TestClient

import moderation_service
from main import app
from schemas import PredictRequest

client = TestClient(app)

@pytest.fixture
def ad_payload():
    return {
        "seller_id": 42,
        "is_verified_seller": False,
        "item_id": 101,
        "name": "Велосипед",
        "description": "Городской велосипед",
        "category": 3,
        "images_qty": 0,
    }

@pytest.mark.parametrize(
    "verified, images_qty, expected",
    [(False, 0, True), (False, 1, False), (True, 0, False), (True, 1, False)],
)
def test_moderation_rule(ad_payload, verified, images_qty, expected):
    ad_payload["is_verified_seller"] = verified
    ad_payload["images_qty"] = images_qty
    ad = PredictRequest(**ad_payload)

    assert moderation_service.has_violation(ad) is expected

@pytest.mark.parametrize(
    "verified, images_qty, expected",
    [(False, 0, True), (False, 1, False), (True, 0, False)],
)
def test_predict_returns_boolean(ad_payload, verified, images_qty, expected):
    ad_payload["is_verified_seller"] = verified
    ad_payload["images_qty"] = images_qty

    response = client.post("/predict", json=ad_payload)

    assert response.status_code == 200
    assert response.json() is expected

@pytest.mark.parametrize(
    "field, value",
    [
        ("seller_id", "42"),
        ("is_verified_seller", "false"),
        ("item_id", "101"),
        ("name", 123),
        ("description", 123),
        ("category", "3"),
        ("images_qty", "1"),
        ("images_qty", -1),
    ],
)
def test_predict_rejects_invalid_values(ad_payload, field, value):
    ad_payload[field] = value

    response = client.post("/predict", json=ad_payload)

    assert response.status_code == 400
    assert response.json()["detail"][0]["field"] == f"body.{field}"

@pytest.mark.parametrize(
    "field",
    [
        "seller_id",
        "is_verified_seller",
        "item_id",
        "name",
        "description",
        "category",
        "images_qty",
    ],
)
def test_predict_requires_all_fields(ad_payload, field):
    del ad_payload[field]

    response = client.post("/predict", json=ad_payload)

    assert response.status_code == 400
    assert response.json()["detail"][0]["field"] == f"body.{field}"

def test_predict_handles_service_failure(ad_payload, monkeypatch):
    def fail(ad):
        raise RuntimeError("Test service failure")

    monkeypatch.setattr(moderation_service, "has_violation", fail)

    response = client.post("/predict", json=ad_payload)

    assert response.status_code == 500
    assert response.json() == {"detail": "Не удалось проверить объявление"}
