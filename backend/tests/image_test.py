import pytest
from app.errors.image_errors import (
    EmptyImageFileError,
    ImageError,
    InvalidImageContentTypeError,
    InvalidImageFormatError,
    InvalidImageSizeError,
)
from app.services.image_service import MAX_IMAGE_SIZE, ImageService, InvalidImageError
from app.services.interfaces.image_service_interface import ImageServiceInterface
from PIL import Image
from tests.mocks import (
    MockImageClassifier,
    MockImageService,
    create_image_bytes,
)


@pytest.fixture
def image_service():
    return ImageService()


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


@pytest.mark.parametrize(
    "error",
    [
        EmptyImageFileError("empty"),
        InvalidImageContentTypeError("content type"),
        InvalidImageFormatError("format"),
        InvalidImageSizeError("size"),
        InvalidImageError("corrupted"),
    ],
)
def test_image_errors_share_the_image_error_base(error):
    assert isinstance(error, ImageError)


def test_recognize_returns_classifier_results():
    classifier = MockImageClassifier()
    service = ImageService(image_classifier=classifier)
    image_bytes = create_image_bytes("JPEG")

    result = service.recognize(image_bytes, "image/jpeg")

    assert len(result) == 1
    assert result[0].id_ml == 7
    assert result[0].confidence == 0.95
    assert len(classifier.calls) == 1


def test_mock_image_service_implements_service_interface():
    assert isinstance(MockImageService(), ImageServiceInterface)


def test_mock_image_service_records_recognize_call():
    from app.schemas.product import Recognition

    recognitions = [Recognition(id_ml=3, confidence=0.75)]
    mock = MockImageService(recognitions=recognitions)

    result = mock.recognize(b"image-data", "image/jpeg")

    assert result == recognitions
    assert mock.recognize_calls == [(b"image-data", "image/jpeg")]
