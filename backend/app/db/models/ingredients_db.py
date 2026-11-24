from sqlalchemy import Double, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_db import Base


class IngredientsDb(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), unique=True, nullable=False
    )
    calories: Mapped[float] = mapped_column(Double, nullable=False)
    protein: Mapped[float] = mapped_column(Double, nullable=False)
    carbs: Mapped[float] = mapped_column(Double, nullable=False)
    fat: Mapped[float] = mapped_column(Double, nullable=False)
    average_size: Mapped[float] = mapped_column(Double, nullable=False)
    shelf_life: Mapped[int] = mapped_column(Integer, nullable=False)

    product: Mapped["ProductDb"] = relationship(back_populates="ingredients")


from .product_db import ProductDb
