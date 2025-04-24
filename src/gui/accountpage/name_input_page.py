import tkinter as tk
from tkinter import ttk
from gui.basetoplevelwindow import BaseToplevelWindow


class NameInputDialog(BaseToplevelWindow):
    def __init__(self, master: tk.Tk = None, number: str = None):
        self.number = number
        super().__init__(master, title="Name eingeben", geometry="250x200")
        self.name = None

    def init_ui(self):
        if self.number is not None:
            self.number_label = ttk.Label(self.main_frame,
                                          text=f"Nummer: {self.number}")
        else:
            self.number_label = ttk.Label(self.main_frame,
                                          text="Konto Nummer (IBAN):")
        self.number_label.pack(pady=(10, 0))

        self.label = ttk.Label(self.main_frame, text="Name:")
        self.label.pack(pady=(10, 0))

        self.entry = ttk.Entry(self.main_frame)
        self.entry.pack(pady=5)
        self.entry.focus()

        self.button = ttk.Button(self.main_frame, text="OK",
                                 command=self.on_ok)
        self.button.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.bind("<Return>", lambda event: self.on_ok())

        # Set the default focus to the entry widget
        self.entry.focus_set()

    def validate_name_input(self):
        name = self.entry.get().strip()
        if not name:
            self.label.config(text="Bitte einen Namen eingeben!",
                              foreground="red")
            return None
        self.label.config(text="Name:", foreground="black")
        print(f"Name: {name}")
        return name

    def on_ok(self):
        self.name = self.validate_name_input()
        if self.name is None:
            return
        self.destroy()
        # self.destroy()

    def on_cancel(self):
        self.name = None
        self.destroy()
