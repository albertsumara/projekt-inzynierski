from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes import ProductRouter, RecipeRouter, UserRouter
from app.db.database import SessionLocal, engine, get_db
from app.db.models import Base
from app.db.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Diet App",
    description="Diet application manager",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db", tags=["Health"])
def database_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}


app.include_router(
    ProductRouter().get_router(),
    prefix="/api/v1",
    tags=["Products"],
)

app.include_router(
    UserRouter().get_router(),
    prefix="/api/v1",
    tags=["Users"],
)

app.include_router(
    RecipeRouter().get_router(),
    prefix="/api/v1",
    tags=["Recipes"],
)
