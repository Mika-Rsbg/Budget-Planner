import logging
from datetime import date as datetime

from models.category_rule.entity import CategoryRule
from models.category_rule.query import (
    LogicalOperator,
    Query,
    QueryCondition,
    QueryDatePartCondition,
    QueryDateRangeCondition,
    QueryGroup,
)
from models.transaction.import_view import TransactionImportView

logger = logging.getLogger(__name__)


def evaluate(
    rule: CategoryRule | Query, transaction: TransactionImportView
) -> bool:
    if type(rule) is CategoryRule:
        query = rule.query
    else:
        query = rule

    if query is None:
        return False

    match query:
        case QueryGroup():
            if query.operator == LogicalOperator.AND:
                evaluated = False
                for child in query.children:
                    evaluated = evaluate(child, transaction)
                    if evaluated is False:
                        break
                return evaluated
            else:
                evaluated = False
                for child in query.children:
                    evaluated = evaluate(child, transaction)
                    if evaluated is True:
                        break
                return evaluated
        case QueryCondition():
            actual_value = getattr(
                transaction,
                query.field,
            )
            evaluated = query.operator.function(actual_value, query.value)

            return evaluated
        case QueryDatePartCondition():
            actual_value = getattr(
                transaction,
                query.field,
            )
            try:
                assert actual_value is datetime
            except AssertionError:
                logger.exception(
                    "Field of a date Condition musst be a date field"
                )
            evaluated: bool = query.operator.function(
                actual_value, query.value
            )

            return evaluated
        case QueryDateRangeCondition():
            actual_value = getattr(
                transaction,
                query.field,
            )
            try:
                assert actual_value is datetime
            except AssertionError:
                logger.exception(
                    "Field of a date Condition musst be a date field"
                )
            evaluated = query.operator.function(
                actual_value, query.start, query.end
            )

            return evaluated

    return False
