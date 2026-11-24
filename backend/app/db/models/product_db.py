from enum import Enum
from typing import List

from sqlalchemy import Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_db import Base


class MeasurementType(str, Enum):
    COUNTABLE = "countable"
    WEIGHT = "weight"
    VOLUME = "volume"


class ProductDb(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_ml: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    measurement_type: Mapped[MeasurementType] = mapped_column(
        SqlEnum(MeasurementType, name="measurement_type"),
        nullable=False,
        default=MeasurementType.WEIGHT,
    )
    ingredients: Mapped["IngredientsDb"] = relationship(
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )

    users_products: Mapped[List["UsersProductsDb"]] = relationship(
        back_populates="product"
    )

    recipes_products: Mapped[List["RecipesProductsDb"]] = relationship(
        back_populates="product"
    )


from .ingredients_db import IngredientsDb
from .recipes_products_db import RecipesProductsDb
from .users_products_db import UsersProductsDb
