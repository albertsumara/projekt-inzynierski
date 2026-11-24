from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session

from app.db.queries.user_queries import get_users_product_by_id, list_users_products
from app.errors.product_errors import ProductNotFoundError
from app.errors.user_errors import (
    UserDbError,
    UsersProductNotFoundError,
    UserNotFoundError,
)
from app.mappers import UserMapper
from app.schemas.user import (
    AddProductToUserRequest,
    ListUsersProductsRequest,
    ListUsersProductsResponse,
)
from app.services.interfaces.user_service_interface import UserServiceInterface
from app.utils.database import raise_for_constraint


class UserService(UserServiceInterface):
    @staticmethod
    def list_users_products(
        params: ListUsersProductsRequest,
        db: Session,
    ) -> ListUsersProductsResponse:
        rows = list_users_products(db, params)
        return UserMapper.to_list_users_products_response(rows)

    @staticmethod
    def add_users_product(request: AddProductToUserRequest, db: Session):

        new_product_to_user = UserMapper.to_add_users_product(request)
        try:
            db.add(new_product_to_user)
            db.commit()
            db.refresh(new_product_to_user)
            return new_product_to_user
        except SQLAlchemyIntegrityError as e:
            db.rollback()
            raise_for_constraint(
                e,
                {"users_products_id_user_fkey": UserNotFoundError},
            )
            raise_for_constraint(
                e,
                {"users_products_id_product_fkey": ProductNotFoundError},
            )
            raise UserDbError("Database error.") from e

    @staticmethod
    def remove_users_product(users_product_id: int, db: Session):
        users_product = get_users_product_by_id(db, users_product_id)
        if users_product is None:
            raise UsersProductNotFoundError("User product not found.")

        db.delete(users_product)
        db.commit()
