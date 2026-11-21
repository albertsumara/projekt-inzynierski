from typing import Any, TypeVar

from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import ColumnElement

from app.schemas.filter import FilterOperator, NumberFilter

QueryResult = TypeVar("QueryResult")


def apply_number_filter(
    query: Query[QueryResult],
    column: ColumnElement[Any],
    number_filter: NumberFilter,
) -> Query[QueryResult]:
    if number_filter.operator == FilterOperator.MORE:
        condition = column > number_filter.value
    elif number_filter.operator == FilterOperator.LESS:
        condition = column < number_filter.value
    elif number_filter.operator == FilterOperator.EQUALS:
        condition = column == number_filter.value
    else:
        raise ValueError(
            f"Unsupported numeric filter operator: {number_filter.operator}"
        )

    return query.filter(condition)
