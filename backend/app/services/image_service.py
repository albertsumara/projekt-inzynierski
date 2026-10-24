from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app.errors.image_errors import (
    EmptyImageFileError,
    InvalidImageContentTypeError,
    InvalidImageFormatError,
    InvalidImageSizeError,
)

MAX_IMAGE_SIZE = 8 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class InvalidImageError(ValueError):
    pass


class ImageService:
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
