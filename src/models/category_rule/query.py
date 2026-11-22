from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

QueryValue: TypeAlias = str | int | float | bool | None


class LogicalOperator(StrEnum):
    AND = "AND"
    OR = "OR"


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


class DatePartOperator(StrEnum):
    WEEKDAY = "WEEKDAY"
    """0-6 0: Monday"""
    MONTH = "MONTH"
    """1-12 1: January"""


class DateRangeOperator(StrEnum):
    BETWEEN = "BETWEEN"
    """Absolut date range (with year)"""
    DATE_RANGE = "DATE_RANGE"
    """Relative date range (without year)"""


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
    end: str


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
