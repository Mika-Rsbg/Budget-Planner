import tkinter as tk
from gui.basewindow import BaseWindow

menu_id = 40


def add_to_menu(window: BaseWindow, menu_bar):
    data_menu = tk.Menu(menu_bar, tearoff=0)

    menu_bar.add_cascade(label="Test", menu=data_menu)
