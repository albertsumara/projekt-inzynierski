from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_db import Base


class RecipeDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RecipeDb(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    time: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[RecipeDifficulty] = mapped_column(
        SqlEnum(RecipeDifficulty, name="recipe_difficulty"),
        nullable=False,
    )
    is_vegetarian: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_gluten_free: Mapped[bool] = mapped_column(Boolean, nullable=False)
    instruction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    recipes_products: Mapped[List["RecipesProductsDb"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )


from .recipes_products_db import RecipesProductsDb
