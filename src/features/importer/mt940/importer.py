from tkinter import filedialog
import logging
from typing import List, Dict, Tuple, Union
from gui.app.basewindow import BaseWindow
from core.logging.logging_tools import log_fn
import features.importer.mt940.interpreter as mt940_interpreter
import features.importer.mt940.database_service as mt940_database_service
from features.importer.mt940.parser import pars_file


logger = logging.getLogger(__name__)


class DatabaseMT940Error(Exception):
    """General exception class for database errors."""
    pass


@log_fn
def insert_all_data_to_db(data: List, window: BaseWindow) -> None:
    """Insert the transactions and everything else, like account history and
        stuff, into the database. Using database utils.

    Args:
        data (List): A List of dictionaries containing the transactions.
        window (BaseWindow): The main window of the application.

    Raises:
        DatabaseMT940Error: If there is an error inserting the transactions
            into the database.
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
    Import an MT940 formatted file using a file dialog and process its
    contents.

    This function opens a file dialog attached to the provided master window,
    prompting the user
    to select a text file (typically containing MT940 formatted data).
    If a file is selected, the function:
        - Reads the content of the file using UTF-8 encoding.
        - Splits the content into blocks using split_toblocks_mt940.
        - Parses the blocks with parse_block.
        - Inserts the parsed transactions into the program by calling
          insert_transactions, using the provided master window for context.

    If no file is selected, the function loggs a message indicating that no
    file was chosen.

    Args:
        master: The parent window (or main window) used to anchor the file
                dialog and interact with the user.

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
    Format the parsed data into a List of Lists, which can be used for tksheet.

    Args:
        data (List[Dict[str, Union[str, Tuple[str], int, float]]]): A List of
            dictionaries containing the parsed data.

    Returns:
        List[List[Union[str, Tuple[str], int, float]]]: A List
            of Lists containing the formatted data.
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


def get_headers(
    data: List[Dict[str, Union[str, Tuple[str], int, float]]]
) -> List[str]:
    """
    Get the headers from the parsed data.

    Args:
        data (List[Dict[str, Union[str, Tuple[str], int, float]]]): A List of
            dictionaries containing the parsed data.
    Returns:
        List[str]: A List of strings containing the headers.
    """
    if not data:
        return []
    headers = list(data[0].keys())
    return headers


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
    Import an MT940 formatted file using a file dialog and process its
    contents.

    This function opens a file dialog attached to the provided master window,
    prompting the user
    to select a text file (typically containing MT940 formatted data).
    If a file is selected, the function:
        - Reads the content of the file using UTF-8 encoding.
        - Splits the content into blocks using split_toblocks_mt940.
        - Parses the blocks with parse_block.
        - Inserts the parsed transactions into the program by calling
          insert_transactions, using the provided master window for context.

    If no file is selected, the function loggs a message indicating that no
    file was chosen.

    Args:
        master: The parent window (or main window) used to anchor the file
                dialog and interact with the user.

    Returns:
        None
    """

    # Reference STARTUMSE
    # Account 0000000000
    # OpeningBalance 0000.00
    # Date 010122
    # Bookingdate 0101
    # Amount 000.00
    # TransactionTypeNumber 000
    # TransactionTypeName UEBERTRAG (GUTSCHR. UEBERW)
    # PurposeAddition SVWZ
    # Purpose Spareinlagen
    # CounterpartyAccount DE00000000000000000000
    # CounterpartyName Mika Rosenberge
    # ClosingBalance ('0000000000', '010100', '0000.00')

    # TODO: Update docu
    # TODO: Typ annotation
    # TODO: Add datatyp Transaction and clear mess
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
