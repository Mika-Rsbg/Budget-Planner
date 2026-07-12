from typing import List, Tuple
from decimal import Decimal
import logging
from models.transaction.imported import ImportedTransaction
from core.logging.logging_tools import log_fn


logger = logging.getLogger(__name__)


@log_fn
def split_toblocks(file_content: str) -> List[str]:
    """
    Split the file content into blocks based on the ":" character at the
    beginning of the line.

    Args:
        file_content (str): The content of the file.

    Returns:
        List: A List of blocks.
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


@log_fn
def pars_block(
        blocks: List[str]
        ) -> List[ImportedTransaction]:
    """Parse a List of "blocks" (aka a Line from the .txt) from a mt940 file.

    Args:
        blocks (List[str]): A List of strings containing all the information
            from the Transactions

    Returns:
        List: A List of ImportedTransaction objects containing the parsed data.
    """
    parsed_data: List[ImportedTransaction] = []
    number_parsed_transactions: int = 0
    last_block_86: bool = False

    # Temporary variables to store data
    temp_transaction_type_number: str = ""
    temp_transaction_type_name: str = ""
    temp_reference: str = ""
    temp_account_number: str = ""
    temp_opening_balance: Decimal = Decimal(0)
    temp_date: str = ""
    temp_booking_date: str = ""
    temp_amount_type: int
    temp_currency: str = ""
    temp_amount: Decimal = Decimal(0)
    temp_purpose_addition: str = ""
    temp_purpose: str = ""
    temp_counterparty_name: str = ""
    temp_counterparty_account: str = ""
    temp_closing_balance: Tuple[str, str, str] = ("", "", "")

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
            temp_opening_balance = Decimal(block[15:].replace(',', '.'))
            if block[6] == "D":
                temp_opening_balance *= -1
        #  =========== (Booking-)Date and Amount of the transaction ===========
        elif block.startswith(":61:"):
            if last_block_86:
                last_block_86 = False
                # =========== Gathering all data ===========
                transaction = ImportedTransaction(
                    reference=temp_reference,
                    account_number=temp_account_number,
                    opening_balance=temp_opening_balance,
                    closing_balance=temp_closing_balance,
                    date=temp_date,
                    booking_date=temp_booking_date,
                    currency=temp_currency,
                    amount=temp_amount,
                    transaction_type_number=temp_transaction_type_number,
                    transaction_type_name=temp_transaction_type_name,
                    purpose_addition=temp_purpose_addition,
                    purpose=temp_purpose,
                    counterparty_account_number=temp_counterparty_account,
                    counterparty_name=temp_counterparty_name,
                )

                # Add the transaction to the parsed data
                parsed_data.append(transaction)
                number_parsed_transactions += 1
            block = block[4:]
            # =========== Date ===========
            temp_date = block[:6]
            temp_booking_date = block[6:10]
            # =========== Amount-Type (+/-) ===========
            # 1 => +; 0 => -
            temp_amount_type = (1 if block[10] == 'C' or
                                block[10:12] == 'RD' else -1)
            # =========== Currency ===========
            if block[10:12] == "RC" or block[10:12] == "RD":
                currency_position = 12
            else:  # "C" or "D"
                currency_position = 11
            temp_currency = block[currency_position]
            # =========== Amount ===========
            # Find the start of the amount by searching for the
            # first digit after position 11
            amount_start = None
            for idx, char in enumerate(block[11:], start=11):
                if char.isdigit():
                    amount_start = idx
                    break
            if amount_start is None:
                logger.error("No amount found")
            if 'S' in block:
                amount_end_search_param = 'S'
            elif 'N' in block:
                amount_end_search_param = 'N'
            else:  # 'F'
                amount_end_search_param = 'F'
            amount_end = block.find(amount_end_search_param, amount_start)
            temp_amount_str = block[amount_start:amount_end].replace(',', '.')
            temp_amount = Decimal(temp_amount_str) * temp_amount_type
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
                temp_purpose_addition = "SVWZ"
            elif temp_purpose.startswith("EREF+"):
                temp_purpose_addition = "EREF"
            elif temp_purpose.startswith("KREF+"):
                temp_purpose_addition = "KREF"
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
            transaction = ImportedTransaction(
                reference=temp_reference,
                account_number=temp_account_number,
                opening_balance=temp_opening_balance,
                closing_balance=temp_closing_balance,
                date=temp_date,
                booking_date=temp_booking_date,
                currency=temp_currency,
                amount=temp_amount,
                transaction_type_number=temp_transaction_type_number,
                transaction_type_name=temp_transaction_type_name,
                purpose_addition=temp_purpose_addition,
                purpose=temp_purpose,
                counterparty_account_number=temp_counterparty_account,
                counterparty_name=temp_counterparty_name,
            )

            # Add the transaction to the parsed data
            parsed_data.append(transaction)
            number_parsed_transactions += 1

            # Reset temporary variables for the next transaction
            temp_reference = ""
            temp_account_number = ""
            temp_opening_balance = Decimal(0)
            temp_date = ""
            temp_booking_date = ""
            temp_amount_type = 0
            temp_amount = Decimal(0)
            temp_purpose_addition = ""
            temp_purpose = ""
            temp_counterparty_name = ""
            temp_closing_balance = ("", "", "")

    logger.debug("Parsed %d transactions.", number_parsed_transactions)
    logger.debug("Bank statement successfully parsed.")
    return parsed_data


def pars_file(
        file_content: str
        ) -> List[ImportedTransaction]:
    split_content = split_toblocks(file_content)
    parsed_content = pars_block(split_content)
    return parsed_content
