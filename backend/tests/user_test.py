from app.services.interfaces.user_service_interface import UserServiceInterface
import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

from app.api.routes.user_router import UserRouter
from app.db.database import get_db
from tests.mocks import (
    MOCK_ADD_USER_PRODUCT_REQUEST,
    MOCK_ADD_USER_RESPONSE,
    MockUserService,
    create_user_products_response,
)


@pytest.fixture
def user_service():
    return MockUserService(
        list_response=create_user_products_response(),
        add_response=MOCK_ADD_USER_RESPONSE,
    )


@pytest.fixture
def user_client(user_service):
    app = FastAPI()
    app.include_router(UserRouter(user_service).get_router(), prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: object()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_user_mock_implements_service_interface():
    assert isinstance(MockUserService(), UserServiceInterface)


def test_add_user_product_endpoint(user_client, user_service):
    response = user_client.post(
        "/api/v1/user/product",
        json=MOCK_ADD_USER_PRODUCT_REQUEST.model_dump(mode="json"),
    )

    assert response.status_code == 201
    assert response.json() == {"id": 9}
    assert len(user_service.add_calls) == 1
    assert user_service.add_calls[0][0].product_id == 4


def test_list_user_products_endpoint(user_client, user_service):
    response = user_client.post("/api/v1/user/products", json={})

    assert response.status_code == 200
    assert response.json()["users_products"][0]["product_id"] == 4
    assert len(user_service.list_calls) == 1


def test_add_product_returns_not_found_when_user_does_not_exist():
    service = MockUserService(
        add_error=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    )
    app = FastAPI()
    app.include_router(UserRouter(service).get_router(), prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: object()

    payload = MOCK_ADD_USER_PRODUCT_REQUEST.model_copy(
        update={"user_id": 999}
    ).model_dump(mode="json")

    with TestClient(app) as client:
        response = client.post("/api/v1/user/product", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_remove_user_product_endpoint(user_client, user_service):
    response = user_client.delete("/api/v1/users/product/9")

    assert response.status_code == 204
    assert len(user_service.remove_calls) == 1
    assert user_service.remove_calls[0][0] == 9
