from abc import ABC, abstractmethod

from app.schemas.recipe import ListRecipesRequest, ListRecipesResponse
from sqlalchemy.orm import Session


class RecipeServiceInterface(ABC):
    @abstractmethod
    def list_recipes(
        self,
        params: ListRecipesRequest,
        db: Session,
    ) -> ListRecipesResponse:
        pass
