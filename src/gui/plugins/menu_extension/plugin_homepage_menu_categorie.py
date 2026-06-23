import tkinter as tk
from gui.pages.category.categoriepage import CategoryPage
from gui.app.basewindow import BaseWindow

menu_id = 15


def add_to_menu(window, menu_bar):
    account_menu = tk.Menu(menu_bar, tearoff=0)

    # open Category Page
    account_menu.add_command(label="Kategorie Fenster (Beta)", command=lambda:
                             open_category_page(window))

    # Menü zur Menüleiste hinzufügen
    menu_bar.add_cascade(label="Kategorie", menu=account_menu)


def open_category_page(window: BaseWindow) -> None:
    """Open the category page.

    Args:
        window: parent window
        account_selection_needed (bool)
    """
    CategoryPage(window, "test")
