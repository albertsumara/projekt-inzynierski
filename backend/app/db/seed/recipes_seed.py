import json

from paths import RECIPES_SEED_PATH
from sqlalchemy.orm import Session

from app.db.models import RecipeDb
from app.db.queries.product_queries import get_products_by_ml_ids
from app.mappers.recipe_mapper import RecipeMapper
from app.schemas.recipe import RecipeSeed


def seed_recipes(db: Session) -> None:
    try:
        with RECIPES_SEED_PATH.open("r", encoding="utf-8") as file:
            recipes_data = json.load(file)

        existing_names = {name for (name,) in db.query(RecipeDb.name).all()}

        for recipe_data in recipes_data:
            recipe = RecipeSeed.model_validate(recipe_data)
            if recipe.name in existing_names:
                continue

            product_ids = {ingredient.id_ml for ingredient in recipe.ingredients}
            products = get_products_by_ml_ids(
                db,
                product_ids,
                with_ingredients=True,
            )
            products_by_id_ml = {product.id_ml: product for product in products}
            missing_product_ids = product_ids - products_by_id_ml.keys()

            if missing_product_ids:
                raise ValueError(
                    f"Recipe '{recipe.name}' references products that are not seeded: "
                    f"{sorted(missing_product_ids)}"
                )

            db.add(RecipeMapper.to_recipe_db(recipe, products_by_id_ml))
            existing_names.add(recipe.name)

        db.commit()
    except Exception:
        db.rollback()
        raise
