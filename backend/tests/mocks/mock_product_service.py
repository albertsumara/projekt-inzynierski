from app.schemas.product import (
    AddProductRequest,
    ListProductsRequest,
    RecognizeProductResponse,
)
from app.services.interfaces.product_service_interface import ProductServiceInterface
from tests.mocks.mock_data import MOCK_ADD_PRODUCT_RESPONSE
from fastapi import UploadFile
from sqlalchemy.orm import Session


class MockProductService(ProductServiceInterface):
    def __init__(
        self,
        *,
        recognize_response: RecognizeProductResponse | None = None,
        add_response: object | None = None,
        product_by_id: object | None = None,
        products: object | None = None,
        recognize_error: Exception | None = None,
        add_error: Exception | None = None,
        get_error: Exception | None = None,
        list_error: Exception | None = None,
    ) -> None:
        self.recognize_response = recognize_response or RecognizeProductResponse(
            filename="uploaded-image",
            recognitions=[],
        )
        self.add_response = add_response or MOCK_ADD_PRODUCT_RESPONSE
        self.product_by_id = product_by_id
        self.products = products if products is not None else []
        self.recognize_error = recognize_error
        self.add_error = add_error
        self.get_error = get_error
        self.list_error = list_error
        self.recognize_calls: list[tuple[bytes, str | None, object]] = []
        self.add_calls: list[tuple[AddProductRequest, object]] = []
        self.get_by_id_calls: list[tuple[int, object]] = []
        self.list_calls: list[tuple[ListProductsRequest, object]] = []

    async def recognize_product(
        self,
        file: UploadFile,
        db: Session,
    ) -> RecognizeProductResponse:
        image_bytes = await file.read()
        self.recognize_calls.append((image_bytes, file.content_type, db))
        await file.close()
        if self.recognize_error is not None:
            raise self.recognize_error
        return self.recognize_response

    def add_product(
        self,
        product: AddProductRequest,
        db: Session,
    ):
        self.add_calls.append((product, db))
        if self.add_error is not None:
            raise self.add_error
        return self.add_response

    def get_product_by_id_ml(
        self,
        id_ml: int,
        db: Session,
    ):
        self.get_by_id_calls.append((id_ml, db))
        if self.get_error is not None:
            raise self.get_error
        return self.product_by_id

    def list_products(
        self,
        params: ListProductsRequest,
        db: Session,
    ):
        self.list_calls.append((params, db))
        if self.list_error is not None:
            raise self.list_error
        return self.products
