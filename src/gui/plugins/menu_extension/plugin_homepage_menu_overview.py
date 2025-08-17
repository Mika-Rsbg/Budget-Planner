import tkinter as tk
from gui.overview.in_out.inout_overview_page import InOutOverviewPage

menu_id = 25


def add_to_menu(window, menu_bar):
    overview_menu = tk.Menu(menu_bar, tearoff=0)

    # Eingaben und Ausgaben
    overview_menu.add_command(
        label="Eingaben und Ausgaben (WIP)",
        command=lambda: open_inout_overview_page
        (window)
    )

    # Konto Historie
    overview_menu.add_command(
        label="Konto Historie (WIP)",
        command=lambda: window.show_message(
            "WIP."
        )
    )

    overview_menu.add_separator()

    # # Transaktion bearbeiten
    # overview_menu.add_command(
    #     label="Transaktion bearbeiten (WIP)",
    #     command=lambda: open_transaction_page_1(window, 1)
    # )

    # # Transaktion löschen
    # overview_menu.add_command(
    #     label="Transaktion löschen (WIP)",
    #     command=lambda: open_transaction_page_1(window, 2)
    # )

    # overview_menu.add_separator()

    # # Übersicht anzeigen
    # overview_menu.add_command(
    #     label="Transaktionsübersicht (WIP)",
    #     command=lambda: window.show_message(
    #         "Hier sind alle Transaktionen aufgelistet."
    #     )
    # )

    # Menü zur Menüleiste hinzufügen
    menu_bar.add_cascade(label="Übersicht", menu=overview_menu)


def open_inout_overview_page(window) -> None:
    """Open the InOutOverviewPage.

    Args:
        window: parent window
    """
    InOutOverviewPage(parent=window)


def open_transaction_page_1(window, opening_mode: int) -> None:
    """Open the transaction page.

    Args:
        window: parent window
        opening_mode (int): 0 = add, 1 = edit, 2 = delete
    """
    # TransactionPage(window, opening_mode)
    window.show_message(
        "Feature not implemented yet!"
    )


def open_transaction_page(window) -> None:
    """Open the transaction page.

    Args:
        window: parent window
        opening_mode (int): 0 = add, 1 = edit, 2 = delete
    """
    pass
