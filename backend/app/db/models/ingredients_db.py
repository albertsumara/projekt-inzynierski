from sqlalchemy import Column, Double, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_db import Base


class IngredientsDb(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    calories = Column(Double, nullable=False)
    protein = Column(Double, nullable=False)
    carbs = Column(Double, nullable=False)
    fat = Column(Double, nullable=False)
    average_size = Column(Double, nullable=False)
    shelf_life = Column(Integer, nullable=False)

    product = relationship("ProductDb", back_populates="ingredients")
