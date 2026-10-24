from app.services.image_service import ImageService
from backend.models.image_classifier import ImageClassifier


class ProductService:
    def __init__(
        self,
        image_service: ImageService,
        image_classifier: ImageClassifier,
    ) -> None:
        self.image_service = image_service
        self.image_classifier = image_classifier

    def predict_product(
        self,
        image_bytes: bytes,
        content_type: str | None,
    ) -> list[dict]:
        image = self.image_service.load_image(
            image_bytes,
            content_type,
        )

        return self.image_classifier.recognize(image)
