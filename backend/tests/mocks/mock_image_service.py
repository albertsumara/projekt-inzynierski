from app.schemas.product import Recognition
from app.services.interfaces.image_service_interface import ImageServiceInterface
from PIL import Image


class MockImageService(ImageServiceInterface):
    def __init__(
        self,
        *,
        recognitions: list[Recognition] | None = None,
        loaded_image: Image.Image | None = None,
        recognize_error: Exception | None = None,
        load_error: Exception | None = None,
    ) -> None:
        self.recognitions = recognitions or []
        self.loaded_image = loaded_image
        self.recognize_error = recognize_error
        self.load_error = load_error
        self.recognize_calls: list[tuple[bytes, str | None]] = []
        self.load_image_calls: list[tuple[bytes, str | None]] = []

    def recognize(
        self,
        image_bytes: bytes,
        content_type: str | None,
    ) -> list[Recognition]:
        self.recognize_calls.append((image_bytes, content_type))
        if self.recognize_error is not None:
            raise self.recognize_error
        return self.recognitions

    def load_image(
        self,
        image_bytes: bytes,
        content_type: str | None,
    ) -> Image.Image:
        self.load_image_calls.append((image_bytes, content_type))
        if self.load_error is not None:
            raise self.load_error
        if self.loaded_image is not None:
            return self.loaded_image
        return Image.new("RGB", (100, 100), color="red")
