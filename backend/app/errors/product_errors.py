class ProductError(Exception):
    """Base exception for product validation errors."""


class ProductDbError(ProductError):
    """Base exception for product database errors."""


class ProductNameAlreadyExistsError(ProductDbError):
    """Raised when a typed name of product already exists."""


class ProductNotFoundError(ProductDbError):
    """Raised when a product with the given ID does not exist."""
