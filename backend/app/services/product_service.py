from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session

from app.db.models.ingredients import IngredientsDb
from app.db.models.product import ProductDb
from app.errors.image_errors import ImageError
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
    Recognition,
    RecognizeProductResponse,
)
from app.services.image_service import ImageService, InvalidImageError
from app.utils.database import raise_for_constraint


class ProductService:
    def __init__(self, image_service: ImageService):
        self.image_service = image_service

    async def recognize_product(
        self, file: UploadFile, db: Session
    ) -> RecognizeProductResponse:
        try:
            image_bytes = await file.read()
            recognitions = self.image_service.recognize(
                image_bytes,
                file.content_type,
            )
            recognitions_dto = self._get_recognized_products(recognitions, db)
            return ProductMapper.to_recognition_response(
                file.filename, recognitions_dto
            )
        except (ImageError, InvalidImageError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        finally:
            await file.close()

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
    def get_product_by_id_ml(id_ml: int, db: Session):
        query = select(ProductDb).where(ProductDb.id_ml == id_ml)
        return db.execute(query).scalar_one_or_none()

    @staticmethod
    def _get_recognized_products(
        recognitions: Recognition,
        db: Session,
    ):
        ids_ml = [r.id_ml for r in recognitions]

        query = select(ProductDb).where(ProductDb.id_ml.in_(ids_ml))
        products = db.execute(query).scalars().all()
        products_map = {p.id_ml: p for p in products}

        return [
            ProductMapper.to_recognition(
                products_map[recognition.id_ml],
                recognition.confidence,
            )
            for recognition in recognitions
            if recognition.id_ml in products_map
        ]

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
