from enum import Enum

from pydantic import BaseModel, Field

from app.schemas import FilterOperator, SortOrder
from app.schemas.ingredients import Ingredients


class Recognition(BaseModel):
    id_ml: int
    confidence: float = Field(ge=0.0, le=1.0)


class RecognizedProduct(BaseModel):
    id: int
    name: str
    confidence: float = Field(ge=0.0, le=1.0)


class RecognizeProductResponse(BaseModel):
    filename: str
    recognitions: list[RecognizedProduct]


class Product(BaseModel):
    id_ml: int
    name: str
    ingredients: Ingredients


class AddProductRequest(BaseModel):
    product: Product


class ProductSortField(str, Enum):
    SHELF_LIFE = "shelf_life"
    CALORIES = "calories"
    PROTEIN = "protein"
    CARBS = "carbs"
    FAT = "fat"
    NAME = "name"


class ProductSort(BaseModel):
    field: ProductSortField
    order: SortOrder = SortOrder.ASC


class NumberFilter(BaseModel):
    operator: FilterOperator
    value: float


class ProductFilters(BaseModel):
    id: int | None = None
    id_ml: int | None = None
    calories: NumberFilter | None = None
    protein: NumberFilter | None = None
    carbs: NumberFilter | None = None
    fat: NumberFilter | None = None
    average_size: NumberFilter | None = None
    shelf_life: NumberFilter | None = None


class ListProductsRequest(BaseModel):
    filters: ProductFilters | None = None
    sort: ProductSort | None = None
