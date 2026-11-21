import json

from paths import USERS_PRODUCTS_SEED_PATH, USERS_SEED_PATH
from sqlalchemy.orm import Session

from app.db.models.product_db import ProductDb
from app.db.models.user_db import UserDb
from app.db.models.users_products_db import UsersProductsDb
from app.mappers.user_mapper import UserMapper
from app.schemas.user import User, UsersProductSeed


def seed_users(db: Session) -> None:
    try:
        seed_users_data = _seed_users(db)
        if seed_users_data:
            db.flush()
        _seed_users_products(db)
        db.commit()
    except Exception:
        db.rollback()
        raise


def _seed_users(db: Session) -> bool:
    with USERS_SEED_PATH.open("r", encoding="utf-8") as file:
        users_data = json.load(file)

    existing_names = {name for (name,) in db.query(UserDb.name).all()}
    added_user = False

    for user_data in users_data:
        user = User.model_validate(user_data)
        if user.name in existing_names:
            continue

        db.add(UserMapper.to_create_user(user))
        existing_names.add(user.name)
        added_user = True

    return added_user


def _seed_users_products(db: Session) -> None:
    with USERS_PRODUCTS_SEED_PATH.open("r", encoding="utf-8") as file:
        users_products_data = json.load(file)

    users_by_name = {
        name: user_id for name, user_id in db.query(UserDb.name, UserDb.id).all()
    }
    existing_ids_ml = {id_ml for (id_ml,) in db.query(ProductDb.id_ml).all()}

    for product_data in users_products_data:
        seed = UsersProductSeed.model_validate(product_data)

        if seed.user_name not in users_by_name:
            raise ValueError(f"Seed user '{seed.user_name}' does not exist")

        if seed.id_ml not in existing_ids_ml:
            raise ValueError(f"Seed product id_ml={seed.id_ml} does not exist")

        product = db.query(ProductDb).filter(ProductDb.id_ml == seed.id_ml).one()
        user_id = users_by_name[seed.user_name]

        already_seeded = (
            db.query(UsersProductsDb)
            .filter(
                UsersProductsDb.user_id == user_id,
                UsersProductsDb.product_id == product.id,
            )
            .first()
        )
        if already_seeded is not None:
            continue

        db.add(
            UsersProductsDb(
                user_id=user_id,
                product_id=product.id,
                quantity=seed.quantity,
                quantity_measurement=seed.quantity_measurement,
            )
        )
