from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.filter import NumberFilter
from app.schemas.sort import SortOrder


class AddProductToUserRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(default=1, gt=0)
    quantity_measurement: float | None = Field(default=None, gt=0)


class User(BaseModel):
    name: str


class UsersProductSeed(BaseModel):
    user_name: str
    id_ml: int
    quantity: int = Field(default=1, gt=0)
    quantity_measurement: float | None = Field(default=None, gt=0)


class UsersProductsSortField(str, Enum):
    SHELF_LIFE_LEFT = "shelf_life_left"
    CREATED_AT = "created_at"
    QUANTITY = "quantity"
    QUANTITY_MEASUREMENT = "quantity_measurement"
    TOTAL_MEASUREMENT = "total_measurement"
    CALORIES = "calories"
    PROTEIN = "protein"
    CARBS = "carbs"
    FAT = "fat"


class UsersProductSort(BaseModel):
    field: UsersProductsSortField
    order: SortOrder = SortOrder.ASC


class UsersProductsFilters(BaseModel):
    id: int | None = None
    name: str | None = None
    shelf_life_left: NumberFilter | None = None
    quantity: NumberFilter | None = None
    calories: NumberFilter | None = None
    protein: NumberFilter | None = None
    fat: NumberFilter | None = None
    carbs: NumberFilter | None = None


class UsersProduct(BaseModel):
    id: int
    product_id: int
    shelf_life_left: int
    quantity: int
    quantity_measurement: float
    total_measurement: float


class UsersProductAggregateField(str, Enum):
    ID = "id"
    PRODUCT_ID = "product_id"
    SHELF_LIFE_LEFT = "shelf_life_left"
    CREATED_AT = "created_at"
    QUANTITY = "quantity"
    QUANTITY_MEASUREMENT = "quantity_measurement"
    TOTAL_MEASUREMENT = "total_measurement"
    CALORIES = "calories"
    PROTEIN = "protein"
    CARBS = "carbs"
    FAT = "fat"


class ListUsersProductsRequest(BaseModel):
    filters: UsersProductsFilters | None = None
    sort: UsersProductSort | None = None


class ListUsersProductsResponse(BaseModel):
    users_products: list[UsersProduct]
