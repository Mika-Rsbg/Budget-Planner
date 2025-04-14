# plugins/plugin_homepage_menu_about.py
import tkinter as tk


def add_to_menu(window, menu_bar):
    about_menu = tk.Menu(menu_bar, tearoff=0)
    about_menu.add_command(label="Über Homepage", command=lambda:
                           window.show_message("Dies ist die Startseite."))
    menu_bar.add_cascade(label="Info", menu=about_menu)
