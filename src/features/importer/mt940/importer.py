import logging
from tkinter import filedialog

import features.importer.mt940.database_service as mt940_database_service
import features.importer.mt940.interpreter as mt940_interpreter
from core.logging.logging_tools import log_fn
from features.account import account_repository
from features.account.account_repository import get_account_by_id
from features.importer.formater.table_config import TRANSACTION_TABLE_COLUMNS
from features.importer.formater.table_formater import format_data
from features.importer.mt940.errors import InvalidMT940FileError
from features.importer.mt940.parser import pars_file
from gui.app.basewindow import BaseWindow
from models.account.entity import Account
from models.transaction.import_view import TransactionImportView

logger = logging.getLogger(__name__)


@log_fn
def import_mt940_file(
    master: BaseWindow, path: str | None = None
) -> tuple[
    str,
    list[str],
    list[list[str | float]],
    Account,
    str,
    list[TransactionImportView],
    list[tuple[int, float, str, str]],
    dict[str, tuple[str, float, int]],
    bool,
]:
    """
    Import and parse an MT940 bank statement file.

    If ``path`` is provided, the specified file is imported directly.
    Otherwise, a file selection dialog is opened and the user can select
    an MT940 text file.

    The selected file is read using UTF-8 encoding and parsed into
    structured transaction data. The transactions are then formatted
    for display in the transaction table. Account information,
    the new account balance, and account history
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

        - account_data (Account):
            Account associated with the imported transactions.

        - new_balance (str):
            Closing balance of the imported account as a string.

        - interpreted_data (List[TransactionImportView]):
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

    if path is None:
        logger.debug("No file path was provided. Open filedialog.")
        file_path = filedialog.askopenfilename(
            parent=master,
            title="Select MT940 Text File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")),
        )
        logger.debug("Filedialog closed.")
    else:
        logger.debug("File path was provided. No filedialog needed.")
        file_path = path

    if file_path:
        logger.info("Start importing bank statment.")

        with open(file_path, "r", encoding="utf8") as file:
            file_content = file.read()

        try:
            parsed_data = pars_file(file_content)
        except InvalidMT940FileError:
            logger.exception("")
        finally:
            parsed_data = None

        if parsed_data:
            (interpreted_data, closing_balance) = (
                mt940_interpreter.interpret_transactions(parsed_data, master)
            )

            formatted_data = format_data(
                interpreted_data, TRANSACTION_TABLE_COLUMNS
            )

            (interpreted_history_data, latest) = (
                mt940_interpreter.interpret_account_history_entries(
                    closing_balance
                )
            )

            try:
                new_balance = str(next(iter(latest.values()))[1])
                # latest: {'1077149530': ('260702', '200.00', 1)}
            except StopIteration:
                logger.info("Empty file selected")
                new_balance = "n.a."

            headers = [column.header for column in TRANSACTION_TABLE_COLUMNS]

            first_entry = parsed_data[0]
            account_id = account_repository.get_account_id(
                data=["", str(first_entry.account_number), "", ""],
                supplied_data=[False, True, False, False],
            )
            account_data = get_account_by_id(account_id)
            assert account_data is not None
        else:
            logger.info("Empty file selected.")
            return (
                file_path,
                ["null"],
                [["null"]],
                Account.empty(),
                "n.a.",
                [TransactionImportView.empty()],
                [(0, 0.0, "", "")],
                {"": ("", 0.0, 0)},
                False,
            )

        return (
            file_path,
            headers,
            formatted_data,
            account_data,
            new_balance,
            interpreted_data,
            interpreted_history_data,
            latest,
            True,
        )
    else:
        logger.info("No file selected.")
        return (
            "n.a.",
            ["null"],
            [["null"]],
            Account.empty(),
            "n.a.",
            [TransactionImportView.empty()],
            [(0, 0.0, "", "")],
            {"": ("", 0.0, 0)},
            False,
        )


@log_fn
def insert_transactions_to_db(
    data: list[TransactionImportView],
    history_data: list[tuple[int, float, str, str]],
    latest: dict[str, tuple[str, float, int]],
) -> None:
    """Persist import transactions, history entries, and account balances.

    Args:
        data: Imported transactions to add to the database.
        history_data: Account history entries to add to the database.
        latest: Latest account balances keyed by account identifier.
    """
    mt940_database_service.add_transactions(data)

    # Add the closing balance to the database
    mt940_database_service.add_account_history_entries(history_data)

    mt940_database_service.update_account_balances(latest)
    logger.debug("Bank statement successfully inserted to database.")
