from enum import Enum
from typing import Any

from sqlalchemy import func
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.sql.selectable import Subquery

from app.db.models.ingredients_db import IngredientsDb
from app.db.models.product_db import ProductDb
from app.db.models.recipe_db import (
    RecipeDb,
)
from app.db.models.recipe_db import (
    RecipeDifficulty as DbRecipeDifficulty,
)
from app.db.models.recipes_products_db import RecipesProductsDb
from app.schemas.recipe import (
    ListRecipesRequest,
    RecipeDifficulty,
    RecipeSortField,
)
from app.schemas.sort import SortOrder
from app.utils.filters import apply_number_filter


class RecipeAggregateField(str, Enum):
    RECIPE_ID = "recipe_id"
    PRODUCTS_COUNT = "products_count"
    TOTAL_WEIGHT = "total_weight"
    CALORIES = "calories"
    PROTEIN = "protein"
    CARBS = "carbs"
    FAT = "fat"


def to_db_difficulty(difficulty: RecipeDifficulty) -> DbRecipeDifficulty:
    return DbRecipeDifficulty[difficulty.name]


def list_recipes(db: Session, params: ListRecipesRequest) -> list[Row[Any]]:
    recipe_stats = get_recipe_stats(db)
    nutrition_fields = (
        RecipeAggregateField.CALORIES,
        RecipeAggregateField.PROTEIN,
        RecipeAggregateField.CARBS,
        RecipeAggregateField.FAT,
    )
    query = (
        db.query(
            RecipeDb,
            *(
                func.coalesce(recipe_stats.c[field.value], 0).label(field.value)
                for field in nutrition_fields
            ),
        )
        .options(
            selectinload(RecipeDb.recipes_products).joinedload(
                RecipesProductsDb.product
            )
        )
        .outerjoin(
            recipe_stats,
            recipe_stats.c[RecipeAggregateField.RECIPE_ID.value] == RecipeDb.id,
        )
    )

    if params.filters:
        filters = params.filters

        if filters.id is not None:
            query = query.filter(RecipeDb.id == filters.id)

        if filters.name is not None:
            query = query.filter(RecipeDb.name.icontains(filters.name, autoescape=True))

        if filters.time is not None:
            query = apply_number_filter(query, RecipeDb.time, filters.time)

        if filters.products_count is not None:
            query = apply_number_filter(
                query,
                func.coalesce(
                    recipe_stats.c[RecipeAggregateField.PRODUCTS_COUNT.value],
                    0,
                ),
                filters.products_count,
            )

        for field in (
            RecipeAggregateField.CALORIES,
            RecipeAggregateField.PROTEIN,
            RecipeAggregateField.CARBS,
            RecipeAggregateField.FAT,
        ):
            number_filter = getattr(filters, field.value)
            if number_filter is not None:
                query = apply_number_filter(
                    query,
                    func.coalesce(recipe_stats.c[field.value], 0),
                    number_filter,
                )

        if filters.difficulty:
            query = query.filter(
                RecipeDb.difficulty.in_(
                    [to_db_difficulty(difficulty) for difficulty in filters.difficulty]
                )
            )

        if filters.is_vegetarian is not None:
            query = query.filter(RecipeDb.is_vegetarian == filters.is_vegetarian)

        if filters.is_gluten_free is not None:
            query = query.filter(RecipeDb.is_gluten_free == filters.is_gluten_free)

        if filters.product_ids:
            products_query = db.query(RecipesProductsDb.recipe_id).filter(
                RecipesProductsDb.product_id.in_(set(filters.product_ids))
            )

            if filters.match_all_products:
                products_query = products_query.group_by(
                    RecipesProductsDb.recipe_id
                ).having(
                    func.count(func.distinct(RecipesProductsDb.product_id))
                    == len(set(filters.product_ids))
                )
            else:
                products_query = products_query.distinct()

            query = query.filter(RecipeDb.id.in_(products_query))

    if params.sort:
        sort_columns = {
            RecipeSortField.NAME: RecipeDb.name,
            RecipeSortField.TIME: RecipeDb.time,
            RecipeSortField.DIFFICULTY: RecipeDb.difficulty,
            RecipeSortField.PRODUCTS_COUNT: func.coalesce(
                recipe_stats.c[RecipeAggregateField.PRODUCTS_COUNT.value],
                0,
            ),
            RecipeSortField.CALORIES: func.coalesce(
                recipe_stats.c[RecipeAggregateField.CALORIES.value], 0
            ),
            RecipeSortField.PROTEIN: func.coalesce(
                recipe_stats.c[RecipeAggregateField.PROTEIN.value], 0
            ),
            RecipeSortField.CARBS: func.coalesce(
                recipe_stats.c[RecipeAggregateField.CARBS.value], 0
            ),
            RecipeSortField.FAT: func.coalesce(
                recipe_stats.c[RecipeAggregateField.FAT.value], 0
            ),
            RecipeSortField.TOTAL_WEIGHT: func.coalesce(
                recipe_stats.c[RecipeAggregateField.TOTAL_WEIGHT.value], 0
            ),
        }

        column = sort_columns[params.sort.field]
        if params.sort.order == SortOrder.ASC:
            query = query.order_by(column.asc(), RecipeDb.id.asc())
        else:
            query = query.order_by(column.desc(), RecipeDb.id.asc())

    return query.all()


def get_recipe_stats(db: Session) -> Subquery:
    ingredient_weight = (
        RecipesProductsDb.quantity_measurement * RecipesProductsDb.quantity
    )
    nutrient_columns = (
        (RecipeAggregateField.CALORIES, IngredientsDb.calories),
        (RecipeAggregateField.PROTEIN, IngredientsDb.protein),
        (RecipeAggregateField.CARBS, IngredientsDb.carbs),
        (RecipeAggregateField.FAT, IngredientsDb.fat),
    )
    nutrient_totals = [
        func.sum(func.coalesce(nutrient_column, 0) * ingredient_weight / 100).label(
            field.value
        )
        for field, nutrient_column in nutrient_columns
    ]

    return (
        db.query(
            RecipesProductsDb.recipe_id.label(RecipeAggregateField.RECIPE_ID.value),
            func.count(func.distinct(RecipesProductsDb.product_id)).label(
                RecipeAggregateField.PRODUCTS_COUNT.value
            ),
            func.sum(ingredient_weight).label(RecipeAggregateField.TOTAL_WEIGHT.value),
            *nutrient_totals,
        )
        .join(ProductDb, ProductDb.id == RecipesProductsDb.product_id)
        .outerjoin(IngredientsDb, IngredientsDb.product_id == ProductDb.id)
        .group_by(RecipesProductsDb.recipe_id)
        .subquery()
    )
