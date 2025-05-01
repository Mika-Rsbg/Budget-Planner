# plugins/menu_extension/plugin_all_menu_help.py
import tkinter as tk


def add_to_menu(window, menu_bar):
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Hilfe", command=lambda:
                          window.show_message("Dies ist die globale Hilfe."))
    menu_bar.add_cascade(label="Hilfe", menu=help_menu)
