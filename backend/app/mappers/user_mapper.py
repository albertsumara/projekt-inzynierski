from app.db.models import UserDb, UsersProductsDb
from app.schemas.user import (
    AddProductToUserRequest,
    ListUsersProductsResponse,
    UsersProduct,
    UsersProductAggregateField,
)


class UserMapper:
    @staticmethod
    def to_create_user(data):
        return UserDb(name=data.name)

    @staticmethod
    def to_add_product_to_user(request: AddProductToUserRequest):
        return UsersProductsDb(
            user_id=request.user_id,
            product_id=request.product_id,
            quantity=request.quantity,
            quantity_measurement=request.quantity_measurement,
        )

    @staticmethod
    def to_list_users_products_response(data) -> ListUsersProductsResponse:
        users_products = [
            UsersProduct(
                id=row[0].id,
                product_id=row[0].product_id,
                shelf_life_left=row._mapping[
                    UsersProductAggregateField.SHELF_LIFE_LEFT.value
                ],
                quantity=row._mapping[UsersProductAggregateField.QUANTITY.value],
                quantity_measurement=round(
                    float(
                        row._mapping[
                            UsersProductAggregateField.QUANTITY_MEASUREMENT.value
                        ]
                    ),
                    2,
                ),
                total_measurement=round(
                    float(
                        row._mapping[UsersProductAggregateField.TOTAL_MEASUREMENT.value]
                    ),
                    2,
                ),
            )
            for row in data
        ]
        return ListUsersProductsResponse(users_products=users_products)
