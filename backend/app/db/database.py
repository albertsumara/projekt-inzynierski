import os

from dotenv import load_dotenv
from paths import ENV_CONFIGURATION_PATH
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(ENV_CONFIGURATION_PATH)

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_ADDRESS')}"
    f"{os.getenv('DB_NAME')}"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
