from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_db import Base


class RecipesProductsDb(Base):
    __tablename__ = "recipes_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recipes.id"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )
    quantity_measurement: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )

    recipe: Mapped["RecipeDb"] = relationship(back_populates="recipes_products")

    product: Mapped["ProductDb"] = relationship(back_populates="recipes_products")


from .product_db import ProductDb
from .recipe_db import RecipeDb
