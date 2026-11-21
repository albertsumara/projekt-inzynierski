from sqlalchemy.orm import Session

from .products_seed import seed_products
from .recipes_seed import seed_recipes
from .users_seed import seed_users


def seed_data(db: Session) -> None:
    seed_products(db)
    seed_recipes(db)
    seed_users(db)
