class ImageError(ValueError):
    """Base exception for image validation errors."""


class InvalidImageFormatError(ImageError):
    """Raised when the image format is not supported."""


class InvalidImageContentTypeError(ImageError):
    """Raised when the uploaded file has an unsupported content type."""


class InvalidImageSizeError(ImageError):
    """Raised when the uploaded image exceeds the maximum allowed size."""


class EmptyImageFileError(ImageError):
    """Raised when the uploaded image file is empty."""
