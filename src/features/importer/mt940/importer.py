from tkinter import filedialog
import logging
from typing import List, Tuple, Union, Optional, Any, Dict
from gui.app.basewindow import BaseWindow
from core.logging.logging_tools import log_fn
from features.account.account_repository import get_account_by_id
import features.importer.mt940.interpreter as mt940_interpreter
import features.importer.mt940.database_service as mt940_database_service
import features.account.account_repository as account_repository
from features.importer.mt940.parser import pars_file
from features.importer.mt940.table_config import (TableColumn,
                                                  TRANSACTION_TABLE_COLUMNS)
from models.transaction.imported_view import ImportedTransactionView
from models.account.entity import Account


logger = logging.getLogger(__name__)


def format_data(
    data: list[ImportedTransactionView],
    columns: list[TableColumn]
) -> list[list[Any]]:
    """Convert transactions into table data."""
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


def get_initial_selected_rows(
    data: list[ImportedTransactionView],
) -> list[int]:
    """
    Return rows that should be selected initially,
    because they aren't in the database.
    """
    return [
        index
        for index, transaction in enumerate(data)
        if not transaction.in_database
    ]


@log_fn
def import_mt940_file(
        master: BaseWindow, path: Optional[str] = None
        ) -> Tuple[
                str,
                List[str],
                List[List[Union[str, float]]],
                List[int],
                Account,
                str,
                List[ImportedTransactionView],
                List[Tuple[int, float, str, str]],
                Dict[str, Tuple[str, float, int]],
                bool
            ]:
    """
    Import and parse an MT940 bank statement file.

    If ``path`` is provided, the specified file is imported directly.
    Otherwise, a file selection dialog is opened and the user can select
    an MT940 text file.

    The selected file is read using UTF-8 encoding and parsed into
    structured transaction data. The transactions are then formatted
    for display in the transaction table. Account information, the
    initial selected rows, the new account balance, and account history
    information are also extracted.

    Args:
        master (BaseWindow):
            Parent window used for the file selection dialog and passed
            to the MT940 transaction interpreter.

        path (Optional[str]):
            Path to the MT940 file to import. If ``None``, a file selection
            dialog is opened to let the user choose a file.

    Returns:
        Tuple containing:

        - file_path (str):
            Path to the imported MT940 file, or ``"n.a."`` if no file
            was selected or the file contains no account data.

        - headers (List[str]):
            Column headers for the formatted transaction table.

        - formatted_data (List[List[Union[str, float]]]):
            Transaction data formatted for display in the transaction
            table.

        - initial_selected_rows (List[int]):
            Indices of the transaction rows that should initially be
            selected. (All Transactions that are not allready in the database)

        - account_data (Account):
            Account associated with the imported transactions.

        - new_balance (str):
            Closing balance of the imported account as a string.

        - interpreted_data (List[ImportedTransactionView]):
            Parsed and interpreted transaction entries.

        - interpreted_history_data (List[Tuple[int, float, str, str]]):
            Interpreted account history entries derived from the closing
            balance.

        - latest (Dict[str, Tuple[str, float, int]]):
            Latest account balance information returned by the account
            history interpreter.

        - success (bool):
            ``True`` if an MT940 file was successfully imported and
            processed; otherwise ``False``.

    Notes:
        If no file is selected, or if the selected file contains no
        parsable account data, a default result indicating an unsuccessful
        import is returned.
    """
    # TODO: update docs

    if path is None:
        logger.debug("No file path was provided. Open filedialog.")
        file_path = filedialog.askopenfilename(
            parent=master,
            title="Select MT940 Text File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        logger.debug("Filedialog closed.")
    else:
        logger.debug("File path was provided. No filedialog needed.")
        file_path = path

    if file_path:
        logger.info("Start importing bank statment.")

        with open(file_path, 'r', encoding='utf8') as file:
            file_content = file.read()

        parsed_data = pars_file(file_content)

        (interpreted_data, closing_balance
         ) = mt940_interpreter.interpret_transactions(
            parsed_data, master
            )

        formatted_data = format_data(
            interpreted_data, TRANSACTION_TABLE_COLUMNS
        )

        initial_selected_rows = get_initial_selected_rows(interpreted_data)

        (interpreted_history_data, latest
         ) = mt940_interpreter.interpret_account_history_entries(
             closing_balance)

        new_balance = str(next(iter(latest.values()))[1])
        # latest: {'1077149530': ('260702', '200.00', 1)}

        headers = [
            column.header
            for column in TRANSACTION_TABLE_COLUMNS
        ]

        if parsed_data:
            first_entry = parsed_data[0]
            account_id = account_repository.get_account_id(
                data=["", str(first_entry.account_number), "", ""],
                supplied_data=[False, True, False, False]
                )
            account_data = get_account_by_id(account_id)
            assert account_data is not None
        else:
            logger.info("Empty file selected.")
            return ("n.a.", ["null"], [["null"]], [], Account.empty(), "n.a.",
                    [ImportedTransactionView.empty()], [(0, 0.0, "", "")],
                    {"": ("", 0.0, 0)}, False)

        return (file_path, headers, formatted_data,
                initial_selected_rows, account_data, new_balance,
                interpreted_data, interpreted_history_data, latest, True)
    else:
        logger.info("No file selected.")
        return ("n.a.", ["null"], [["null"]], [], Account.empty(), "n.a.",
                [ImportedTransactionView.empty()], [(0, 0.0, "", "")],
                {"": ("", 0.0, 0)}, False)


@log_fn
def insert_transactions_to_db(data: List[ImportedTransactionView],
                              history_data: List[Tuple[int, float, str, str]],
                              latest: Dict[str, Tuple[str, float, int]],
                              window: BaseWindow) -> None:
    # TODO: add docs
    mt940_database_service.add_transactions(data)

    # Add the closing balance to the database
    mt940_database_service.add_account_history_entries(history_data)

    mt940_database_service.update_account_balances(latest)
    logger.debug("Bank statement successfully inserted to database.")
