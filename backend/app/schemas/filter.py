from enum import Enum

from pydantic import BaseModel


class FilterOperator(str, Enum):
    MORE = "more"
    LESS = "less"
    EQUALS = "equals"


class NumberFilter(BaseModel):
    operator: FilterOperator
    value: float
