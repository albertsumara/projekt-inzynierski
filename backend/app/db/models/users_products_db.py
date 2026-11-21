from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base_db import Base


class UsersProductsDb(Base):
    __tablename__ = "users_products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column("id_user", Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(
        "id_product", Integer, ForeignKey("products.id"), nullable=False
    )
    quantity = Column(Integer, nullable=False, default=1, server_default="1")
    quantity_measurement = Column(Numeric(10, 2), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user = relationship(
        "UserDb",
        back_populates="users_products",
    )

    product = relationship(
        "ProductDb",
        back_populates="users_products",
    )
