import tkinter as tk
from gui.accountpage.accountpage import AccountPage

menu_id = 1


def add_to_menu(window, menu_bar):
    account_menu = tk.Menu(menu_bar, tearoff=0)

    # Konto hinzufügen
    account_menu.add_command(label="Konto hinzufügen", command=lambda:
                             open_account_page(window, 0))

    # Konto bearbeiten
    account_menu.add_command(label="Konto bearbeiten", command=lambda:
                             window.show_message("Konto wurde bearbeitet."))

    # Konto löschen
    account_menu.add_command(label="Konto löschen", command=lambda:
                             window.show_message("Konto wurde gelöscht."))

    account_menu.add_separator()  # Noch eine Trennlinie

    # Transaktion hinzufügen
    account_menu.add_command(label="Transaktion hinzufügen", command=lambda:
                             window.show_message
                             ("Transaktion wurde hinzugefügt."))

    # Übersicht anzeigen
    account_menu.add_command(label="Kontenübersicht", command=lambda:
                             window.show_message
                             ("Hier sind alle Konten aufgelistet."))

    # Menü zur Menüleiste hinzufügen
    menu_bar.add_cascade(label="Konto", menu=account_menu)


def open_account_page(window, opening_mode: int) -> None:
    """Open the account page.

    Args:
        window: parent window
        opening_mode (int): 0 = add, 1 = edit, 2 = delete
    """
    AccountPage(window)
