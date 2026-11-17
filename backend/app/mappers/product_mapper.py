from app.db.models import IngredientsDb, ProductDb
from app.schemas.product import AddProductRequest


class ProductMapper:
    @staticmethod
    def to_ingredients(data):
        return IngredientsDb(
            calories=data.calories,
            protein=data.protein,
            carbs=data.carbs,
            fat=data.fat,
            average_size=data.average_size,
            shelf_life=data.shelf_life,
        )

    @staticmethod
    def to_product(data: AddProductRequest):
        return ProductDb(
            id_ml=data.product.id_ml,
            name=data.product.name,
            ingredients=ProductMapper.to_ingredients(data.product.ingredients),
        )
