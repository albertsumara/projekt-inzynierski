import json

from paths import (
    CUSTOM_FOOD_CLASSES_PATH,
    CUSTOM_FOOD_INGREDIENTS_PATH,
    IMAGENET_FOOD_CLASSES_PATH,
    IMAGENET_FOOD_INGREDIENTS_PATH,
)
from sqlalchemy.orm import Session

from app.db.models import ProductDb
from app.mappers.product_mapper import ProductMapper
from app.mappers.user_mapper import UserMapper
from app.schemas.product import AddProductRequest
from app.schemas.user import User


def seed_data(db: Session):
    _seed_products(db)
    _seed_users(db)


def _seed_products(db: Session):
    try:
        _seed_from_json(
            db,
            IMAGENET_FOOD_CLASSES_PATH,
            IMAGENET_FOOD_INGREDIENTS_PATH,
        )

        _seed_from_json(
            db,
            CUSTOM_FOOD_CLASSES_PATH,
            CUSTOM_FOOD_INGREDIENTS_PATH,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise


def _seed_users(db: Session):
    test_user_data = {"name": "Test User"}
    test_user_schema = User.model_validate(test_user_data)
    test_user = UserMapper.to_create_user(test_user_schema)
    db.add(test_user)
    db.commit()


def _seed_from_json(
    db: Session,
    classes_path,
    ingredients_path,
):

    with classes_path.open("r", encoding="utf-8") as file:
        classes_data = json.load(file)

    with ingredients_path.open("r", encoding="utf-8") as file:
        ingredients_data = json.load(file)

    existing_ids = {id_ml for (id_ml,) in db.query(ProductDb.id_ml).all()}

    for id_ml, name in classes_data.items():
        if int(id_ml) in existing_ids:
            continue

        ingredient_data = ingredients_data.get(id_ml)

        if ingredient_data is None:
            continue

        product_data = {
            "product": {
                "id_ml": int(id_ml),
                "name": name,
                "ingredients": ingredient_data,
            }
        }

        product_schema = AddProductRequest.model_validate(product_data)
        product = ProductMapper.to_product(product_schema)
        db.add(product)
        existing_ids.add(int(id_ml))
