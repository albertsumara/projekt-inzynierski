from io import BytesIO

from models.image_classifier import ImageClassifier
from PIL import Image, UnidentifiedImageError

from app.errors.image_errors import (
    EmptyImageFileError,
    ImageError,
    InvalidImageContentTypeError,
    InvalidImageFormatError,
    InvalidImageSizeError,
)
from app.schemas.product import Recognition
from app.services.interfaces.image_service_interface import ImageServiceInterface

MAX_IMAGE_SIZE = 8 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jfif",
    "image/png",
    "image/webp",
}

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "JFIF"}


class InvalidImageError(ImageError):
    pass


class ImageService(ImageServiceInterface):
    def __init__(self, image_classifier: ImageClassifier | None = None) -> None:
        self.image_classifier = image_classifier or ImageClassifier()

    def recognize(
        self,
        image_bytes: bytes,
        content_type: str | None,
    ) -> list[Recognition]:
        image = self.load_image(image_bytes, content_type)
        return [
            Recognition.model_validate(recognition)
            for recognition in self.image_classifier.recognize(image)
        ]

    def load_image(
        self,
        image_bytes: bytes,
        content_type: str | None,
    ) -> Image.Image:
        if not image_bytes:
            raise EmptyImageFileError("The image file is empty.")

        if len(image_bytes) > MAX_IMAGE_SIZE:
            raise InvalidImageSizeError("The image file cannot be larger than 8 MB.")

        if content_type not in ALLOWED_CONTENT_TYPES:
            raise InvalidImageContentTypeError("This content type is not supported.")

        try:
            with Image.open(BytesIO(image_bytes)) as image:
                if image.format not in ALLOWED_FORMATS:
                    raise InvalidImageFormatError("This image format is not supported.")

                image.load()
                return image.convert("RGB")

        except (UnidentifiedImageError, OSError) as exc:
            raise InvalidImageError("The image file is invalid or corrupted.") from exc
