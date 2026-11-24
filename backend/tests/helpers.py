import io

from app.db.models.product_db import MeasurementType
from app.schemas.ingredients import Ingredients
from app.schemas.product import AddProductRequest, Product
from models.image_classifier import ImageClassifier
from PIL import Image


class DeterministicImageClassifier(ImageClassifier):
    def recognize(self, image: Image.Image) -> list[dict[str, int | float]]:
        return [{"id_ml": 7, "confidence": 0.95}]


def create_image_bytes(
    image_format: str = "JPEG",
    size: tuple[int, int] = (100, 100),
) -> bytes:
    image = Image.new("RGB", size, color="red")
    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


def add_product_payload() -> dict[str, object]:
    return AddProductRequest(
        product=Product(
            id_ml=12,
            name="Banana",
            measurement_type=MeasurementType.WEIGHT,
            ingredients=Ingredients(
                calories=89,
                protein=1.1,
                fat=0.3,
                carbs=22.8,
                average_size=120,
                shelf_life=7,
            ),
        )
    ).model_dump(mode="json")
