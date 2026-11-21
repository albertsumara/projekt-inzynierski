from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.schemas.recipe import ListRecipesRequest, ListRecipesResponse


class RecipeServiceInterface(ABC):
    @abstractmethod
    def list_recipes(
        self,
        params: ListRecipesRequest,
        db: Session,
    ) -> ListRecipesResponse:
        pass
