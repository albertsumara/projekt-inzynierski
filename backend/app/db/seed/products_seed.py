import json

from paths import (
    CUSTOM_FOOD_CLASSES_PATH,
    CUSTOM_FOOD_INGREDIENTS_PATH,
    CUSTOM_PRODUCT_MEASUREMENT_TYPES_PATH,
    IMAGENET_FOOD_CLASSES_PATH,
    IMAGENET_FOOD_INGREDIENTS_PATH,
    IMAGENET_PRODUCT_MEASUREMENT_TYPES_PATH,
)
from sqlalchemy.orm import Session

from app.db.models import ProductDb
from app.db.models.product_db import MeasurementType
from app.mappers.product_mapper import ProductMapper
from app.schemas.product import AddProductRequest


def seed_products(db: Session) -> None:
    try:
        with IMAGENET_PRODUCT_MEASUREMENT_TYPES_PATH.open(
            "r", encoding="utf-8"
        ) as file:
            imagenet_measurement_types = json.load(file)
        with CUSTOM_PRODUCT_MEASUREMENT_TYPES_PATH.open("r", encoding="utf-8") as file:
            custom_measurement_types = json.load(file)

        _seed_from_json(
            db,
            IMAGENET_FOOD_CLASSES_PATH,
            IMAGENET_FOOD_INGREDIENTS_PATH,
            imagenet_measurement_types,
        )
        _seed_from_json(
            db,
            CUSTOM_FOOD_CLASSES_PATH,
            CUSTOM_FOOD_INGREDIENTS_PATH,
            custom_measurement_types,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise


def _seed_from_json(
    db: Session,
    classes_path,
    ingredients_path,
    measurement_types: dict[str, str],
) -> None:
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
                "measurement_type": measurement_types.get(
                    id_ml,
                    MeasurementType.WEIGHT.value,
                ),
                "ingredients": ingredient_data,
            }
        }
        product_schema = AddProductRequest.model_validate(product_data)
        db.add(ProductMapper.to_product(product_schema))
        existing_ids.add(int(id_ml))
