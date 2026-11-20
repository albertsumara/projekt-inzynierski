from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session

from app.errors.product_errors import ProductNotFoundError
from app.errors.user_errors import UserDbError, UserNotFoundError
from app.mappers import UserMapper
from app.schemas.user import AddProductToUserRequest
from app.utils.database import raise_for_constraint


class UserService:
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
