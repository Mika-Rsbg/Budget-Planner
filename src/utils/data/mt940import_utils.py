import tkinter as tk
from tkinter import filedialog
import logging
from utils.logging.logging_tools import logg
from .database import account_utils as db_account_utils
from .database import account_history_utils as db_account_history_utils
from .database import counterparty_utils as db_counterparty_utils
from .database import transaction_typ_utils as db_transaction_typ_utils
from .database import transaction_utils as db_transaction_utils
from .date_utils import get_iso_date


logger = logging.getLogger(__name__)


class DatabaseMT940Error(Exception):
    """General exception class for database errors."""
    pass


@logg
def split_toblocks_mt940(file_content: str) -> list:
    """
    Split the file content into blocks based on the ":" character at the
    beginning of the line.

    Args:
        file_content (str): The content of the file.

    Returns:
        list: A list of blocks.
    """
    # Split after new line
    lines = file_content.split('\n')
    blocks = []
    current_block = []

    for line in lines:
        if line.startswith(':'):
            # If a block is already in current_block, add it to blocks
            if current_block:
                blocks.append(''.join(current_block))
            # Add current line to current_block to start a new block
            current_block = [line]
        # If the line does not start with ":", then it is part of the current
        # block and is added to current_block if it is not empty (only spaces)
        elif line.strip():
            current_block.append(line)

    # Add the last block
    if current_block:
        blocks.append(''.join(current_block))
    logger.debug("Bank statement successfully split into blocks.")
    return blocks


@logg
def parse_block(blocks: list) -> list:
    """Parse the blocks and extract the data.

    Args:
        blocks (list): A list of blocks.

    Returns:
        list: A list of dictionaries containing the parsed data.
    """
    parsed_data = []
    last_block_86 = False
    # Temporary variables to store data
    temp_transaction_type_number = None
    temp_transaction_type_name = None
    temp_reference = None
    temp_account_number = None
    temp_opening_balance = None
    temp_date = None
    temp_bookingdate = None
    temp_amount_type = None
    temp_amount = None
    temp_purpose_adition = None
    temp_purpose = None
    temp_counterparty_name = None
    temp_counterparty_account = None
    temp_closing_balance = None

    for block in blocks:
        transaction = {}
        # =========== Reference ===========
        if block.startswith(":20:"):
            temp_reference = block[4:]
            if last_block_86:
                last_block_86 = False
        # =========== Account Number ===========
        elif block.startswith(":25:"):
            temp_account_number = block[13:]
        # =========== Opening balance ===========
        elif block.startswith(":60F:"):
            # Opening balance of the account
            temp_opening_balance = float(block[15:].replace(',', '.'))
            if block[6] == "D":
                temp_opening_balance *= -1
        #  =========== (Booking-)Date and Amount of the transaction ===========
        elif block.startswith(":61:"):
            if last_block_86:
                last_block_86 = False
                # =========== Gathering all data ===========
                transaction['Reference'] = temp_reference
                transaction['Account'] = temp_account_number
                transaction['OpeningBalance'] = temp_opening_balance
                transaction['Date'] = temp_date
                transaction['Bookingdate'] = temp_bookingdate
                transaction['Amount'] = temp_amount
                transaction['TransactionTypeNumber'] = (
                    temp_transaction_type_number
                )
                transaction['TransactionTypeName'] = temp_transaction_type_name
                transaction['PurposeAddition'] = temp_purpose_adition
                transaction['Purpose'] = temp_purpose
                transaction['CounterpartyAccount'] = temp_counterparty_account
                transaction['CounterpartyName'] = temp_counterparty_name
                transaction['ClosingBalance'] = temp_closing_balance

                # Add the transaction to the parsed data
                parsed_data.append(transaction)
            block = block[4:]
            # =========== Date ===========
            temp_date = block[:6]
            temp_bookingdate = block[6:10]
            # =========== Amount ===========
            # 1 => +; 0 => -
            temp_amount_type = 1 if block[11:12] in ("C", "RD") else -1
            if 'CR' in block:
                amount_start = block.find('CR') + 2
            elif 'DR' in block:
                amount_start = block.find('DR') + 2
            else:
                logger.error("No amount found")
            if 'S' in block:
                amount_end_search_param = 'S'
            elif 'N' in block:
                amount_end_search_param = 'N'
            else:  # 'F'
                amount_end_search_param = 'F'
            amount_end = block.find(amount_end_search_param, amount_start)
            temp_amount = block[amount_start:amount_end].replace(',', '.')
            temp_amount = float(temp_amount) * temp_amount_type
        # =========== TransacationTyp, Purpose and Counterparty ===========
        elif block.startswith(":86:"):
            block = block[4:]
            # =========== TransactionType ===========
            temp_transaction_type_number = block[:3]
            temp_transaction_type_name = block[6:block.find('?', 6)]

            # =========== Purpose and Purposeadition ===========
            purpose_fields = []
            for i in range(20, 30):  # Geht durch die Felder von ?20 bis ?29
                field_tag = f'?{i}'
                if block.find(field_tag) != -1:
                    start = block.find(field_tag) + 3
                    next_qmark = block.find('?', start)
                    end = next_qmark if next_qmark != -1 else len(block)
                    purpose_fields.append(block[start:end])
            temp_purpose = ' '.join(purpose_fields)

            if temp_purpose.startswith("SVWZ+"):
                temp_purpose_adition = "SVWZ"
            elif temp_purpose.startswith("EREF+"):
                temp_purpose_adition = "EREF"
            elif temp_purpose.startswith("KREF+"):
                temp_purpose_adition = "KREF"
            temp_purpose = temp_purpose.replace('SVWZ+', '')
            temp_purpose = temp_purpose.replace('EREF+', '')
            temp_purpose = temp_purpose.replace('KREF+', '')

            # =========== CounterpartyAccount ===========
            cp_account_start = block.find('?31') + 3
            cp_account_end = block.find('?', cp_account_start)
            temp_counterparty_account = block[cp_account_start:cp_account_end]

            # =========== CounterpartyName ===========
            cp_name_start = block.find('?32') + 3
            cp_name_end = block.find('?', cp_name_start)
            temp_counterparty_name = block[cp_name_start:cp_name_end]

            # If the Counterparty (cp) Name is split into two parts
            if block.find('?33') != -1:
                second_start = block.find('?33') + 3
                second_end = block.find('?', second_start)
                temp_counterparty_name += " " + block[second_start:second_end]

            last_block_86 = True
        # =========== Closing balance ===========
        elif block.startswith(":62F:"):
            block = block[5:]
            closing_balance_date = block[1:7]
            closing_balance = block[10:].replace(',', '.')
            closing_balance = closing_balance[:-1]
            temp_closing_balance = (temp_account_number, closing_balance_date,
                                    closing_balance)

            # =========== Gathering all data ===========
            transaction['Reference'] = temp_reference
            transaction['Account'] = temp_account_number
            transaction['OpeningBalance'] = temp_opening_balance
            transaction['Date'] = temp_date
            transaction['Bookingdate'] = temp_bookingdate
            transaction['Amount'] = temp_amount
            transaction['TransactionTypeNumber'] = temp_transaction_type_number
            transaction['TransactionTypeName'] = temp_transaction_type_name
            transaction['PurposeAddition'] = temp_purpose_adition
            transaction['Purpose'] = temp_purpose
            transaction['CounterpartyAccount'] = temp_counterparty_account
            transaction['CounterpartyName'] = temp_counterparty_name
            transaction['ClosingBalance'] = temp_closing_balance

            # Add the transaction to the parsed data
            parsed_data.append(transaction)

            # Reset temporary variables for the next transaction
            temp_reference = None
            temp_account_number = None
            temp_opening_balance = None
            temp_date = None
            temp_bookingdate = None
            temp_amount_type = None
            temp_amount = None
            temp_purpose_adition = None
            temp_purpose = None
            temp_counterparty_name = None
            temp_closing_balance = None
    logger.debug("Bank statement successfully parsed.")
    return parsed_data


@logg
def insert_transactions(data: list, window: tk.Tk) -> None:
    """Insert the transactions into the database. Using database utils.

    Args:
        data (list): A list of dictionaries containing the transactions.
        window (tk.Tk): The main window of the application.

    Raises:
        DatabaseMT940Error: If there is an error inserting the transactions
            into the database.
    """
    closing_balance = []
    skipped_last_transaction = False
    number_skipped_transactions = 0
    for entry in data:
        # temp: not ready for the database
        # rti: ready to insert
        temp_account_number = entry['Account']
        try:
            rti_account_id = db_account_utils.get_account_id(
                data=[None, temp_account_number, None, None],
                supplied_data=[False, True, False, False]
            )
        except db_account_utils.NoAccountFoundError:
            logger.warning(
                f"Account {temp_account_number} not found in database."
            )
            db_account_utils.add_account_mt940(
                master=window,
                number=temp_account_number, balance=entry['OpeningBalance']
            )
            rti_account_id = db_account_utils.get_account_id(
                data=[None, temp_account_number, None, None],
                supplied_data=[False, True, False, False]
            )
        temp_date = entry['Date']
        rti_date = get_iso_date(temp_date)
        temp_bookingdate = rti_date[:2] + entry['Bookingdate']
        rti_bookingdate = get_iso_date(temp_bookingdate)
        temp_tt_number = entry['TransactionTypeNumber']
        temp_tt_name = entry['TransactionTypeName']
        try:
            rti_tt_id = db_transaction_typ_utils.get_transaction_typ_id(
                data=[temp_tt_name, temp_tt_number],
                supplied_data=[True, True]
            )
        except db_transaction_typ_utils.Error:
            logger.warning(
                f"Transaction type {temp_tt_name} not found in database."
            )
            db_transaction_typ_utils.add_transaction_typ(
                name=temp_tt_name, number=temp_tt_number
            )
            rti_tt_id = db_transaction_typ_utils.get_transaction_typ_id(
                data=[temp_tt_name, temp_tt_number],
                supplied_data=[True, True]
            )
        rti_amount = entry['Amount']
        rti_purpose = entry['Purpose']
        temp_counterparty_number = entry['CounterpartyAccount']
        temp_counterparty_name = entry['CounterpartyAccount']
        try:
            rti_counterparty_id = db_counterparty_utils.get_counterparty_id(
                data=[temp_counterparty_name, temp_counterparty_number],
                supplied_data=[True, True]
            )
        except db_counterparty_utils.Error:
            logger.warning(
                f"Counterparty {temp_counterparty_name} not found in "
                "database."
            )
            db_counterparty_utils.add_counterparty(
                name=temp_counterparty_name, number=temp_counterparty_number
            )
            rti_counterparty_id = db_counterparty_utils.get_counterparty_id(
                data=[temp_counterparty_name, temp_counterparty_number],
                supplied_data=[True, True]
            )
        rti_category_id = 1  # Default category
        rti_user_comments = None  # No user comments
        rti_displayed_name = None  # No displayed name
        # Add the closing balance to the list
        if entry['ClosingBalance'] is not None:
            closing_balance.append(entry['ClosingBalance'])

        rti_data = (rti_account_id, rti_date, rti_bookingdate, rti_tt_id,
                    rti_amount, rti_purpose, rti_counterparty_id,
                    rti_category_id, rti_user_comments, rti_displayed_name)
        try:
            db_transaction_utils.add_transaction(
                data=rti_data
            )
            if skipped_last_transaction:
                logger.debug(f"Skipped {number_skipped_transactions} "
                             "transactions because they were already "
                             "in the database.")
                skipped_last_transaction = False
                number_skipped_transactions = 0
        except db_transaction_utils.AlreadyExistsError:
            number_skipped_transactions += 1
            skipped_last_transaction = True
        except db_transaction_utils.Error:
            if skipped_last_transaction:
                logger.debug(f"Skipped {number_skipped_transactions} "
                             "transactions because they were already "
                             "in the database.")
                skipped_last_transaction = False
                number_skipped_transactions = 0
            logger.error("Error inserting transaction.")
            raise DatabaseMT940Error("Error inserting transaction.")

    # If the last transaction was skipped, log the number of skipped
    # transactions
    if skipped_last_transaction:
        logger.debug(f"Skipped {number_skipped_transactions} "
                     "transactions because they were already "
                     "in the database.")
        skipped_last_transaction = False
        number_skipped_transactions = 0
    logger.debug("Transactions successfully inserted to database.")

    # Add the closing balance to the database
    latest = {}
    rti_account_id = None
    today = get_iso_date(today=True)
    skipped_last_ac_his_entry = False
    number_skipped_ac_his_entrys = 0
    for (account_number, record_date, balance) in closing_balance:
        try:
            rti_account_id = db_account_utils.get_account_id(
                data=[None, account_number, None, None],
                supplied_data=[False, True, False, False]
            )
        except db_account_utils.NoAccountFoundError:
            logger.warning(
                f"Account {account_number} not found in database."
            )
            raise DatabaseMT940Error(
                f"Account {account_number} not found in database."
                " Even though it was in the MT940 file."
                " And should therefore be in the database."
            )
        balance = float(balance)
        if account_number not in latest:
            latest[account_number] = (record_date, balance, rti_account_id)
        elif record_date > latest[account_number][0]:
            latest[account_number] = (record_date, balance, rti_account_id)
        try:
            db_account_history_utils.add_account_history(
                account_id=rti_account_id,
                balance=balance, record_date=get_iso_date(record_date),
                change_date=today
            )
            logger.info(
                f"Account history for {account_number} "
                f"added with date: {record_date} and balance: {balance}"
            )
            if skipped_last_ac_his_entry:
                logger.debug(
                    f"Skipped {number_skipped_ac_his_entrys} "
                    "account history entries because they were already "
                    "in the database."
                )
                skipped_last_ac_his_entry = False
                number_skipped_ac_his_entrys = 0
        except db_account_history_utils.ExistingAccountHistoryError:
            number_skipped_ac_his_entrys += 1
            skipped_last_ac_his_entry = True

    # If the last account history entry was skipped, log the number of
    # skipped account history entries
    if skipped_last_ac_his_entry:
        logger.debug(
            f"Skipped {number_skipped_ac_his_entrys} "
            "account history entries because they were already "
            "in the database."
        )
        skipped_last_ac_his_entry = False
        number_skipped_ac_his_entrys = 0

    for account_number, (record_date, balance,
                         rti_account_id) in latest.items():
        try:
            last_balance = db_account_history_utils.get_last_balance(
                account_id=rti_account_id
            )
        except db_account_history_utils.NoAccountHistoryFoundError:
            logger.debug(
                "No balance found within the previous year."
            )
            last_balance = 0.0
        logger.debug(
            f"Last balance: {last_balance} and new balance: {balance}")
        difference = float(balance) - float(last_balance)
        logger.debug(
            f"Difference between last balance and new balance: {difference}"
        )
        try:
            db_account_utils.update_account(
                account_id=rti_account_id,
                new_values=["", "", "", balance, difference,
                            get_iso_date(record_date), today]
            )
            logger.info(
                f"Account {account_number} updated with new balance: {balance}"
            )
        except db_account_utils.NoAccountFoundError:
            logger.warning(
                f"Account {account_number} not found in database."
            )
            raise DatabaseMT940Error(
                f"Account {account_number} not found in database.",
                " Even though it was in the MT940 file.",
                " And should therefore be in the database."
            )
        except db_account_utils.NoChangesDetectedError:
            logger.debug(
                f"Account {account_number} already has the same values. "
                "Skipping..."
            )
    logger.debug("Account history successfully inserted to database.")
    logger.debug("Bank statement successfully inserted to database.")


@logg
def import_mt940_file(master: tk.Tk) -> None:
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
        blocks = split_toblocks_mt940(file_content)
        parsed_data = parse_block(blocks)
        insert_transactions(parsed_data, master)
        logger.info("Imported bank statment successfully.")
        master.reload()
    else:
        logger.info("No file selected.")
