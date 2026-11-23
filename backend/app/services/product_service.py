from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session

from app.db.queries.product_queries import (
    get_product_by_ml,
    get_products_by_ml_ids,
    list_products as query_products,
)
from app.errors.image_errors import ImageError
from app.errors.product_errors import (
    ProductDbError,
    ProductNameAlreadyExistsError,
)
from app.mappers import ProductMapper
from app.schemas.product import (
    ListProductsResponse,
    ListProductsRequest,
    ProductResponse,
    Recognition,
    RecognizeProductResponse,
)
from app.services.image_service import InvalidImageError
from app.services.interfaces.image_service_interface import ImageServiceInterface
from app.services.interfaces.product_service_interface import (
    ProductServiceInterface,
)
from app.utils.database import raise_for_constraint


class ProductService(ProductServiceInterface):
    def __init__(self, image_service: ImageServiceInterface):
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
    def add_product(product, db: Session) -> ProductResponse:

        new_product = ProductMapper.to_product_db(product)

        try:
            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            return ProductMapper.to_product_response(new_product)
        except SQLAlchemyIntegrityError as e:
            db.rollback()

            raise_for_constraint(
                e,
                {"products_name_key": ProductNameAlreadyExistsError},
            )
            raise ProductDbError("Database error.") from e

    @staticmethod
    def get_product_by_id_ml(id_ml: int, db: Session):
        return get_product_by_ml(db, id_ml)

    @staticmethod
    def _get_recognized_products(
        recognitions: list[Recognition],
        db: Session,
    ):
        ids_ml = [r.id_ml for r in recognitions]
        products = get_products_by_ml_ids(db, ids_ml)
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
    def list_products(
        params: ListProductsRequest,
        db: Session,
    ) -> ListProductsResponse:
        products = query_products(db, params)
        return ProductMapper.to_list_products_response(products)
