import logging
import tkinter as tk
from tkinter import ttk
from gui.basetoplevelwindow import BaseToplevelWindow


logger = logging.getLogger(__name__)


class TransactionPage(BaseToplevelWindow):
    def __init__(self, master=None, plugin_scope=None,
                 title="Transaction Page",
                 geometry="800x600", bg_color="white"):
        super().__init__(master, plugin_scope, title, geometry, bg_color)
        self.init_ui()

    def init_ui(self) -> None:
        # ======= Account Information =======
        self.account_infomation_frame = tk.LabelFrame(
            self.main_frame, text="Account Informationen",
            background=self.bg_color, foreground="black",
        )
        self.account_infomation_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew"
        )

        # === Acount Name ===
        self.account_name_label = tk.Label(
            self.account_infomation_frame, text="Account Name:",
            background=self.bg_color, foreground="black"
        )
        self.account_name_label.grid(row=0, column=0)  # , sticky="nsew")
        self.account_name_dropdown = tk.OptionMenu(
            self.account_infomation_frame,
            tk.StringVar(value="Select Account"),
            "Account 1", "Account 2", "Account 3"
        )
        self.account_name_dropdown.config(bg=self.bg_color, fg="black")
        self.account_name_dropdown["menu"].config(bg=self.bg_color, fg="black")
        self.account_name_dropdown.grid(row=0, column=1, sticky="ew")

        # === Padding ===
        for widget in self.account_infomation_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)

        # ======= Transaction Information =======
        self.transaction_information_frame = tk.LabelFrame(
            self.main_frame, text="Transaction Informationen",
            background=self.bg_color, foreground="black"
        )
        self.transaction_information_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsew"
        )

        # === Date ===
        self.date_label = tk.Label(
            self.transaction_information_frame, text="Datum:",
            background=self.bg_color, foreground="black"
        )
        self.date_label.grid(row=0, column=0)
        self.date_entry = tk.Entry(
            self.transaction_information_frame, background=self.bg_color,
            foreground="black")
        self.date_entry.grid(row=0, column=1, sticky="ew")
        self.date_warning_label = tk.Label(
            self.transaction_information_frame, text="",
            background=self.bg_color, foreground="red"
        )
        self.date_warning_label.grid(row=1, column=0, columnspan=2)
        # ========================= Transaction Type is always "manual"
        # === Amount ===
        self.amount_label = tk.Label(
            self.transaction_information_frame, text="Betrag:",
            background=self.bg_color, foreground="black"
        )
        self.amount_label.grid(row=2, column=0)
        self.amount_entry = tk.Entry(
            self.transaction_information_frame, background=self.bg_color,
            foreground="black")
        self.amount_entry.grid(row=2, column=1, sticky="ew")
        self.amount_warning_label = tk.Label(
            self.transaction_information_frame, text="",
            background=self.bg_color, foreground="red"
        )
        self.amount_warning_label.grid(row=3, column=0, columnspan=2)
        # === Purpose ===
        self.purpose_label = tk.Label(
            self.transaction_information_frame, text="Beschreibung:",
            background=self.bg_color, foreground="black", cursor="xterm"
        )
        self.purpose_label.grid(row=4, column=0)
        self.purpose_entry = tk.Entry(
            self.transaction_information_frame, background=self.bg_color,
            foreground="black")
        self.purpose_entry.grid(row=4, column=1, sticky="ew")
        self.purpose_warning_label = tk.Label(
            self.transaction_information_frame, text="",
            background=self.bg_color, foreground="red"
        )
        self.purpose_warning_label.grid(row=5, column=0, columnspan=2)
        # === Counterparty ===
        self.counterparty_label = tk.Label(
            self.transaction_information_frame, text="Gegenpartei:",
            background=self.bg_color, foreground="black"
        )
        self.counterparty_label.grid(row=6, column=0)
        values = ["Gegenpartei 1", "Gegenpartei 2", "Gegenpartei 3"]
        self.counterparty_var = tk.StringVar()
        self.counterparty_combo = ttk.Combobox(
            self.transaction_information_frame,
            textvariable=self.counterparty_var,
            values=values,
            state="normal"
        )
        self.counterparty_combo.grid(row=6, column=1, sticky="ew")

        def filter_counterparties(event):
            entered = self.counterparty_var.get().lower()
            filtered = [v for v in values if entered in v.lower()]
            self.counterparty_combo['values'] = (filtered if filtered
                                                 else values)

        self.counterparty_combo.bind('<KeyRelease>', filter_counterparties)

        # === Counterparty Name (read-only) ===
        self.counterparty_name_label = tk.Label(
            self.transaction_information_frame, text="Gegenpartei Name:",
            background=self.bg_color, foreground="black"
        )
        self.counterparty_name_label.grid(row=7, column=0)
        self.counterparty_name_entry = tk.Entry(
            self.transaction_information_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.counterparty_name_entry.grid(row=7, column=1, sticky="ew")

        # === Counterparty Account (read-only) ===
        self.counterparty_account_label = tk.Label(
            self.transaction_information_frame, text="Gegenpartei Konto:",
            background=self.bg_color, foreground="black"
        )
        self.counterparty_account_label.grid(row=8, column=0)
        self.counterparty_account_entry = tk.Entry(
            self.transaction_information_frame, state="readonly",
            background="gray", foreground="black"
        )
        self.counterparty_account_entry.grid(row=8, column=1, sticky="ew")

        # === Padding ===
        for widget in self.transaction_information_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)
