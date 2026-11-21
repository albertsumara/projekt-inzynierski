from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.recipe import ListRecipesRequest, ListRecipesResponse
from app.services.interfaces.recipe_service_interface import (
    RecipeServiceInterface,
)
from app.services.recipe_service import RecipeService


class RecipeRouter:
    def __init__(self, service: RecipeServiceInterface | None = None):
        self.service = service if service is not None else RecipeService()
        self.router = APIRouter()

        self.router.post("/recipe", response_model=ListRecipesResponse)(
            self.list_recipes
        )

    def list_recipes(
        self,
        params: ListRecipesRequest | None = None,
        db: Annotated[Session, Depends(get_db)] = None,
    ):
        if params is None:
            params = ListRecipesRequest()

        return self.service.list_recipes(params, db)

    def get_router(self) -> APIRouter:
        return self.router
