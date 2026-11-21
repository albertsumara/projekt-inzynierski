from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base_db import Base


class UserDb(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    users_products = relationship(
        "UsersProductsDb",
        back_populates="user",
    )
