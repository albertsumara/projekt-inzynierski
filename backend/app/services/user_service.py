from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session

from app.db.queries.user_queries import list_users_products as query_users_products
from app.errors.product_errors import ProductNotFoundError
from app.errors.user_errors import UserDbError, UserNotFoundError
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
        rows = query_users_products(db, params)
        return UserMapper.to_list_users_products_response(rows)

    @staticmethod
    def add_product_to_user(request: AddProductToUserRequest, db: Session):

        new_product_to_user = UserMapper.to_add_product_to_user(request)
        try:
            db.add(new_product_to_user)
            db.commit()
            db.refresh(new_product_to_user)
            return new_product_to_user
        except SQLAlchemyIntegrityError as e:
            db.rollback()
            raise_for_constraint(
                e,
                {"users_products_user_id_fkey": UserNotFoundError},
            )
            raise_for_constraint(
                e,
                {"users_products_product_id_fkey": ProductNotFoundError},
            )
            raise UserDbError("Database error.") from e
