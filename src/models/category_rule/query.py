from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from operator import eq, ge, gt, le, lt, ne
from typing import TypeAlias

QueryValue: TypeAlias = str | int | float | bool | None


class LogicalOperator(StrEnum):
    AND = "AND"
    OR = "OR"


def contains(a: str, b: str) -> bool:
    return b.lower() in a.lower()


def not_contains(a: str, b: str) -> bool:
    return b.lower() not in a.lower()


def starts_with(a: str, b: str) -> bool:
    return a.casefold().startswith(b.casefold())


def ends_with(a: str, b: str) -> bool:
    return a.casefold().endswith(b.casefold())


class QueryOperator(StrEnum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="

    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"

    @property
    def function(self) -> Callable:
        return {
            QueryOperator.EQUAL: eq,
            QueryOperator.NOT_EQUAL: ne,
            QueryOperator.LESS_THAN: lt,
            QueryOperator.LESS_THAN_OR_EQUAL: le,
            QueryOperator.GREATER_THAN: gt,
            QueryOperator.GREATER_THAN_OR_EQUAL: ge,
            QueryOperator.CONTAINS: contains,
            QueryOperator.NOT_CONTAINS: not_contains,
            QueryOperator.STARTS_WITH: starts_with,
            QueryOperator.ENDS_WITH: ends_with,
        }[self]


def weekday(a: date, b: int) -> bool:
    return a.weekday() == b


def month(a: date, b: int) -> bool:
    return a.month == b


class DatePartOperator(StrEnum):
    WEEKDAY = "WEEKDAY"
    """0-6 0: Monday"""
    MONTH = "MONTH"
    """1-12 1: January"""

    @property
    def function(self) -> Callable:
        return {
            DatePartOperator.WEEKDAY: weekday,
            DatePartOperator.MONTH: month,
        }[self]


def between(a: date, b: str, c: str) -> bool:
    start_date = datetime.strptime(b, "%d.%m.%Y").date()
    end_date = datetime.strptime(c, "%d.%m.%Y").date()

    return start_date <= a <= end_date


def date_range(a: date, b: str, c: str) -> bool:
    start_date = datetime.strptime(b, "%d.%m.").date()
    end_date = datetime.strptime(c, "%d.%m.").date()

    current = (a.month, a.day)
    start = (start_date.month, start_date.day)
    end = (end_date.month, end_date.day)

    if start <= end:
        return start <= current <= end

    return current >= start or current <= end


class DateRangeOperator(StrEnum):
    BETWEEN = "BETWEEN"
    """Absolut date range (with year)"""
    DATE_RANGE = "DATE_RANGE"
    """Relative date range (without year)"""

    @property
    def function(self) -> Callable:
        return {
            DateRangeOperator.BETWEEN: between,
            DateRangeOperator.DATE_RANGE: date_range,
        }[self]


@dataclass
class QueryCondition:
    field: str
    operator: QueryOperator
    value: QueryValue = None
    tolerance: float = 0.0


@dataclass
class QueryDatePartCondition:
    field: str
    operator: DatePartOperator
    value: int


@dataclass
class QueryDateRangeCondition:
    field: str
    operator: DateRangeOperator
    start: str
    """Format: DD.MM. or DD.MM.YYYY (when using BETWEEN)"""
    end: str
    """Format: DD.MM. or DD.MM.YYYY (when using BETWEEN)"""


@dataclass
class QueryGroup:
    operator: LogicalOperator
    children: list[
        QueryCondition
        | QueryDatePartCondition
        | QueryDateRangeCondition
        | QueryGroup
    ]


Query: TypeAlias = (
    QueryCondition
    | QueryDatePartCondition
    | QueryDateRangeCondition
    | QueryGroup
)

test_query_1 = QueryCondition(
    field="purpose",
    operator=QueryOperator.CONTAINS,
    value="test",
)

test_query = QueryGroup(
    operator=LogicalOperator.OR,
    children=[
        QueryCondition(
            field="amount", operator=QueryOperator.GREATER_THAN, value=120
        ),
        QueryCondition(
            field="purpose",
            operator=QueryOperator.CONTAINS,
            value="test",
        ),
    ],
)

# test_query = QueryCondition(
#     field="amount", operator=QueryOperator.GREATER_THAN, value=120
# )


example_query = QueryGroup(
    operator=LogicalOperator.OR,
    children=[
        QueryCondition(
            field="purpose", operator=QueryOperator.CONTAINS, value="test"
        ),
        QueryGroup(
            operator=LogicalOperator.OR,
            children=[
                QueryDateRangeCondition(
                    field="date",
                    operator=DateRangeOperator.DATE_RANGE,
                    start="01.01",
                    end="31.05",
                ),
                QueryCondition(
                    field="counterparty_id",
                    operator=QueryOperator.EQUAL,
                    value=10,
                ),
            ],
        ),
    ],
)
complex_query = QueryGroup(
    operator=LogicalOperator.AND,
    children=[
        # Condition 1: Counterparty
        QueryCondition(
            field="counterparty_name",
            operator=QueryOperator.CONTAINS,
            value="Amazon",
        ),
        # Condition 2: Amount
        QueryGroup(
            operator=LogicalOperator.OR,
            children=[
                QueryCondition(
                    field="amount",
                    operator=QueryOperator.GREATER_THAN,
                    value=100.0,
                    tolerance=0.5,
                ),
                QueryCondition(
                    field="amount",
                    operator=QueryOperator.LESS_THAN_OR_EQUAL,
                    value=25,
                ),
            ],
        ),
        # Condition 3: Date
        QueryGroup(
            operator=LogicalOperator.OR,
            children=[
                QueryDatePartCondition(
                    field="date",
                    operator=DatePartOperator.MONTH,
                    value=12,
                ),
                QueryGroup(
                    operator=LogicalOperator.AND,
                    children=[
                        QueryDatePartCondition(
                            field="date",
                            operator=DatePartOperator.WEEKDAY,
                            value=4,
                        ),
                        QueryDateRangeCondition(
                            field="date",
                            operator=DateRangeOperator.DATE_RANGE,
                            start="01.11",
                            end="31.12",
                        ),
                    ],
                ),
            ],
        ),
        # Condition 4: Purpose
        QueryGroup(
            operator=LogicalOperator.OR,
            children=[
                QueryCondition(
                    field="purpose",
                    operator=QueryOperator.CONTAINS,
                    value="Bestellung",
                ),
                QueryCondition(
                    field="purpose",
                    operator=QueryOperator.NOT_CONTAINS,
                    value="Stornierung",
                ),
                QueryCondition(
                    field="purpose",
                    operator=QueryOperator.STARTS_WITH,
                    value="Amazon*Prime",
                ),
            ],
        ),
        # Condition 5: Boolean
        QueryCondition(
            field="is_recurring",
            operator=QueryOperator.EQUAL,
            value=True,
        ),
        # Condition 6: Null
        QueryCondition(
            field="category_id",
            operator=QueryOperator.EQUAL,
            value=None,
        ),
        # Condition 7: Absolute date range
        QueryDateRangeCondition(
            field="booking_date",
            operator=DateRangeOperator.BETWEEN,
            start="01.01.2025",
            end="31.12.2026",
        ),
    ],
)
