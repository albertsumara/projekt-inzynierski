from app.schemas.user import (
    AddProductToUserRequest,
    ListUsersProductsRequest,
    ListUsersProductsResponse,
)
from app.services.interfaces.user_service_interface import UserServiceInterface
from sqlalchemy.orm import Session
from tests.mocks.mock_data import MOCK_ADD_USER_RESPONSE


class MockUserService(UserServiceInterface):
    def __init__(
        self,
        *,
        list_response: ListUsersProductsResponse | None = None,
        add_response: object | None = None,
        list_error: Exception | None = None,
        add_error: Exception | None = None,
        remove_error: Exception | None = None,
    ) -> None:
        self.list_response = list_response or ListUsersProductsResponse(
            users_products=[]
        )
        self.add_response = add_response or MOCK_ADD_USER_RESPONSE
        self.list_error = list_error
        self.add_error = add_error
        self.remove_error = remove_error
        self.list_calls: list[tuple[ListUsersProductsRequest, object]] = []
        self.add_calls: list[tuple[AddProductToUserRequest, object]] = []
        self.remove_calls: list[tuple[int, object]] = []

    def list_users_products(
        self,
        params: ListUsersProductsRequest,
        db: Session,
    ) -> ListUsersProductsResponse:
        self.list_calls.append((params, db))
        if self.list_error is not None:
            raise self.list_error
        return self.list_response

    def add_users_product(
        self,
        request: AddProductToUserRequest,
        db: Session,
    ):
        self.add_calls.append((request, db))
        if self.add_error is not None:
            raise self.add_error
        return self.add_response

    def remove_users_product(self, users_product_id: int, db: Session):
        self.remove_calls.append((users_product_id, db))
        if self.remove_error is not None:
            raise self.remove_error
