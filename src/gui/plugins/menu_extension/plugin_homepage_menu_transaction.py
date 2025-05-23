import tkinter as tk
# from gui.transactionpage.transactionpage import TransactionPage
from utils.data.mt940import_utils import import_mt940_file

menu_id = 20


def add_to_menu(window, menu_bar):
    transaction_menu = tk.Menu(menu_bar, tearoff=0)

    # Transaktion manuell hinzufügen
    transaction_menu.add_command(
        label="Manuelle Transaktion hinzufügen",
        command=lambda: open_transaction_page(window, 0)
    )

    # Transaktion aus Datei importieren
    transaction_menu.add_command(
        label="Transaktionen aus MT940-Datei importieren",
        command=lambda: import_mt940_file(window)
    )

    transaction_menu.add_separator()

    # Transaktion bearbeiten
    transaction_menu.add_command(
        label="Transaktion bearbeiten",
        command=lambda: open_transaction_page(window, 1)
    )

    # Transaktion löschen
    transaction_menu.add_command(
        label="Transaktion löschen",
        command=lambda: open_transaction_page(window, 2)
    )

    transaction_menu.add_separator()

    # Übersicht anzeigen
    transaction_menu.add_command(
        label="Transaktionsübersicht",
        command=lambda: window.show_message(
            "Hier sind alle Transaktionen aufgelistet."
        )
    )

    # Menü zur Menüleiste hinzufügen
    menu_bar.add_cascade(label="Transaktionen", menu=transaction_menu)


def open_transaction_page(window, opening_mode: int) -> None:
    """Open the transaction page.

    Args:
        window: parent window
        opening_mode (int): 0 = add, 1 = edit, 2 = delete
    """
    # TransactionPage(window, opening_mode)
    window.show_message(
        "Feature not implemented yet!"
    )
