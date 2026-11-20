from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class ProductDb(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    id_ml = Column(Integer, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)

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
