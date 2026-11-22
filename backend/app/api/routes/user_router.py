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

        self.router.post("/user/product", status_code=201)(self.add_users_product)
        self.router.post(
            "/user/products",
            response_model=ListUsersProductsResponse,
        )(self.list_users_products)
        self.router.delete(
            "/user/product/{users_product_id}",
            status_code=204,
        )(self.remove_users_product)

    def add_users_product(
        self,
        request: AddProductToUserRequest,
        db: Annotated[Session, Depends(get_db)],
    ):
        return self.service.add_users_product(request, db)

    def list_users_products(
        self,
        params: ListUsersProductsRequest | None = None,
        db: Annotated[Session, Depends(get_db)] = None,
    ):
        if params is None:
            params = ListUsersProductsRequest()

        return self.service.list_users_products(params, db)

    def remove_users_product(
        self,
        users_product_id: int,
        db: Annotated[Session, Depends(get_db)],
    ):
        return self.service.remove_users_product(users_product_id, db)

    def get_router(self) -> APIRouter:
        return self.router
