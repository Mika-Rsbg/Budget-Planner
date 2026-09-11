from dataclasses import dataclass
from typing import Any, Callable

from shared.date_utils import format_mt940_date
from shared.currency_utils import format_mt940_currency


@dataclass(frozen=True)
class TableColumn:
    attribute: str
    header: str
    formatter: Callable[[Any], Any] | None = None


TRANSACTION_TABLE_COLUMNS = [
    TableColumn("import_id", "ID"),
    TableColumn("date", "Datum", format_mt940_date),
    TableColumn("booking_date", "Buchungsdatum", format_mt940_date),
    TableColumn("amount", "Betrag", format_mt940_currency),
    TableColumn("transaction_type_name", "Transaktionstyp"),
    TableColumn("purpose", "Verwendungszweck"),
    TableColumn("counterparty_account_number", "Kontonummer"),
    TableColumn("counterparty_name", "Name"),
    TableColumn("opening_balance", "Eröffnungssaldo", format_mt940_currency),
    TableColumn("category_id", "Kategorie ID"),
]
