import tkinter as tk
from gui.basewindow import BaseWindow
from gui.cashpage.cashpage import CashPage

menu_id = 1


def add_to_menu(window, menu_bar):
    account_menu = tk.Menu(menu_bar, tearoff=0)

    # Konto hinzufügen
    account_menu.add_command(label="Cash Page", command=lambda:
                             open_cash_page(window))

    account_menu.add_separator()  # Noch eine Trennlinie

    # Transaktion hinzufügen
    account_menu.add_command(label="Transaktion hinzufügen", command=lambda:
                             window.show_message
                             ("Feature in Arbeit."))

    # Übersicht anzeigen
    account_menu.add_command(label="Kontenübersicht", command=lambda:
                             window.show_message
                             ("Feature in Arbeit."))

    # Menü zur Menüleiste hinzufügen
    menu_bar.add_cascade(label="Bargeld", menu=account_menu)


def open_cash_page(window: BaseWindow) -> None:
    """Open the account page.

    Args:
        window: parent window
        account_selection_needed (bool)
    """
    cash_page = CashPage(window)
    window.withdraw()  # Hide the parent window
    window.wait_window(cash_page)
    window.deiconify()  # Show the parent window again
    window.reload()  # Reload the parent window to refresh the UI
