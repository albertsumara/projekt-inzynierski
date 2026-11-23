from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import (
    AddProductToUserRequest,
    ListUsersProductsRequest,
    ListUsersProductsResponse,
)
from app.services.interfaces.user_service_interface import UserServiceInterface
from app.services.user_service import UserService


class UserRouter:
    def __init__(self, service: UserServiceInterface | None = None):
        self.service = service if service is not None else UserService()
        self.router = APIRouter()

        self.router.post("/user/product", status_code=201)(self.add_product)
        self.router.post(
            "/user/products",
            response_model=ListUsersProductsResponse,
        )(self.list_products)

    def add_product(
        self,
        db: Annotated[Session, Depends(get_db)],
        request: AddProductToUserRequest,
    ):
        return self.service.add_product_to_user(request, db)

    def list_products(
        self,
        db: Annotated[Session, Depends(get_db)],
        params: ListUsersProductsRequest | None = None,
    ):
        if params is None:
            params = ListUsersProductsRequest()

        return self.service.list_users_products(params, db)

    def get_router(self) -> APIRouter:
        return self.router
