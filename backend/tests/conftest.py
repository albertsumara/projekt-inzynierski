import os
import shutil
import subprocess
import uuid
from enum import Enum

import pytest
from app.api.routes.product_router import ProductRouter
from app.api.routes.recipe_router import RecipeRouter
from app.api.routes.user_router import UserRouter
from app.db.database import get_db
from app.db.models import Base
from app.db.models.ingredients_db import IngredientsDb
from app.db.models.product_db import MeasurementType, ProductDb
from app.db.models.recipe_db import (
    RecipeDb,
)
from app.db.models.recipe_db import (
    RecipeDifficulty as DbRecipeDifficulty,
)
from app.db.models.recipes_products_db import RecipesProductsDb
from app.db.models.user_db import UserDb
from app.services.image_service import ImageService
from app.services.product_service import ProductService
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from paths import BASE_DIR, DOCKER_COMPOSE_TEST_PATH, ENV_TEST_CONFIGURATION_PATH
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from tests.helpers import DeterministicImageClassifier


class TestDatabaseSetting(str, Enum):
    HOST = "TEST_DB_HOST"
    PORT = "TEST_DB_PORT"
    NAME = "TEST_DB_NAME"
    USER = "TEST_DB_USER"
    PASSWORD = "TEST_DB_PASSWORD"


@pytest.fixture(scope="session")
def integration_engine():
    env_file = ENV_TEST_CONFIGURATION_PATH
    compose_file = DOCKER_COMPOSE_TEST_PATH
    if not env_file.is_file():
        pytest.fail(f"Test environment file not found: {env_file}")
    load_dotenv(env_file, override=True)

    database_settings = {
        setting: os.getenv(setting.value) for setting in TestDatabaseSetting
    }
    missing_settings = [
        setting.value for setting, value in database_settings.items() if not value
    ]
    if missing_settings:
        pytest.fail(
            f"Missing test database settings in {env_file}: "
            f"{', '.join(missing_settings)}"
        )

    database_host = database_settings[TestDatabaseSetting.HOST]
    database_name = database_settings[TestDatabaseSetting.NAME]
    if database_host not in {
        "localhost",
        "127.0.0.1",
        "::1",
    } or not (database_name and database_name.endswith("_test")):
        pytest.fail(
            "The test database must use a local host and a database name "
            "ending in '_test'."
        )
    try:
        database_port = int(database_settings[TestDatabaseSetting.PORT] or "")
    except ValueError:
        pytest.fail(f"{TestDatabaseSetting.PORT} in .env.test must be an integer.")
    if not 1 <= database_port <= 65535:
        pytest.fail(
            f"{TestDatabaseSetting.PORT} in .env.test must be between 1 and 65535."
        )

    project_name = f"projekt-tests-{uuid.uuid4().hex[:8]}"
    if shutil.which("docker") is None:
        pytest.fail(
            "Docker CLI was not found on PATH. Install Docker Desktop or add "
            "the directory containing docker.exe to PATH.",
            pytrace=False,
        )

    compose_command = [
        "docker",
        "compose",
        "--project-name",
        project_name,
        "--env-file",
        str(env_file),
        "--file",
        str(compose_file),
    ]

    def run_compose(*arguments):
        return subprocess.run(
            compose_command + list(arguments),
            cwd=BASE_DIR,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )

    startup = run_compose("up", "--detach", "--wait")
    if startup.returncode != 0:
        run_compose("down", "--volumes", "--remove-orphans")
        pytest.fail(
            "Could not start the PostgreSQL test container. "
            "Make sure Docker Desktop is running.\n"
            f"{startup.stderr.strip()}"
        )

    database_url = URL.create(
        "postgresql+psycopg",
        username=database_settings[TestDatabaseSetting.USER],
        password=database_settings[TestDatabaseSetting.PASSWORD],
        host=database_host,
        port=database_port,
        database=database_name,
    )
    engine = None
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.begin() as connection:
            Base.metadata.drop_all(bind=connection)
            Base.metadata.create_all(bind=connection)
        yield engine
    finally:
        try:
            if engine is not None:
                try:
                    with engine.begin() as connection:
                        Base.metadata.drop_all(bind=connection)
                finally:
                    engine.dispose()
        finally:
            shutdown = run_compose("down", "--volumes", "--remove-orphans")
            if shutdown.returncode != 0:
                pytest.fail(
                    "Could not remove the PostgreSQL test container.\n"
                    f"{shutdown.stderr.strip()}"
                )


@pytest.fixture
def db_connection(integration_engine):
    connection = integration_engine.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture
def db_session(db_connection):
    test_session = sessionmaker(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    session = test_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def api_client(db_connection):
    test_session = sessionmaker(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    def override_get_db():
        session: Session = test_session()
        try:
            yield session
        finally:
            session.close()

    app = FastAPI()
    app.include_router(
        ProductRouter(
            ProductService(ImageService(DeterministicImageClassifier()))
        ).get_router(),
        prefix="/api/v1",
    )
    app.include_router(RecipeRouter().get_router(), prefix="/api/v1")
    app.include_router(UserRouter().get_router(), prefix="/api/v1")
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def seeded_product(db_session):
    product = ProductDb(
        id_ml=7,
        name="Apple",
        measurement_type=MeasurementType.WEIGHT,
        ingredients=IngredientsDb(
            calories=89,
            protein=1.1,
            fat=0.3,
            carbs=22.8,
            average_size=120,
            shelf_life=7,
        ),
    )
    db_session.add(product)
    db_session.commit()
    return product


@pytest.fixture
def seeded_products(db_session, seeded_product):
    second_product = ProductDb(
        id_ml=8,
        name="Pear",
        measurement_type=MeasurementType.WEIGHT,
        ingredients=IngredientsDb(
            calories=57,
            protein=0.4,
            fat=0.1,
            carbs=15.2,
            average_size=130,
            shelf_life=5,
        ),
    )
    db_session.add(second_product)
    db_session.commit()
    return seeded_product


@pytest.fixture
def seeded_user(db_session):
    user = UserDb(name="Test user")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def seeded_recipe(db_session, seeded_product):
    recipe = RecipeDb(
        name="Fruit salad",
        time=10,
        difficulty=DbRecipeDifficulty.EASY,
        is_vegetarian=True,
        is_gluten_free=True,
        instruction="Mix.",
        recipes_products=[
            RecipesProductsDb(
                product=seeded_product,
                quantity_measurement=100,
                quantity=2,
            )
        ],
    )
    db_session.add(recipe)
    db_session.commit()
    return recipe
