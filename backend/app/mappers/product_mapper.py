from app.db.models import IngredientsDb, ProductDb
from app.schemas.ingredients import Ingredients
from app.schemas.product import (
    AddProductRequest,
    ListProductsResponse,
    ProductResponse,
    RecognizedProduct,
    RecognizeProductResponse,
    Ingredients as IngredientsResponse,
)


class ProductMapper:
    @staticmethod
    def to_product_response(data: ProductDb) -> ProductResponse:
        return ProductResponse(
            id=data.id,
            id_ml=data.id_ml,
            name=data.name,
            measurement_type=data.measurement_type,
            ingredients=ProductMapper.to_ingredients_response(data.ingredients),
        )

    @staticmethod
    def to_ingredients_response(ingredients: IngredientsDb) -> IngredientsResponse:
        return IngredientsResponse(
            calories=ingredients.calories,
            protein=ingredients.protein,
            carbs=ingredients.carbs,
            fat=ingredients.fat,
            average_size=ingredients.average_size,
            shelf_life=ingredients.shelf_life,
        )

    @staticmethod
    def to_list_products_response(
        products: list[ProductDb],
    ) -> ListProductsResponse:
        return ListProductsResponse(
            products=[
                ProductMapper.to_product_response(product) for product in products
            ]
        )

    @staticmethod
    def to_recognition_response(
        filename: str | None, recognitions: list[RecognizedProduct]
    ):
        return RecognizeProductResponse(
            filename=filename or "uploaded-image",
            recognitions=recognitions,
        )

    @staticmethod
    def to_recognition(
        product: ProductDb,
        confidence: float,
    ) -> RecognizedProduct:
        return RecognizedProduct(
            id=product.id,
            name=product.name,
            confidence=confidence,
        )

    @staticmethod
    def to_ingredients_db(data: Ingredients) -> IngredientsDb:
        return IngredientsDb(
            calories=round(data.calories, 2),
            protein=round(data.protein, 2),
            carbs=round(data.carbs, 2),
            fat=round(data.fat, 2),
            average_size=round(data.average_size, 2),
            shelf_life=data.shelf_life,
        )

    @staticmethod
    def to_product_db(data: AddProductRequest) -> ProductDb:
        return ProductDb(
            id_ml=data.product.id_ml,
            name=data.product.name,
            measurement_type=data.product.measurement_type,
            ingredients=ProductMapper.to_ingredients_db(data.product.ingredients),
        )
