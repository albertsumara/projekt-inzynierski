from app.schemas.recipe import ListRecipesRequest, ListRecipesResponse
from app.services.interfaces.recipe_service_interface import RecipeServiceInterface
from sqlalchemy.orm import Session


class MockRecipeService(RecipeServiceInterface):
    def __init__(
        self,
        response: ListRecipesResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response or ListRecipesResponse(recipes=[])
        self.error = error
        self.calls: list[tuple[ListRecipesRequest, object]] = []

    def list_recipes(
        self,
        params: ListRecipesRequest,
        db: Session,
    ) -> ListRecipesResponse:
        self.calls.append((params, db))
        if self.error is not None:
            raise self.error
        return self.response
