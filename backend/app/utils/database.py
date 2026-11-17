from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError


def raise_for_constraint(
    error: SQLAlchemyIntegrityError,
    constraints: dict[str, type[Exception]],
):
    constraint_name = getattr(
        getattr(error.orig, "diag", None), "constraint_name", None
    )

    exception_class = constraints.get(constraint_name)
    if exception_class:
        raise exception_class() from error
