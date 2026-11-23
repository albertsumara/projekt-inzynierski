import pytest
from app.db.models.user_db import UserDb
from app.schemas.user import AddProductToUserRequest

pytestmark = pytest.mark.integration


def test_add_and_list_user_product_uses_database(
    api_client, db_session, seeded_product, seeded_user
):
    other_user = UserDb(name="Other user")
    db_session.add(other_user)
    db_session.commit()

    payload = AddProductToUserRequest(
        user_id=seeded_user.id,
        product_id=seeded_product.id,
        quantity=2,
        quantity_measurement=100,
    ).model_dump(mode="json")

    add_response = api_client.post("/api/v1/user/product", json=payload)

    assert add_response.status_code == 201

    other_payload = AddProductToUserRequest(
        user_id=other_user.id,
        product_id=seeded_product.id,
    ).model_dump(mode="json")
    other_add_response = api_client.post("/api/v1/user/product", json=other_payload)
    assert other_add_response.status_code == 201

    list_response = api_client.post(
        "/api/v1/user/products",
        json={"user_id": seeded_user.id},
    )

    assert list_response.status_code == 200
    user_product = list_response.json()["users_products"][0]
    assert user_product["product_id"] == seeded_product.id
    assert user_product["quantity"] == 2
    assert user_product["quantity_measurement"] == 100
    assert user_product["total_measurement"] == 200
    assert user_product["shelf_life_left"] == 7

    other_list_response = api_client.post(
        "/api/v1/user/products",
        json={"user_id": other_user.id},
    )
    assert other_list_response.status_code == 200
    assert len(other_list_response.json()["users_products"]) == 1
    assert (
        other_list_response.json()["users_products"][0]["product_id"]
        == seeded_product.id
    )


def test_list_user_products_requires_user_id(api_client):
    response = api_client.post("/api/v1/user/products", json={})

    assert response.status_code == 422
