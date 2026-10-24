import io

import pytest
from app.errors.image_errors import (
    EmptyImageFileError,
    InvalidImageContentTypeError,
    InvalidImageFormatError,
    InvalidImageSizeError,
)
from app.services.image_service import MAX_IMAGE_SIZE, ImageService
from PIL import Image


@pytest.fixture
def image_service():
    return ImageService()


def create_image_bytes(image_format="JPEG", size=(100, 100)):
    image = Image.new("RGB", size, color="red")
    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


def test_accepts_valid_jpeg(image_service):
    image_bytes = create_image_bytes("JPEG")

    result = image_service.load_image(image_bytes, "image/jpeg")

    assert result.mode == "RGB"
    assert result.size == (100, 100)


def test_accepts_valid_png(image_service):
    image_bytes = create_image_bytes("PNG")

    result = image_service.load_image(image_bytes, "image/png")

    assert result.mode == "RGB"
    assert result.size == (100, 100)


def test_accepts_valid_webp(image_service):
    image_bytes = create_image_bytes("WEBP")

    result = image_service.load_image(image_bytes, "image/webp")

    assert result.mode == "RGB"
    assert result.size == (100, 100)


def test_rejects_unsupported_content_type(image_service):
    image_bytes = create_image_bytes("JPEG")

    with pytest.raises(InvalidImageContentTypeError):
        image_service.load_image(image_bytes, "image/gif")


def test_rejects_unsupported_image_format(image_service):
    image_bytes = create_image_bytes("BMP")

    with pytest.raises(InvalidImageFormatError):
        image_service.load_image(image_bytes, "image/jpeg")


def test_accepts_image_within_size_limit(image_service):
    image_bytes = create_image_bytes("PNG")

    assert len(image_bytes) < MAX_IMAGE_SIZE

    result = image_service.load_image(image_bytes, "image/png")

    assert result.size == (100, 100)


def test_rejects_image_exceeding_size_limit(image_service):
    image_bytes = b"x" * (MAX_IMAGE_SIZE + 1)

    with pytest.raises(InvalidImageSizeError, match="8 MB"):
        image_service.load_image(image_bytes, "image/jpeg")


def test_rejects_empty_file(image_service):
    with pytest.raises(EmptyImageFileError):
        image_service.load_image(b"", "image/jpeg")


def test_rejects_missing_content_type(image_service):
    image_bytes = create_image_bytes("JPEG")

    with pytest.raises(InvalidImageContentTypeError):
        image_service.load_image(image_bytes, None)
