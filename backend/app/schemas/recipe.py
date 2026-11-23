from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.filter import NumberFilter
from app.schemas.sort import SortOrder


class RecipeDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RecipesProduct(BaseModel):
    product_id: int
    product_name: str
    quantity_measurement: float
    quantity: int
    measurement: str


class Recipe(BaseModel):
    id: int
    name: str
    time: int
    difficulty: RecipeDifficulty
    recipes_products: list[RecipesProduct]
    is_vegetarian: bool
    is_gluten_free: bool
    instruction: str | None


class RecipeSeedProduct(BaseModel):
    id_ml: int
    quantity_measurement: float | None = Field(default=None, gt=0)
    quantity: int = Field(default=1, gt=0)


class RecipeSeed(BaseModel):
    name: str = Field(min_length=1)
    time: int = Field(gt=0)
    difficulty: RecipeDifficulty
    is_vegetarian: bool
    is_gluten_free: bool
    instruction: str
    ingredients: list[RecipeSeedProduct] = Field(min_length=1)


class RecipeNutrition(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float


class RecipeResponse(BaseModel):
    recipe: Recipe
    recipe_nutrition: RecipeNutrition


class RecipeSortField(str, Enum):
    NAME = "name"
    TIME = "time"
    DIFFICULTY = "difficulty"
    PRODUCTS_COUNT = "products_count"
    CALORIES = "calories"
    PROTEIN = "protein"
    CARBS = "carbs"
    FAT = "fat"
    TOTAL_WEIGHT = "total_weight"


class RecipeSort(BaseModel):
    field: RecipeSortField
    order: SortOrder = SortOrder.ASC


class RecipeFilters(BaseModel):
    id: int | None = None
    name: str | None = None
    time: NumberFilter | None = None
    difficulty: list[RecipeDifficulty] | None = None
    is_vegetarian: bool | None = None
    is_gluten_free: bool | None = None
    products_count: NumberFilter | None = None
    product_ids: list[int] | None = None
    match_all_products: bool = False
    calories: NumberFilter | None = None
    protein: NumberFilter | None = None
    fat: NumberFilter | None = None
    carbs: NumberFilter | None = None


class ListRecipesRequest(BaseModel):
    filters: RecipeFilters | None = None
    sort: RecipeSort | None = None


class ListRecipesResponse(BaseModel):
    recipes: list[RecipeResponse]
