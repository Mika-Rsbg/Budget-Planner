import logging
from typing import List, Any
from models.transaction.imported_view import ImportedTransactionView
from features.importer.formater.table_config import TableColumn


logger = logging.getLogger(__name__)


def format_data(
    data: list[ImportedTransactionView],
    columns: list[TableColumn]
) -> List[List[Any]]:
    """Convert transactions into table data."""
    # TODO: specify docs
    formatted_data = []

    for transaction in data:
        row = []

        for column in columns:
            value = getattr(transaction, column.attribute)

            if column.formatter is not None:
                value = column.formatter(value)

            row.append(value)

        formatted_data.append(row)

    logger.debug("Formatted ImportedTransactionView's for table view.")
    return formatted_data
