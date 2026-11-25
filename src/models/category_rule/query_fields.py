from dataclasses import dataclass
from enum import StrEnum

from models.category_rule.query import (
    DatePartOperator,
    DateRangeOperator,
    QueryOperator,
)


class QueryFieldType(StrEnum):
    STRING = "STRING"
    SIMPLE_NUMBER = "SIMPLE_NUMBER"
    NUMBER = "NUMBER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"


@dataclass(frozen=True)
class QueryFieldDefinition:
    name: str
    label: str
    field_type: QueryFieldType


QUERY_FIELDS = {
    "date": QueryFieldDefinition(
        name="date",
        label="Datum",
        field_type=QueryFieldType.DATE,
    ),
    "amount": QueryFieldDefinition(
        name="amount",
        label="Betrag",
        field_type=QueryFieldType.FLOAT,
    ),
    "transaction_typ_number": QueryFieldDefinition(
        name="transaction_typ_number",
        label="Transaktions Typ Nummer",
        field_type=QueryFieldType.SIMPLE_NUMBER,
    ),
    "purpose": QueryFieldDefinition(
        name="purpose",
        label="Verwendungszweck",
        field_type=QueryFieldType.STRING,
    ),
    "counterparty_account_number": QueryFieldDefinition(
        name="counterparty_account_number",
        label="Counterparty Kontonummer",
        field_type=QueryFieldType.SIMPLE_NUMBER,
    ),
    "counterparty_name": QueryFieldDefinition(
        name="counterparty_name",
        label="Counterparty Name",
        field_type=QueryFieldType.STRING,
    ),
}

STRING_OPERATORS = (
    QueryOperator.EQUAL,
    QueryOperator.NOT_EQUAL,
    QueryOperator.CONTAINS,
    QueryOperator.NOT_CONTAINS,
    QueryOperator.STARTS_WITH,
    QueryOperator.ENDS_WITH,
)

SIMPLE_NUMBER_OPERATORS = (
    QueryOperator.EQUAL,
    QueryOperator.NOT_EQUAL,
)

NUMBER_OPERATORS = (
    QueryOperator.EQUAL,
    QueryOperator.NOT_EQUAL,
    QueryOperator.LESS_THAN,
    QueryOperator.LESS_THAN_OR_EQUAL,
    QueryOperator.GREATER_THAN,
    QueryOperator.GREATER_THAN_OR_EQUAL,
)

FLOAT_OPERATORS = (
    QueryOperator.EQUAL,
    QueryOperator.NOT_EQUAL,
    QueryOperator.LESS_THAN,
    QueryOperator.LESS_THAN_OR_EQUAL,
    QueryOperator.GREATER_THAN,
    QueryOperator.GREATER_THAN_OR_EQUAL,
)

BOOLEAN_OPERATORS = (
    QueryOperator.EQUAL,
    QueryOperator.NOT_EQUAL,
)

DATE_OPERATORS = (
    QueryOperator.EQUAL,
    QueryOperator.NOT_EQUAL,
    QueryOperator.LESS_THAN,
    QueryOperator.LESS_THAN_OR_EQUAL,
    QueryOperator.GREATER_THAN,
    QueryOperator.GREATER_THAN_OR_EQUAL,
    DatePartOperator.WEEKDAY,
    DatePartOperator.MONTH,
    DateRangeOperator.BETWEEN,
    DateRangeOperator.DATE_RANGE,
)

FIELD_OPERATORS = {
    QueryFieldType.STRING: STRING_OPERATORS,
    QueryFieldType.SIMPLE_NUMBER: SIMPLE_NUMBER_OPERATORS,
    QueryFieldType.NUMBER: NUMBER_OPERATORS,
    QueryFieldType.FLOAT: FLOAT_OPERATORS,
    QueryFieldType.BOOLEAN: BOOLEAN_OPERATORS,
    QueryFieldType.DATE: DATE_OPERATORS,
}
