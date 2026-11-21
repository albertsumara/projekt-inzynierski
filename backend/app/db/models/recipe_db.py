from enum import Enum

from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import relationship

from .base_db import Base


class RecipeDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RecipeDb(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    time = Column(Integer, nullable=False)
    difficulty = Column(
        SqlEnum(RecipeDifficulty, name="recipe_difficulty"),
        nullable=False,
    )
    is_vegetarian = Column(Boolean, nullable=False)
    is_gluten_free = Column(Boolean, nullable=False)
    instruction = Column(Text, nullable=True)

    recipes_products = relationship(
        "RecipesProductsDb",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
