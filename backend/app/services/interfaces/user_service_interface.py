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
    def add_users_product(
        self,
        request: AddProductToUserRequest,
        db: Session,
    ):
        pass

    @abstractmethod
    def remove_users_product(self, users_product_id: int, db: Session):
        pass
