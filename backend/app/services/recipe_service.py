from sqlalchemy.orm import Session

from app.db.queries.recipe_queries import list_recipes as query_recipes
from app.mappers import RecipeMapper
from app.schemas.recipe import ListRecipesRequest, ListRecipesResponse
from app.services.interfaces.recipe_service_interface import (
    RecipeServiceInterface,
)


class RecipeService(RecipeServiceInterface):
    @staticmethod
    def list_recipes(params: ListRecipesRequest, db: Session) -> ListRecipesResponse:
        return RecipeMapper.to_list_recipes_response(query_recipes(db, params))
