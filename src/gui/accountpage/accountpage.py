# import tkinter as tk
from tkinter import ttk
from gui.basetoplevelwindow import BaseToplevelWindow


class AccountPage(BaseToplevelWindow):
    def __init__(self, parent, account_id: int = None) -> None:
        super().__init__(parent, title="Budget Planner - Konto")

    def init_ui(self):
        """
        Erzeuge Widgets und Layout für die Account Page.
        """
        self.heading_label = ttk.Label(
            self.main_frame,
            text="Konto Fenster",
            font=("Helvetica", 35),
            padding=10
            )
        self.heading_label.grid(row=0, column=0, sticky="nsew")
