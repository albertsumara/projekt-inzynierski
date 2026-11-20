from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.product import (
    AddProductRequest,
    ListProductsRequest,
    ProductFilters,
    RecognizeProductResponse,
)
from app.services.image_service import ImageService
from app.services.product_service import ProductService

product_router = APIRouter()

image_service = ImageService()
product_service = ProductService(image_service=image_service)


@product_router.post(
    "/product/recognize",
    response_model=RecognizeProductResponse,
    status_code=status.HTTP_200_OK,
)
async def recognize(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    file: UploadFile = File(...),
):
    return await product_service.recognize_product(file, db)


@product_router.post("/product")
def add_product(
    product: AddProductRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    return ProductService.add_product(product, db)


@product_router.get("/product/{product_id}")
def get_product(
    product_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    params = ListProductsRequest(filters=ProductFilters(id=product_id))
    return ProductService.list_products(params, db)


@product_router.post("/products")
def list_products(
    params: ListProductsRequest | None = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    return ProductService.list_products(params, db)
