import logging
from typing import List, Any
from models.transaction.import_view import TransactionImportView
from features.importer.formater.table_config import TableColumn


logger = logging.getLogger(__name__)


def format_data(
    data: list[TransactionImportView],
    columns: list[TableColumn]
) -> List[List[Any]]:
    """Convert imported transactions into rows suitable for a table view.

    Each returned row follows the order of ``columns``. Values are read from
    the transaction attribute named by ``TableColumn.attribute`` and are
    passed through the column's formatter when one is configured.

    Args:
        data: Transactions to convert.
        columns: Column definitions describing the attribute and optional
            formatter to use for each cell.

    Returns:
        List[List[Any]]:
            A list of rows, where each row contains the formatted values for
            one transaction.

    Raises:
        AttributeError: If a column refers to an attribute that a transaction
            does not provide.
        Exception: Any exception raised by a configured column formatter.
    """
    formatted_data = []

    for transaction in data:
        row = []

        for column in columns:
            value = getattr(transaction, column.attribute)

            if column.formatter is not None:
                value = column.formatter(value)

            row.append(value)

        formatted_data.append(row)

    logger.debug("Formatted TransactionImportView's for table view.")
    return formatted_data
