from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from models.image_classifier import ImageClassifier
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.product import (
    AddProductRequest,
    ListProductsRequest,
    ProductFilters,
    RecognitionResponse,
)
from app.services.image_service import ImageService, InvalidImageError
from app.services.product_service import ProductService

product_router = APIRouter()

image_service = ImageService()
image_classifier = ImageClassifier()

product_service = ProductService(
    image_service=image_service,
    image_classifier=image_classifier,
)


@product_router.post(
    "/product/recognize",
    response_model=RecognitionResponse,
    status_code=status.HTTP_200_OK,
)
async def recognize(
    file: UploadFile = File(...),
) -> RecognitionResponse:
    image_bytes = await file.read()

    try:
        recognitions = product_service.recognize_product(
            image_bytes=image_bytes,
            content_type=file.content_type,
        )
    except InvalidImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await file.close()

    return RecognitionResponse(
        filename=file.filename or "uploaded-image",
        recognitions=recognitions,
    )


@product_router.post("/product")
def add_product(product: AddProductRequest, db: Annotated[Session, Depends(get_db)]):
    return ProductService.add_product(product, db)


@product_router.get("/product/{product_id}")
def get_product(product_id: int, db: Annotated[Session, Depends(get_db)]):
    params = ListProductsRequest(filters=ProductFilters(id=product_id))
    return ProductService.list_products(params, db)


@product_router.post("/products")
def list_products(
    params: ListProductsRequest | None = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    return ProductService.list_products(params, db)
