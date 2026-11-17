from enum import Enum


class FilterOperator(str, Enum):
    MORE = "more"
    LESS = "less"
    EQUALS = "equals"
