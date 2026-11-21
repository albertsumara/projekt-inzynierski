from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from .base_db import Base


class RecipesProductsDb(Base):
    __tablename__ = "recipes_products"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(
        Integer,
        ForeignKey("recipes.id"),
        nullable=False,
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )
    quantity_measurement = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1, server_default="1")

    recipe = relationship(
        "RecipeDb",
        back_populates="recipes_products",
    )

    product = relationship(
        "ProductDb",
        back_populates="recipes_products",
    )
