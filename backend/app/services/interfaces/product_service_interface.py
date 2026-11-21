from abc import ABC, abstractmethod

from app.schemas.product import (
    AddProductRequest,
    ListProductsRequest,
    RecognizeProductResponse,
)
from fastapi import UploadFile
from sqlalchemy.orm import Session


class ProductServiceInterface(ABC):
    @abstractmethod
    async def recognize_product(
        self,
        file: UploadFile,
        db: Session,
    ) -> RecognizeProductResponse:
        pass

    @abstractmethod
    def add_product(
        self,
        product: AddProductRequest,
        db: Session,
    ):
        pass

    @abstractmethod
    def get_product_by_id_ml(
        self,
        id_ml: int,
        db: Session,
    ):
        pass

    @abstractmethod
    def list_products(
        self,
        params: ListProductsRequest,
        db: Session,
    ):
        pass
