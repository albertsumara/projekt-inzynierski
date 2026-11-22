from sqlalchemy import func
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session

from app.db.models.ingredients_db import IngredientsDb
from app.db.models.product_db import ProductDb
from app.db.models.users_products_db import UsersProductsDb
from app.errors.product_errors import ProductNotFoundError
from app.errors.user_errors import UserDbError, UserNotFoundError
from app.mappers import UserMapper
from app.schemas.sort import SortOrder
from app.schemas.user import (
    AddProductToUserRequest,
    ListUsersProductsRequest,
    ListUsersProductsResponse,
    UsersProductAggregateField,
    UsersProductsSortField,
)
from app.services.interfaces.user_service_interface import UserServiceInterface
from app.utils.database import raise_for_constraint
from app.utils.filters import apply_number_filter

SECONDS_PER_DAY = 24 * 60 * 60


class UserService(UserServiceInterface):
    @staticmethod
    def list_users_products(
        params: ListUsersProductsRequest,
        db: Session,
    ) -> ListUsersProductsResponse:
        quantity_measurement = func.coalesce(
            UsersProductsDb.quantity_measurement,
            IngredientsDb.average_size,
            0,
        )
        quantity = func.coalesce(UsersProductsDb.quantity, 1)
        total_measurement = quantity_measurement * quantity

        shelf_life_left = func.greatest(
            IngredientsDb.shelf_life
            - func.floor(
                func.extract(
                    "epoch",
                    func.now() - UsersProductsDb.created_at,
                )
                / SECONDS_PER_DAY
            ),
            0,
        )

        nutrition_columns = {
            UsersProductAggregateField.CALORIES.value: func.coalesce(
                IngredientsDb.calories, 0
            )
            * total_measurement
            / 100,
            UsersProductAggregateField.PROTEIN.value: func.coalesce(
                IngredientsDb.protein, 0
            )
            * total_measurement
            / 100,
            UsersProductAggregateField.CARBS.value: func.coalesce(
                IngredientsDb.carbs, 0
            )
            * total_measurement
            / 100,
            UsersProductAggregateField.FAT.value: func.coalesce(IngredientsDb.fat, 0)
            * total_measurement
            / 100,
        }

        query = (
            db.query(
                UsersProductsDb,
                shelf_life_left.label(UsersProductAggregateField.SHELF_LIFE_LEFT.value),
                quantity.label(UsersProductAggregateField.QUANTITY.value),
                quantity_measurement.label(
                    UsersProductAggregateField.QUANTITY_MEASUREMENT.value
                ),
                total_measurement.label(
                    UsersProductAggregateField.TOTAL_MEASUREMENT.value
                ),
                *(column.label(field) for field, column in nutrition_columns.items()),
            )
            .join(ProductDb, ProductDb.id == UsersProductsDb.product_id)
            .outerjoin(IngredientsDb, IngredientsDb.product_id == ProductDb.id)
        )

        if params and params.filters:
            filters = params.filters

            if filters.id is not None:
                query = query.filter(UsersProductsDb.id == filters.id)

            if filters.name is not None:
                query = query.filter(
                    ProductDb.name.icontains(filters.name, autoescape=True)
                )

            if filters.shelf_life_left is not None:
                query = apply_number_filter(
                    query,
                    shelf_life_left,
                    filters.shelf_life_left,
                )

            if filters.quantity is not None:
                query = apply_number_filter(query, quantity, filters.quantity)

            for field, column in nutrition_columns.items():
                number_filter = getattr(filters, field)
                if number_filter is not None:
                    query = apply_number_filter(query, column, number_filter)

        if params and params.sort:
            sort_columns = {
                UsersProductsSortField.SHELF_LIFE_LEFT: shelf_life_left,
                UsersProductsSortField.CREATED_AT: UsersProductsDb.created_at,
                UsersProductsSortField.QUANTITY: quantity,
                UsersProductsSortField.QUANTITY_MEASUREMENT: quantity_measurement,
                UsersProductsSortField.TOTAL_MEASUREMENT: total_measurement,
                UsersProductsSortField.CALORIES: nutrition_columns[
                    UsersProductAggregateField.CALORIES.value
                ],
                UsersProductsSortField.PROTEIN: nutrition_columns[
                    UsersProductAggregateField.PROTEIN.value
                ],
                UsersProductsSortField.CARBS: nutrition_columns[
                    UsersProductAggregateField.CARBS.value
                ],
                UsersProductsSortField.FAT: nutrition_columns[
                    UsersProductAggregateField.FAT.value
                ],
            }

            column = sort_columns[params.sort.field]
            if params.sort.order == SortOrder.ASC:
                query = query.order_by(column.asc(), UsersProductsDb.id.asc())
            else:
                query = query.order_by(column.desc(), UsersProductsDb.id.asc())

        return UserMapper.to_list_users_products_response(query.all())

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
                {"users_products_user_id_fkey": UserNotFoundError},
            )
            raise_for_constraint(
                e,
                {"users_products_product_id_fkey": ProductNotFoundError},
            )
            raise UserDbError("Database error.") from e

    @staticmethod
    def remove_users_product(users_product_id: int, db: Session):
        users_product = (
            db.query(UsersProductsDb)
            .filter(UsersProductsDb.id == users_product_id)
            .first()
        )
        if users_product is None:
            raise UserNotFoundError("User product not found.")

        db.delete(users_product)
        db.commit()
