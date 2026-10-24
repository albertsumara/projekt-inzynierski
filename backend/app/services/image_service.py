
from io import BytesIO

from PIL import Image, UnidentifiedImageError


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
            raise InvalidImageError("Image file is required.")

        if len(image_bytes) > MAX_IMAGE_SIZE:
            raise InvalidImageError(
                "Image exceeding 8 MB limit."
            )

        if content_type not in ALLOWED_CONTENT_TYPES:
            raise InvalidImageError(
                "Dozwolone formaty: JPEG, PNG i WEBP."
            )

        try:
            with Image.open(BytesIO(image_bytes)) as image:
                if image.format not in ALLOWED_FORMATS:
                    raise InvalidImageError(
                        "Invalid image format."
                    )

                image.load()
                return image.convert("RGB")

        except (UnidentifiedImageError, OSError) as exc:
            raise InvalidImageError(
                "Unknown error."
            ) from exc
