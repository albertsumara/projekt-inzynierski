import io

from app.db.models.product_db import MeasurementType
from app.schemas.ingredients import Ingredients
from app.schemas.product import (
    AddProductRequest,
    Product,
    RecognizedProduct,
    RecognizeProductResponse,
)
from app.schemas.recipe import (
    ListRecipesResponse,
    Recipe,
    RecipeDifficulty,
    RecipeNutrition,
    RecipeResponse,
)
from app.schemas.user import (
    AddProductToUserRequest,
    ListUsersProductsResponse,
    UsersProduct,
)
from PIL import Image

MOCK_ADD_PRODUCT_REQUEST = AddProductRequest(
    product=Product(
        id_ml=12,
        name="Banana",
        measurement_type=MeasurementType.WEIGHT,
        ingredients=Ingredients(
            calories=89,
            protein=1.1,
            fat=0.3,
            carbs=22.8,
            average_size=120,
            shelf_life=7,
        ),
    )
)

MOCK_ADD_USER_PRODUCT_REQUEST = AddProductToUserRequest(
    user_id=1,
    product_id=4,
    quantity=2,
    quantity_measurement=100,
)

MOCK_PRODUCTS = [{"id": 1, "name": "Apple"}]
MOCK_ADD_PRODUCT_RESPONSE = {"id": 1, "name": "Test product"}
MOCK_ADD_USER_RESPONSE = {"id": 9}


def create_image_bytes(image_format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size, color="red")
    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


def create_recognition_response():
    return RecognizeProductResponse(
        filename="apple.jpg",
        recognitions=[
            RecognizedProduct(id=4, name="Apple", confidence=0.98),
        ],
    )


def create_recipe_response():
    return ListRecipesResponse(
        recipes=[
            RecipeResponse(
                recipe=Recipe(
                    id=2,
                    name="Fruit salad",
                    time=10,
                    difficulty=RecipeDifficulty.EASY,
                    recipes_products=[],
                    is_vegetarian=True,
                    is_gluten_free=True,
                    instruction="Mix.",
                ),
                recipe_nutrition=RecipeNutrition(
                    calories=200,
                    protein=3,
                    carbs=40,
                    fat=2,
                ),
            )
        ]
    )


def create_user_products_response():
    return ListUsersProductsResponse(
        users_products=[
            UsersProduct(
                id=3,
                product_id=4,
                shelf_life_left=5,
                quantity=2,
                quantity_measurement=100,
                total_measurement=200,
            )
        ]
    )
