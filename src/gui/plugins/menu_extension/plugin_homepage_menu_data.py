import tkinter as tk
import utils.data.createdatabase_utils as db_utils
from gui.basewindow import BaseWindow

menu_id = 3


def add_to_menu(window: BaseWindow, menu_bar):
    data_menu = tk.Menu(menu_bar, tearoff=0)

    # Datenbank erstellen
    data_menu.add_command(label="Datenbank erstellen",
                          command=lambda: create_database(window))

    # Datenbank löschen
    data_menu.add_command(label="Datenbank löschen",
                          command=lambda: delete_database(window))

    # Menü zur Menüleiste hinzufügen
    menu_bar.add_cascade(label="Datenbank", menu=data_menu)


def create_database(window: BaseWindow) -> None:
    """
    Deletes the database and reloads the window.

    Args:
        window (tk.Tk): The main window of the application.
    """
    db_utils.create_database()
    window.reload()


def delete_database(window: BaseWindow) -> None:
    """
    Deletes the database file.
    """
    window.ask_permission(
        message="Möchten Sie die Datenbank wirklich löschen?",
        focus_on=[True, False]
    )
    permission = window.permission
    if permission:
        try:
            db_utils.delete_database()
        except db_utils.Error as e:
            print(f"Fehler beim Löschen der Datenbank: {e}")
    else:
        print("Datenbank wurde nicht gelöscht.")
