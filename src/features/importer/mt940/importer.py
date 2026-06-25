from tkinter import filedialog
import logging
from typing import List, Dict, Tuple, Union
from gui.app.basewindow import BaseWindow
from core.logging.logging_tools import log_fn
import features.importer.mt940.interpreter as mt940_interpreter
import features.importer.mt940.database_service as mt940_database_service
from features.importer.mt940.parser import pars_file


logger = logging.getLogger(__name__)


@log_fn
def insert_all_data_to_db(data: List, window: BaseWindow) -> None:
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
            List of dictionaries containing parsed MT940 transaction data.
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
    data: List[Dict[str, Union[str, Tuple[str], int, float]]],
    filtered_columns: List[str]
) -> List[List[Union[str, Tuple[str], int, float]]]:
    """
    Convert parsed transaction dictionaries into a tabular list format.

    This function extracts only the specified columns from each transaction
    dictionary and converts the data into a list-of-lists structure suitable
    for table widgets such as tksheet.

    Args:
        data (List[Dict[str, Union[str, Tuple[str], int, float]]]):
            List of transaction dictionaries containing parsed MT940 data.
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
        line = []

        for (key, value) in transaction.items():
            if key in filtered_columns:
                line.append(value)

        formatted_data.append(line)

    return formatted_data


@log_fn
def import_mt940_file_gui(
        master: BaseWindow, columns: List[str] = [
            "Account", "OpeningBalance", "Date", "Bookingdate", "Amount",
            "TransactionTypeName", "Purpose", "CounterpartyAccount",
            "CounterpartyName"]
        ) -> Tuple[
            List[str], List[List[Union[str, Tuple[str], int, float]]]
        ]:
    """
    Open a file dialog to import an MT940 text file and parse its content.

    This function allows the user to select a text file via a GUI file dialog.
    If a file is selected, it reads and parses the MT940 content, converts it
    into a structured format, and returns headers together with formatted data
    ready for further processing or display.

    Workflow:
        1. Open file selection dialog.
        2. Read selected file using UTF-8 encoding.
        3. Parse MT940 content into structured blocks.
        4. Convert parsed data into tabular format.

    If no file is selected, an empty result is returned.

    Args:
        master (BaseWindow):
            Parent window used to attach the file dialog.
        columns (List[str], optional):
            Column names used for formatting the parsed data.
            Defaults to:
            [
                "Account", "OpeningBalance", "Date", "Bookingdate",
                "Amount", "TransactionTypeName", "Purpose",
                "CounterpartyAccount", "CounterpartyName"
            ]

    Returns:
        Tuple[List[str], List[List[Union[str, Tuple[str], int, float]]]]:
            A tuple containing:
            - headers: List of column names
            - formatted_data: Table-like list of rows containing parsed values

            If no file is selected, returns ([], []).
    """
    # TODO: Typ annotation
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
        formatted_data = format_data(parsed_data, columns)
        headers = columns
        return (headers, formatted_data)
    else:
        logger.info("No file selected.")
        return ([], [])
