import pytest
from app.errors.image_errors import (
    EmptyImageFileError,
    InvalidImageContentTypeError,
    InvalidImageFormatError,
    InvalidImageSizeError,
)
from app.services.image_service import MAX_IMAGE_SIZE, ImageService, InvalidImageError
from tests.helpers import DeterministicImageClassifier, create_image_bytes


@pytest.fixture
def image_service():
    return ImageService(DeterministicImageClassifier())


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


def test_rejects_corrupted_image(image_service):
    with pytest.raises(InvalidImageError, match="invalid or corrupted"):
        image_service.load_image(b"not-an-image", "image/jpeg")


def test_recognize_returns_classifier_results():
    classifier = DeterministicImageClassifier()
    service = ImageService(image_classifier=classifier)
    image_bytes = create_image_bytes("JPEG")

    result = service.recognize(image_bytes, "image/jpeg")

    assert len(result) == 1
    assert result[0].id_ml == 7
    assert result[0].confidence == 0.95
