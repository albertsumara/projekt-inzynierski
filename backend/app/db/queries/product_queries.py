from collections.abc import Collection

from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.db.models.ingredients_db import IngredientsDb
from app.db.models.product_db import ProductDb
from app.schemas import SortOrder
from app.schemas.product import (
    ListProductsRequest,
    ProductFilters,
    ProductSortField,
)
from app.utils.filters import apply_number_filter


def get_product_by_ml(db: Session, id_ml: int) -> ProductDb | None:
    query = select(ProductDb).where(ProductDb.id_ml == id_ml)
    return db.execute(query).scalar_one_or_none()


def get_products_by_ml_ids(
    db: Session,
    ids_ml: Collection[int],
    *,
    with_ingredients: bool = False,
) -> list[ProductDb]:
    if not ids_ml:
        return []

    query = select(ProductDb).where(ProductDb.id_ml.in_(ids_ml))
    if with_ingredients:
        query = query.options(joinedload(ProductDb.ingredients))
    return list(db.execute(query).scalars().all())


def get_product_ml_ids(db: Session) -> set[int]:
    query = select(ProductDb.id_ml)
    return set(db.execute(query).scalars().all())


def list_products(db: Session, params: ListProductsRequest) -> list[ProductDb]:
    query = (
        db.query(ProductDb)
        .join(ProductDb.ingredients)
        .options(contains_eager(ProductDb.ingredients))
    )

    if params and params.filters:
        filters = params.filters

        if filters.id is not None:
            query = query.filter(ProductDb.id == filters.id)

        if filters.id_ml is not None:
            query = query.filter(ProductDb.id_ml == filters.id_ml)

        filter_columns = {
            field: getattr(IngredientsDb, field)
            for field in ProductFilters.model_fields
            if field not in ("id", "id_ml")
        }

        for field, column in filter_columns.items():
            number_filter = getattr(filters, field)
            if number_filter is not None:
                query = apply_number_filter(query, column, number_filter)

    if params and params.sort:
        sort_columns = {
            ProductSortField.NAME: ProductDb.name,
            ProductSortField.CALORIES: IngredientsDb.calories,
            ProductSortField.PROTEIN: IngredientsDb.protein,
            ProductSortField.CARBS: IngredientsDb.carbs,
            ProductSortField.FAT: IngredientsDb.fat,
            ProductSortField.SHELF_LIFE: IngredientsDb.shelf_life,
        }

        column = sort_columns[params.sort.field]
        if params.sort.order == SortOrder.ASC:
            query = query.order_by(column.asc())
        else:
            query = query.order_by(column.desc())

    return query.all()
