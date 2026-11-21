from app.db.models import IngredientsDb, ProductDb
from app.schemas.ingredients import Ingredients
from app.schemas.product import (
    AddProductRequest,
    RecognizedProduct,
    RecognizeProductResponse,
)


class ProductMapper:
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
    def to_ingredients(data: Ingredients):
        return IngredientsDb(
            calories=round(data.calories, 2),
            protein=round(data.protein, 2),
            carbs=round(data.carbs, 2),
            fat=round(data.fat, 2),
            average_size=round(data.average_size, 2),
            shelf_life=data.shelf_life,
        )

    @staticmethod
    def to_product(data: AddProductRequest):
        return ProductDb(
            id_ml=data.product.id_ml,
            name=data.product.name,
            measurement_type=data.product.measurement_type,
            ingredients=ProductMapper.to_ingredients(data.product.ingredients),
        )
