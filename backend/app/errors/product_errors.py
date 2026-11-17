class ProductError(Exception):
    """Base exception for product validation errors."""


class ProductDbError(ProductError):
    """Base exception for droduct database errors."""


class ProductNameAlreadyExistsError(ProductDbError):
    """Raised when a typed name of product already exists."""
