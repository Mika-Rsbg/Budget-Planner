import tkinter as tk
from gui.app.basewindow import BaseWindow
from gui.pages.transaction.import_overview import ImportOverview

menu_id = 5


def add_to_menu(window: BaseWindow, menu_bar):
    transaction_menu = tk.Menu(menu_bar, tearoff=0)

    # Transaktion manuell hinzufügen
    transaction_menu.add_command(
        label="Manuelle Transaktion hinzufügen (WIP)"
    )

    # Transaktion aus Datei importieren
    transaction_menu.add_command(
        label="Transaktionen aus MT940-Datei importieren",
        command=lambda: open_transaction_page(window)
    )

    transaction_menu.add_separator()

    # Transaktion bearbeiten
    transaction_menu.add_command(
        label="Transaktion bearbeiten (WIP)"
    )

    # Transaktion löschen
    transaction_menu.add_command(
        label="Transaktion löschen (WIP)"
    )

    transaction_menu.add_separator()

    # Übersicht anzeigen
    transaction_menu.add_command(
        label="Transaktionsübersicht (WIP)",
        command=lambda: window.show_message(
            "Hier sind alle Transaktionen aufgelistet."
        )
    )

    # Menü zur Menüleiste hinzufügen
    menu_bar.add_cascade(label="Transaktionen", menu=transaction_menu)


def open_transaction_page(window) -> None:
    """Open the transaction page.

    Args:
        window: parent window
    """
    ImportOverview(parent=window)
