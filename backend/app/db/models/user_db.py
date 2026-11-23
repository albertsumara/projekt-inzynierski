from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_db import Base


class UserDb(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    users_products: Mapped[List["UsersProductsDb"]] = relationship(
        back_populates="user"
    )


from .users_products_db import UsersProductsDb
