from tkinter import filedialog
import logging
from typing import List, Dict, Tuple, Union, Optional
from datetime import date
from gui.app.basewindow import BaseWindow
from core.logging.logging_tools import log_fn
import features.importer.mt940.interpreter as mt940_interpreter
import features.importer.mt940.database_service as mt940_database_service
import features.account.account_repository as account_repository
from features.importer.mt940.parser import pars_file
from models.transaction.imported import ImportedTransaction


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
    data: List[ImportedTransaction],
    filter_columns: List[str]
) -> List[List[Union[str, Tuple[str], int, float]]]:
    """
    Convert parsed transaction dictionaries into a tabular list format.

    This function extracts only the specified columns from each transaction
    dictionary and converts the data into a list-of-lists structure suitable
    for table widgets such as tksheet.

    Args:
        data (List[ImportedTransaction]):
            List of ImportedTransaction containing parsed MT940 data.
        filtered_columns (List[str]):
            List of keys to include in the output table.

    Returns:
        List[List[Union[str, Tuple[str], int, float]]]:
            Tabular representation of the filtered transaction data.
            Each inner list represents one row.
    """
    formatted_data: List[
        List[Union[str, Tuple[str], int, float]]
    ] = []

    for transaction in data:
        row = []

        for column in filter_columns:
            row.append(getattr(transaction, column))

        formatted_data.append(row)

    return formatted_data


def get_account_data(account_id: int) -> Dict[str, str | float | int | date]:
    # TODO: use function from account_service
    # TODO: add docs
    temp_account_data = account_repository.get_account_data()
    # [AccountID(int), AccountName(str), AccountNumber(str),
    # AccountBalance(float), RecordDate(str)]
    # (3, 'Sparbuch 2', '3073527115', 226.99, '2024-12-30')
    for account_data in temp_account_data:
        if id == account_id:
            account = {
                "account_id": account_data.id,
                "account_name": account_data.name,
                "account_number": account_data.number,
                "account_balance": account_data.balance,
                "last_record_date": account_data.record_date
            }
            return account
    return {}


@log_fn
def import_mt940_file_gui(
        master: BaseWindow, columns: List[str] = [
            "opening_balance", "date", "booking_date", "amount",
            "transaction_type_name", "purpose", "counterparty_account_number",
            "counterparty_name"], path: Optional[str] = None
        ) -> Tuple[
                str,
                List[str],
                List[List[Union[str, Tuple[str], int, float]]],
                Dict[str, str | float | int | date],
                str
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
        columns (List[str], optional):
            Column names used for formatting the parsed data.
            Defaults to:
            [
                "OpeningBalance", "Date", "Bookingdate",
                "Amount", "TransactionTypeName", "Purpose",
                "CounterpartyAccount", "CounterpartyName"
            ]

    Returns:
        Tuple[str, List[str],
                        List[List[Union[str, Tuple[str], int, float]]],
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
        formatted_data = format_data(parsed_data, columns)

        (interpreted_data, closing_balance
         ) = mt940_interpreter.interpret_transactions(
            parsed_data, master
            )
        (interpreted_history_data, latest
         ) = mt940_interpreter.interpret_account_history_entries(
             closing_balance)

        new_balance = str(next(iter(latest.values()))[1])
        # {'1077149530': ('260702', '200.00', 1)}

        headers = columns

        first_entry = parsed_data[0]
        if parsed_data:
            account_id = account_repository.get_account_id(
                data=["", str(first_entry.account_number), "", ""],
                supplied_data=[False, True, False, False]
                )
            account_data = get_account_data(account_id)
        else:
            logger.info("Empty file selected.")
            return ("", [], [], {}, "")

        return (file_path, headers, formatted_data, account_data, new_balance)
    else:
        logger.info("No file selected.")
        return ("", [], [], {}, "")
