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
from models.transaction.imported import ImportedTransaction
from models.transaction.imported_view import ImportedTransactionView
from models.account.entity import Account


logger = logging.getLogger(__name__)


@log_fn
def insert_all_data_to_db(data: List[ImportedTransaction],
                          window: BaseWindow) -> None:
    """
    Process parsed MT940 data and insert all related
    information into the database.

    This function orchestrates the full import pipeline for MT940 data:
        1. Interprets raw transaction data into database-ready structures.
        2. Inserts transactions into the database.
        3. Processes account history (closing balances).
        4. Inserts account history entries.
        5. Updates account balances with the latest values.

    Args:
        data (List):
            List of ImportedTransaction containing
            parsed MT940 transaction data.
        window (BaseWindow):
            Main application window used for context during interpretation.

    Raises:
        DatabaseMT940Error:
            If any database insertion or processing step fails.
    """
    (interpreted_data,
     closing_balance) = mt940_interpreter.interpret_transactions(data, window)
    mt940_database_service.add_transactions(interpreted_data)

    # Add the closing balance to the database
    (interpreted_history_data, latest
     ) = mt940_interpreter.interpret_account_history_entries(closing_balance)
    mt940_database_service.add_account_history_entries(
        interpreted_history_data)

    mt940_database_service.update_account_balances(latest)
    logger.debug("Bank statement successfully inserted to database.")


@log_fn
def import_mt940_file(master: BaseWindow) -> None:
    """
    Import an MT940 formatted text file via a GUI file dialog and process it.

    This function:
        1. Opens a file selection dialog.
        2. Reads the selected file using UTF-8 encoding.
        3. Parses the MT940 file content into structured data.
        4. Passes the parsed data to the database import pipeline.
        5. Refreshes the UI after successful import.

    If no file is selected, the function logs this event and exits without
    further processing.

    Args:
        master (BaseWindow):
            Main application window used as parent for the file dialog
            and to trigger UI refresh after import.

    Returns:
        None
    """
    file_path = filedialog.askopenfilename(
        parent=master,
        title="Select MT940 Text File",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    if file_path:
        logger.info("Start importing bank statment.")
        with open(file_path, 'r', encoding='utf8') as file:
            file_content = file.read()

        parsed_data = pars_file(file_content)
        insert_all_data_to_db(parsed_data, master)
        logger.info("Imported bank statment successfully.")
        master.reload()
    else:
        logger.info("No file selected.")


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
def import_mt940_file_gui(
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
    Open a file dialog to import an MT940 text file and parse its content.

    This function allows the user to select a text file via a GUI file dialog.
    If a file is selected, it reads and parses the MT940 content, converts it
    into a structured format, and returns the selected file path together with
    the table headers and formatted transaction data.

    Workflow:
        1. Open file selection dialog.
        2. Read selected file using UTF-8 encoding.
        3. Parse MT940 content into structured blocks.
        4. Convert parsed data into tabular format.
        5. Return the selected file path, headers, and formatted data.

    If no file is selected, an empty result is returned.

    Args:
        master (BaseWindow):
            Parent window used to attach the file dialog.

    Returns:
        Tuple[str, List[str],
            List[List[Union[str, float, Tuple[str, str, str]]]],
            Dict[str, str | float | int]]:
            A tuple containing:
            - file_path: Path to the selected MT940 file.
            - headers: List of column names.
            - formatted_data: Table-like list of rows containing parsed values.
            - account_info: Dictionary with account metadata:
                "account_id", "account_name", "account_number",
                "account_balance", "last_record_date"
            - new_balance: String containing the new account balance

            If no file is selected, returns ("", [], [], {}, "").
    """
    # TODO: update docs

    if path is None:
        file_path = filedialog.askopenfilename(
            parent=master,
            title="Select MT940 Text File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
    else:
        file_path = path

    if file_path:
        logger.info("Start importing bank statment.")

        with open(file_path, 'r', encoding='utf8') as file:
            file_content = file.read()

        parsed_data = pars_file(file_content)

        (interpreted_data, closing_balance
         ) = mt940_interpreter.interpret_transactions_gui(
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

        first_entry = parsed_data[0]
        if parsed_data:
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
