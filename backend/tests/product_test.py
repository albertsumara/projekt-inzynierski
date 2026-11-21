import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

from app.api.routes.product_router import ProductRouter
from app.db.database import get_db
from app.errors.image_errors import InvalidImageSizeError
from app.services.interfaces.product_service_interface import ProductServiceInterface
from app.services.product_service import ProductService
from tests.mocks import (
    MOCK_ADD_PRODUCT_REQUEST,
    MOCK_PRODUCTS,
    MockImageService,
    MockProductService,
    create_recognition_response,
)


@pytest.fixture
def product_service():
    return MockProductService(
        recognize_response=create_recognition_response(),
        products=MOCK_PRODUCTS,
    )


@pytest.fixture
def product_client(product_service):
    app = FastAPI()
    app.include_router(ProductRouter(product_service).get_router(), prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: object()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_product_mock_implements_service_interface():
    assert isinstance(MockProductService(), ProductServiceInterface)


def test_recognize_product_endpoint(product_client, product_service):
    response = product_client.post(
        "/api/v1/product/recognize",
        files={"file": ("apple.jpg", b"image-data", "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "apple.jpg"
    assert response.json()["recognitions"][0]["name"] == "Apple"
    assert product_service.recognize_calls[0][0] == b"image-data"
    assert product_service.recognize_calls[0][1] == "image/jpeg"


def test_add_product_endpoint(product_client, product_service):
    response = product_client.post(
        "/api/v1/product",
        json=MOCK_ADD_PRODUCT_REQUEST.model_dump(mode="json"),
    )

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Test product"}
    assert len(product_service.add_calls) == 1
    assert product_service.add_calls[0][0].product.name == "Banana"


def test_get_product_endpoint_filters_by_product_id(product_client, product_service):
    response = product_client.get("/api/v1/product/5")

    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "Apple"}]
    assert product_service.list_calls[0][0].filters.id == 5


def test_list_products_endpoint(product_client, product_service):
    response = product_client.post("/api/v1/products", json={})

    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "Apple"}]
    assert len(product_service.list_calls) == 1


def test_add_product_returns_conflict_when_product_already_exists():
    service = MockProductService(
        add_error=HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already exists.",
        )
    )
    app = FastAPI()
    app.include_router(ProductRouter(service).get_router(), prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: object()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/product",
            json=MOCK_ADD_PRODUCT_REQUEST.model_dump(mode="json"),
        )

    assert response.status_code == 409
    assert response.json()["detail"] == "Product already exists."


def test_get_missing_product_returns_not_found():
    service = MockProductService(
        list_error=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )
    )
    app = FastAPI()
    app.include_router(ProductRouter(service).get_router(), prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: object()

    with TestClient(app) as client:
        response = client.get("/api/v1/product/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_recognize_endpoint_returns_400_for_image_custom_error():
    image_service = MockImageService(
        recognize_error=InvalidImageSizeError(
            "The image file cannot be larger than 8 MB."
        )
    )
    app = FastAPI()
    app.include_router(
        ProductRouter(ProductService(image_service)).get_router(),
        prefix="/api/v1",
    )
    app.dependency_overrides[get_db] = lambda: object()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/product/recognize",
            files={"file": ("large.jpg", b"image-data", "image/jpeg")},
        )

    assert response.status_code == 400
    assert "8 MB" in response.json()["detail"]

