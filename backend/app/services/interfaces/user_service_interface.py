from abc import ABC, abstractmethod

from app.schemas.user import (
    AddProductToUserRequest,
    ListUsersProductsRequest,
    ListUsersProductsResponse,
)
from sqlalchemy.orm import Session


class UserServiceInterface(ABC):
    @abstractmethod
    def list_users_products(
        self,
        params: ListUsersProductsRequest,
        db: Session,
    ) -> ListUsersProductsResponse:
        pass

    @abstractmethod
    def add_product_to_user(
        self,
        request: AddProductToUserRequest,
        db: Session,
    ):
        pass
