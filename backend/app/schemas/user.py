from pydantic import BaseModel


class AddProductToUserRequest(BaseModel):
    user_id: int
    product_id: int


class User(BaseModel):
    name: str
