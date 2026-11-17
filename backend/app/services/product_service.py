from models.image_classifier import ImageClassifier
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session

from app.db.models.ingredients import IngredientsDb
from app.db.models.product import ProductDb
from app.errors.product_errors import (
    ProductDbError,
    ProductNameAlreadyExistsError,
)
from app.mappers import ProductMapper
from app.schemas import FilterOperator, SortOrder
from app.schemas.product import (
    ListProductsRequest,
    ProductFilters,
    ProductSortField,
)
from app.services.image_service import ImageService
from app.utils.database import raise_for_constraint


class ProductService:
    def __init__(self, image_service: ImageService, image_classifier: ImageClassifier):
        self.image_service = image_service
        self.image_classifier = image_classifier

    def recognize_product(
        self,
        image_bytes: bytes,
        content_type: str | None,
    ) -> list[dict]:
        image = self.image_service.load_image(
            image_bytes,
            content_type,
        )

        return self.image_classifier.recognize(image)

    @staticmethod
    def add_product(product, db: Session):

        new_product = ProductMapper.to_product(product)

        try:
            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            return new_product
        except SQLAlchemyIntegrityError as e:
            db.rollback()

            raise_for_constraint(
                e,
                {"products_name_key": ProductNameAlreadyExistsError},
            )
            raise ProductDbError("Database error.") from e

    @staticmethod
    def list_products(params: ListProductsRequest, db: Session):

        query = db.query(ProductDb).join(ProductDb.ingredients)

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

                if number_filter is None:
                    continue

                if number_filter.operator == FilterOperator.MORE:
                    query = query.filter(column > number_filter.value)

                elif number_filter.operator == FilterOperator.LESS:
                    query = query.filter(column < number_filter.value)

                elif number_filter.operator == FilterOperator.EQUALS:
                    query = query.filter(column == number_filter.value)

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
