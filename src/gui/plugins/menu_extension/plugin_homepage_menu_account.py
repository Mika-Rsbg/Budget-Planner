import tkinter as tk
from gui.accountpage.accountpage import AccountPage
from gui.accountpage.reorder_account_widgets_page import (
    ReorderAccountWidgetsWindow,
)
from gui.basewindow import BaseWindow

menu_id = 10


def add_to_menu(window, menu_bar):
    account_menu = tk.Menu(menu_bar, tearoff=0)

    # Konto hinzufügen
    account_menu.add_command(label="Konto hinzufügen (Beta)", command=lambda:
                             open_account_page(window, False))

    # Konto bearbeiten
    account_menu.add_command(label="Konto bearbeiten (Beta)", command=lambda:
                             open_account_page(window, True))

    # Konto löschen
    account_menu.add_command(label="Konto löschen (Beta)", command=lambda:
                             open_account_page(window, True))

    account_menu.add_separator()

    account_menu.add_command(label="Widgets neu anordnen",
                             command=lambda: reorder_account_widgets(window))

    account_menu.add_separator()

    # Übersicht anzeigen
    account_menu.add_command(label="Kontenübersicht(WIP)", command=lambda:
                             window.show_message
                             ("Feature in Arbeit."))

    # Menü zur Menüleiste hinzufügen
    menu_bar.add_cascade(label="Konto", menu=account_menu)


def open_account_page(window, account_selection_needed: bool) -> None:
    """Open the account page.

    Args:
        window: parent window
        account_selection_needed (bool)
    """
    AccountPage(window, account_selection_needed)


def reorder_account_widgets(window: BaseWindow) -> None:
    """
    Tests the ReorderAccountWidgetsWindow by creating an instance of it.
    This function is intended for testing purposes only and should not be
    used in release code.
    """
    app = ReorderAccountWidgetsWindow(master=window)
    window.wait_window(app)
    window.reload()
