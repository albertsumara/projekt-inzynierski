from enum import Enum

from sqlalchemy import Column, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import relationship

from .base_db import Base


class MeasurementType(str, Enum):
    COUNTABLE = "countable"
    WEIGHT = "weight"
    VOLUME = "volume"


class ProductDb(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    id_ml = Column(Integer, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)
    measurement_type = Column(
        SqlEnum(MeasurementType, name="measurement_type"),
        nullable=False,
        default=MeasurementType.WEIGHT,
    )
    ingredients = relationship(
        "IngredientsDb",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )

    users_products = relationship(
        "UsersProductsDb",
        back_populates="product",
    )

    recipes_products = relationship(
        "RecipesProductsDb",
        back_populates="product",
    )
