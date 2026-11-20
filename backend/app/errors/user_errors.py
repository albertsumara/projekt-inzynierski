class UserError(Exception):
    """Base exception for product validation errors."""


class UserDbError(UserError):
    """Base exception for user database errors."""


class UserNotFoundError(UserDbError):
    """Raised when a product with the given ID does not exist."""
