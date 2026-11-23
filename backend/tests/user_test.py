import pytest

from app.schemas.user import AddProductToUserRequest

pytestmark = pytest.mark.integration


def test_add_and_list_user_product_uses_database(
    api_client, seeded_product, seeded_user
):
    payload = AddProductToUserRequest(
        user_id=seeded_user.id,
        product_id=seeded_product.id,
        quantity=2,
        quantity_measurement=100,
    ).model_dump(mode="json")

    add_response = api_client.post("/api/v1/user/product", json=payload)

    assert add_response.status_code == 201

    list_response = api_client.post("/api/v1/user/products", json={})

    assert list_response.status_code == 200
    user_product = list_response.json()["users_products"][0]
    assert user_product["product_id"] == seeded_product.id
    assert user_product["quantity"] == 2
    assert user_product["quantity_measurement"] == 100
    assert user_product["total_measurement"] == 200
    assert user_product["shelf_life_left"] == 7
