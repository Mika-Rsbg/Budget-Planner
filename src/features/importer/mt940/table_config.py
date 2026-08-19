from dataclasses import dataclass
from typing import Any, Callable

from shared.date_utils import format_mt940_date


@dataclass(frozen=True)
class TableColumn:
    attribute: str
    header: str
    formatter: Callable[[Any], Any] | None = None


TRANSACTION_TABLE_COLUMNS = [
    TableColumn("date", "Datum", format_mt940_date),
    TableColumn("booking_date", "Buchungsdatum", format_mt940_date),
    TableColumn("amount", "Betrag"),
    TableColumn("transaction_type_name", "Transaktionstyp"),
    TableColumn("purpose", "Verwendungszweck"),
    TableColumn("counterparty_account_number", "Kontonummer"),
    TableColumn("counterparty_name", "Name"),
    TableColumn("opening_balance", "Eröffnungssaldo"),
    TableColumn("category_id", "Kategorie ID"),
]
