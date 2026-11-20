from app.db.models import UserDb, UsersProductsDb
from app.schemas.user import AddProductToUserRequest


class UserMapper:
    @staticmethod
    def to_create_user(data):
        return UserDb(name=data.name)

    @staticmethod
    def to_add_product_to_user(request: AddProductToUserRequest):
        return UsersProductsDb(
            user_id=request.user_id,
            product_id=request.product_id,
        )
