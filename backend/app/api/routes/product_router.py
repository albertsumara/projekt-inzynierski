from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.product import (
    AddProductRequest,
    ListProductsResponse,
    ListProductsRequest,
    ProductFilters,
    ProductResponse,
    RecognizeProductResponse,
)
from app.services.image_service import ImageService
from app.services.interfaces.product_service_interface import (
    ProductServiceInterface,
)
from app.services.product_service import ProductService


class ProductRouter:
    def __init__(self, service: ProductServiceInterface | None = None):
        self.service = (
            service if service is not None else ProductService(ImageService())
        )

        self.router = APIRouter()

        self.router.post(
            "/product/recognize",
            response_model=RecognizeProductResponse,
            status_code=status.HTTP_200_OK,
        )(self.recognize)

        self.router.post("/product", response_model=ProductResponse)(self.add_product)
        self.router.get(
            "/product/{product_id}",
            response_model=ListProductsResponse,
        )(self.get_product)
        self.router.post("/products", response_model=ListProductsResponse)(
            self.list_products
        )

    async def recognize(
        self,
        db: Annotated[Session, Depends(get_db)],
        file: UploadFile = File(...),
    ):
        return await self.service.recognize_product(file, db)

    def add_product(
        self,
        product: AddProductRequest,
        db: Annotated[Session, Depends(get_db)],
    ):
        return self.service.add_product(product, db)

    def get_product(
        self,
        product_id: int,
        db: Annotated[Session, Depends(get_db)],
    ):
        params = ListProductsRequest(filters=ProductFilters(id=product_id))
        return self.service.list_products(params, db)

    def list_products(
        self,
        db: Annotated[Session, Depends(get_db)],
        params: ListProductsRequest | None = None,
    ):
        if params is None:
            params = ListProductsRequest()

        return self.service.list_products(params, db)

    def get_router(self) -> APIRouter:
        return self.router
