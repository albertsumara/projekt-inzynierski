from pydantic import BaseModel


class Ingredients(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    average_size: float
    shelf_life: int
