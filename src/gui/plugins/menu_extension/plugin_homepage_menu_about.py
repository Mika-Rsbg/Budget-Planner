import tkinter as tk

menu_id = 1000


def add_to_menu(window, menu_bar):
    about_menu = tk.Menu(menu_bar, tearoff=0)
    about_menu.add_command(label="Über Homepage", command=lambda:
                           window.show_message("Feature in Arbeit."))

    about_menu.add_command(label="Reload", command=lambda:
                           window.reload())

    menu_bar.add_cascade(label="Info", menu=about_menu)
