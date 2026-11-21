from abc import ABC, abstractmethod

from PIL import Image

from app.schemas.product import Recognition


class ImageServiceInterface(ABC):
    @abstractmethod
    def recognize(
        self,
        image_bytes: bytes,
        content_type: str | None,
    ) -> list[Recognition]:
        pass

    @abstractmethod
    def load_image(
        self,
        image_bytes: bytes,
        content_type: str | None,
    ) -> Image.Image:
        pass
