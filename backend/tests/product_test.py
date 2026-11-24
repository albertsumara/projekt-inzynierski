import pytest
from app.db.models.product_db import ProductDb

from tests.helpers import add_product_payload, create_image_bytes

pytestmark = pytest.mark.integration


def test_recognize_product_endpoint_uses_classifier_and_database(
    api_client, seeded_product
):
    response = api_client.post(
        "/api/v1/product/recognize",
        files={
            "file": (
                "apple.jpg",
                create_image_bytes("JPEG"),
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "apple.jpg",
        "recognitions": [
            {
                "id": seeded_product.id,
                "name": "Apple",
                "confidence": 0.95,
            }
        ],
    }


def test_add_product_persists_product_and_ingredients(api_client, db_session):
    create_response = api_client.post(
        "/api/v1/product",
        json=add_product_payload(),
    )

    assert create_response.status_code == 200
    created_product = create_response.json()
    assert created_product["name"] == "Banana"
    assert created_product["id_ml"] == 12
    assert created_product["ingredients"]["calories"] == 89

    persisted_product = (
        db_session.query(ProductDb).filter(ProductDb.id == created_product["id"]).one()
    )
    assert persisted_product.ingredients.calories == 89

    read_response = api_client.get(f"/api/v1/product/{created_product['id']}")

    assert read_response.status_code == 200
    assert [product["name"] for product in read_response.json()["products"]] == [
        "Banana"
    ]
    assert read_response.json()["products"][0]["ingredients"]["calories"] == 89


def test_get_product_filters_using_database(api_client, seeded_products):
    response = api_client.get(f"/api/v1/product/{seeded_products.id}")

    assert response.status_code == 200
    products = response.json()["products"]
    assert [product["name"] for product in products] == ["Apple"]
    assert products[0]["id"] == seeded_products.id


def test_get_missing_product_returns_empty_list(api_client, seeded_product):
    response = api_client.get(f"/api/v1/product/{seeded_product.id + 1000}")

    assert response.status_code == 200
    assert response.json() == {"products": []}


def test_invalid_image_returns_bad_request(api_client):
    response = api_client.post(
        "/api/v1/product/recognize",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The image file is empty."
