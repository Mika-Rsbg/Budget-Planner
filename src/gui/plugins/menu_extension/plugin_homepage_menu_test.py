import tkinter as tk
from gui.accountpage.reorder_account_widgets_page import (
    ReorderAccountWidgetsWindow,
)
from gui.basewindow import BaseWindow

menu_id = 4


def add_to_menu(window: BaseWindow, menu_bar):
    data_menu = tk.Menu(menu_bar, tearoff=0)

    # Datenbank erstellen
    data_menu.add_command(label="Widgets neu anordnen",
                          command=lambda: test_reorder_page(window))

    # Menü zur Menüleiste hinzufügen
    menu_bar.add_cascade(label="Test", menu=data_menu)


def test_reorder_page(window: BaseWindow) -> None:
    """
    Tests the ReorderAccountWidgetsWindow by creating an instance of it.
    This function is intended for testing purposes only and should not be
    used in release code.
    """
    app = ReorderAccountWidgetsWindow(master=window)
    window.wait_window(app)
    window.reload()
