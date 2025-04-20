import tkinter as tk
from gui.accountpage.accountpage import AccountPage

menu_id = 1


def add_to_menu(window, menu_bar):
    account_menu = tk.Menu(menu_bar, tearoff=0)

    # Konto hinzufügen
    account_menu.add_command(label="Konto hinzufügen", command=lambda:
                             open_account_page(window, False))

    # Konto bearbeiten
    account_menu.add_command(label="Konto bearbeiten", command=lambda:
                             open_account_page(window, True))

    # Konto löschen
    account_menu.add_command(label="Konto löschen", command=lambda:
                             open_account_page(window, True))

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
    menu_bar.add_cascade(label="Konto", menu=account_menu)


def open_account_page(window, account_selection_needed: bool) -> None:
    """Open the account page.

    Args:
        window: parent window
        account_selection_needed (bool)
    """
    AccountPage(window, account_selection_needed)
