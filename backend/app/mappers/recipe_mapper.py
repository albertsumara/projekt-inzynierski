from collections.abc import Iterable
from typing import Any

from sqlalchemy.engine import Row

from app.db.queries.recipe_queries import (
    RecipeAggregateField,
    to_db_difficulty,
)
from app.db.models.product_db import MeasurementType, ProductDb
from app.db.models.recipe_db import RecipeDb
from app.db.models.recipes_products_db import RecipesProductsDb
from app.schemas.recipe import (
    ListRecipesResponse,
    Recipe,
    RecipeDifficulty,
    RecipeNutrition,
    RecipeResponse,
    RecipeSeed,
    RecipeSeedProduct,
    RecipesProduct,
)


class RecipeMapper:
    @staticmethod
    def to_recipe(data: RecipeDb) -> Recipe:
        return Recipe(
            id=data.id,
            name=data.name,
            time=data.time,
            difficulty=RecipeDifficulty(data.difficulty.value),
            recipes_products=[
                RecipeMapper.to_recipe_product(recipe_product)
                for recipe_product in data.recipes_products
            ],
            is_vegetarian=data.is_vegetarian,
            is_gluten_free=data.is_gluten_free,
            instruction=data.instruction,
        )

    @staticmethod
    def to_recipe_product(data: RecipesProductsDb) -> RecipesProduct:
        return RecipesProduct(
            product_id=data.product_id,
            product_name=data.product.name,
            quantity_measurement=float(data.quantity_measurement),
            quantity=data.quantity,
            measurement=RecipeMapper.to_measurement_unit(data.product),
        )

    @staticmethod
    def to_measurement_unit(product: ProductDb) -> str:
        if product.measurement_type == MeasurementType.COUNTABLE:
            return "pcs"
        elif product.measurement_type == MeasurementType.VOLUME:
            return "ml"
        return "g"

    @staticmethod
    def to_recipe_db(
        data: RecipeSeed,
        products: dict[int, ProductDb],
    ) -> RecipeDb:
        return RecipeDb(
            name=data.name,
            time=data.time,
            difficulty=to_db_difficulty(data.difficulty),
            is_vegetarian=data.is_vegetarian,
            is_gluten_free=data.is_gluten_free,
            instruction=data.instruction,
            recipes_products=[
                RecipeMapper.to_recipes_product_db(
                    ingredient, products[ingredient.id_ml]
                )
                for ingredient in data.ingredients
            ],
        )

    @staticmethod
    def to_recipes_product_db(
        data: RecipeSeedProduct,
        product: ProductDb,
    ) -> RecipesProductsDb:
        quantity_measurement = data.quantity_measurement
        if quantity_measurement is None:
            quantity_measurement = product.ingredients.average_size

        return RecipesProductsDb(
            product=product,
            quantity_measurement=round(quantity_measurement, 2),
            quantity=data.quantity,
        )

    @staticmethod
    def to_recipe_nutrition(data: Row[Any]) -> RecipeNutrition:
        return RecipeNutrition(
            calories=round(getattr(data, RecipeAggregateField.CALORIES.value), 2),
            protein=round(getattr(data, RecipeAggregateField.PROTEIN.value), 2),
            carbs=round(getattr(data, RecipeAggregateField.CARBS.value), 2),
            fat=round(getattr(data, RecipeAggregateField.FAT.value), 2),
        )

    @staticmethod
    def to_recipe_response(data: Row[Any]) -> RecipeResponse:
        recipe = RecipeMapper.to_recipe(data[0])
        nutrition = RecipeMapper.to_recipe_nutrition(data)
        return RecipeResponse(recipe=recipe, recipe_nutrition=nutrition)

    @staticmethod
    def to_list_recipes_response(
        data: Iterable[Row[Any]],
    ) -> ListRecipesResponse:
        return ListRecipesResponse(
            recipes=[RecipeMapper.to_recipe_response(row) for row in data]
        )
