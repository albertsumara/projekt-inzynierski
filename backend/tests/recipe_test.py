import pytest
from app.api.routes.recipe_router import RecipeRouter
from app.db.database import get_db
from app.services.interfaces.recipe_service_interface import RecipeServiceInterface
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.mocks import MockRecipeService, create_recipe_response


@pytest.fixture
def recipe_service():
    return MockRecipeService(create_recipe_response())


@pytest.fixture
def recipe_client(recipe_service):
    app = FastAPI()
    app.include_router(RecipeRouter(recipe_service).get_router(), prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: object()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_recipe_mock_implements_service_interface():
    assert isinstance(MockRecipeService(), RecipeServiceInterface)


def test_list_recipes_endpoint(recipe_client, recipe_service):
    response = recipe_client.post("/api/v1/recipe", json={})

    assert response.status_code == 200
    assert response.json()["recipes"][0]["recipe"]["name"] == "Fruit salad"
    assert len(recipe_service.calls) == 1
