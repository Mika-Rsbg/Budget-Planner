import logging
import tkinter as tk
from tkinter import ttk
from typing import List, Union, cast
from gui.basetoplevelwindow import BaseToplevelWindow
from utils.data.database.account_utils import get_account_data
from utils.data.database.counterparty_utils import get_counterparty_data
from utils.data.database.category_utils import get_category_data


logger = logging.getLogger(__name__)


class TransactionPage(BaseToplevelWindow):
    def __init__(self, master=None, plugin_scope=None,
                 title="Transaction Page",
                 geometry="500x600", bg_color="white"):
        self.frames: List[Union[tk.LabelFrame, tk.Frame]] = []
        self.account_data = get_account_data(
            selected_columns=[True, False, True, True, True,
                              False, False, False]
        )
        """List[Tuple[int, str, str, float]]"""
        self.counterparty_data = get_counterparty_data()
        """List[Tuple[int, str, str]]"""
        self.category_data = get_category_data(
            selected_columns=[True, True, True, False]
        )
        """List[Tuple[int, str, float]]"""
        super().__init__(master, plugin_scope, title, geometry, bg_color)
        logger.debug(f"Account data: {self.account_data}")
        self.init_ui()

    def _clear_placeholder(self, event):
        if self.date_entry.get() == "YYYY-MM-DD":
            self.date_entry.delete(0, tk.END)
            self.date_entry.config(foreground="black")

    def _add_placeholder(self, event):
        if not self.date_entry.get():
            self.date_entry.insert(0, "YYYY-MM-DD")
            self.date_entry.config(foreground="grey")

    def init_ui(self) -> None:
        # ======= Account Information =======
        # region
        # === Frame ===
        # region
        self.account_infomation_frame = tk.LabelFrame(
            self.main_frame, text="Account Informationen",
            background=self.bg_color, foreground="black",
        )
        self.account_infomation_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew"
        )
        self.frames.append(self.account_infomation_frame)
        # endregion
        # === Acount Name ===
        # region
        self.account_name_label = tk.Label(
            self.account_infomation_frame, text="Account Name:",
            background=self.bg_color, foreground="black"
        )
        self.account_name_label.grid(row=0, column=0)  # , sticky="nsew")
        account_names: List[str] = [
            cast(str, account[1]) for account in self.account_data
        ]
        self.account_name_var = tk.StringVar(value="Select Account")
        self.account_name_dropdown = ttk.Combobox(
            self.account_infomation_frame,
            textvariable=self.account_name_var,
            values=account_names,
            state="readonly"
        )
        self.account_name_dropdown.grid(row=0, column=1, sticky="ew")

        def on_account_selected(event):
            selected_name = self.account_name_var.get()
            for account in self.account_data:
                if account[1] == selected_name:
                    self.account_number_entry.config(state="normal")
                    self.account_number_entry.delete(0, tk.END)
                    self.account_number_entry.insert(0, str(account[2]))
                    self.account_number_entry.config(state="readonly")
                    self.account_balance_entry.config(state="normal")
                    self.account_balance_entry.delete(0, tk.END)
                    self.account_balance_entry.insert(0, str(account[3]))
                    self.account_balance_entry.config(state="readonly")
                    break

        self.account_name_dropdown.bind(
            '<<ComboboxSelected>>', on_account_selected
        )
        # endregion
        # === Account Number ===
        # region
        self.account_number_label = tk.Label(
            self.account_infomation_frame, text="Account Nummer:",
            background=self.bg_color, foreground="black"
        )
        self.account_number_label.grid(row=1, column=0)
        self.account_number_entry = tk.Entry(
            self.account_infomation_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.account_number_entry.grid(row=1, column=1, sticky="ew")
        # endregion
        # === Account Balance ===
        # region
        self.account_balance_label = tk.Label(
            self.account_infomation_frame, text="Account Balance:",
            background=self.bg_color, foreground="black"
        )
        self.account_balance_label.grid(row=2, column=0)
        self.account_balance_entry = tk.Entry(
            self.account_infomation_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.account_balance_entry.grid(row=2, column=1, sticky="ew")
        # endregion
        # === Padding ===
        # region
        for widget in self.account_infomation_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        # endregion
        # endregion
        # ======= Transaction Information =======
        # region
        # === Frame ===
        # region
        self.transaction_information_frame = tk.LabelFrame(
            self.main_frame, text="Transaktions Informationen",
            background=self.bg_color, foreground="black"
        )
        self.transaction_information_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsew"
        )
        self.frames.append(self.transaction_information_frame)
        # endregion
        # === Date ===
        # region
        self.date_label = tk.Label(
            self.transaction_information_frame, text="Datum:",
            background=self.bg_color, foreground="black"
        )
        self.date_label.grid(row=0, column=0)
        self.date_entry = tk.Entry(
            self.transaction_information_frame,
            background=self.bg_color,
            foreground="grey"
        )
        self.date_entry.insert(0, "YYYY-MM-DD")
        self.date_entry.bind("<FocusIn>", self._clear_placeholder)
        self.date_entry.bind("<FocusOut>", self._add_placeholder)
        self.date_entry.grid(row=0, column=1, sticky="ew")
        # self.date_warning_label = tk.Label(
        #     self.transaction_information_frame, text="",
        #     background=self.bg_color, foreground="red"
        # )
        # self.date_warning_label.grid(row=1, column=0, columnspan=2)
        # ========================= Transaction Type is always "manual"
        # endregion
        #  === Amount ===
        # region
        self.amount_label = tk.Label(
            self.transaction_information_frame, text="Betrag:",
            background=self.bg_color, foreground="black"
        )
        self.amount_label.grid(row=2, column=0)
        self.amount_entry = tk.Entry(
            self.transaction_information_frame, background=self.bg_color,
            foreground="black")
        self.amount_entry.grid(row=2, column=1, sticky="ew")
        # self.amount_warning_label = tk.Label(
        #     self.transaction_information_frame, text="",
        #     background=self.bg_color, foreground="red"
        # )
        # self.amount_warning_label.grid(row=3, column=0, columnspan=2)
        # endregion
        # === Purpose ===
        # region
        self.purpose_label = tk.Label(
            self.transaction_information_frame, text="Beschreibung:",
            background=self.bg_color, foreground="black", cursor="xterm"
        )
        self.purpose_label.grid(row=4, column=0)
        self.purpose_entry = tk.Entry(
            self.transaction_information_frame, background=self.bg_color,
            foreground="black")
        self.purpose_entry.grid(row=4, column=1, sticky="ew")
        # self.purpose_warning_label = tk.Label(
        #     self.transaction_information_frame, text="",
        #     background=self.bg_color, foreground="red"
        # )
        # self.purpose_warning_label.grid(row=5, column=0, columnspan=2)
        # endregion
        # === Counterparty ===
        # region
        self.counterparty_label = tk.Label(
            self.transaction_information_frame, text="Gegenpartei Name:",
            background=self.bg_color, foreground="black"
        )
        self.counterparty_label.grid(row=6, column=0)
        counterparty_names: List[str] = [
            cast(str, cp[1]) for cp in self.counterparty_data
        ]
        self.counterparty_var = tk.StringVar()
        self.counterparty_combo = ttk.Combobox(
            self.transaction_information_frame,
            textvariable=self.counterparty_var,
            values=counterparty_names,
            state="normal"
        )
        self.counterparty_combo.grid(row=6, column=1, sticky="ew")

        def filter_counterparties(event):
            entered = self.counterparty_var.get().lower()
            filtered = [v for v in counterparty_names if entered in v.lower()]
            self.counterparty_combo['values'] = (filtered if filtered
                                                 else counterparty_names)

        self.counterparty_combo.bind('<KeyRelease>', filter_counterparties)

        def on_counterparty_selected(event):
            selected_name = self.counterparty_var.get()
            for cp in self.counterparty_data:
                if cp[1] == selected_name:
                    self.counterparty_account_entry.config(state="normal")
                    self.counterparty_account_entry.delete(0, tk.END)
                    self.counterparty_account_entry.insert(0, str(cp[2]))
                    self.counterparty_account_entry.config(state="readonly")
                    break

        self.counterparty_combo.bind(
            '<<ComboboxSelected>>', on_counterparty_selected
        )
        # endregion
        # === Counterparty Account Number (read-only) ===
        # region
        self.counterparty_account_label = tk.Label(
            self.transaction_information_frame, text="Gegenpartei Konto:",
            background=self.bg_color, foreground="black"
        )
        self.counterparty_account_label.grid(row=7, column=0)
        self.counterparty_account_entry = tk.Entry(
            self.transaction_information_frame, state="readonly",
            background="gray", foreground="black"
        )
        self.counterparty_account_entry.grid(row=7, column=1, sticky="ew")
        # endregion
        # === Padding ===
        # region
        for widget in self.transaction_information_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        # endregion
        # endregion
        # ======= Category =======
        # region
        # === Frame ===
        # region
        self.category_frame = tk.LabelFrame(
            self.main_frame, text="Kategorie",
            background=self.bg_color, foreground="black"
        )
        self.category_frame.grid(
            row=2, column=0, padx=10, pady=10, sticky="nsew"
        )
        # endregion
        # === Category Name ===
        # region
        self.category_label = tk.Label(
            self.category_frame, text="Kategorie:",
            background=self.bg_color, foreground="black"
        )
        self.category_label.grid(row=0, column=0)
        category_names: List[str] = [
            cast(str, category[1]) for category in self.category_data
        ]
        self.category_name_var = tk.StringVar(value="Select Category")
        self.category_name_dropdown = ttk.Combobox(
            self.category_frame,
            textvariable=self.category_name_var,
            values=category_names,
            state="readonly"
        )
        self.category_name_dropdown.grid(row=0, column=1, sticky="ew")

        def on_category_selected(event):
            selected_name = self.category_name_var.get()
            for category in self.category_data:
                if category[2] == selected_name:
                    self.category_budget_entry.config(state="normal")
                    self.category_budget_entry.delete(0, tk.END)
                    self.category_budget_entry.insert(0, str(category[2]))
                    self.category_budget_entry.config(state="readonly")
                    break

        self.category_name_dropdown.bind(
            '<<ComboboxSelected>>', on_category_selected
        )
        # endregion
        # === Category Budget ===
        # region
        self.category_budget_label = tk.Label(
            self.category_frame, text="Budget:",
            background=self.bg_color, foreground="black"
        )
        self.category_budget_label.grid(row=1, column=0)
        self.category_budget_entry = tk.Entry(
            self.category_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.category_budget_entry.grid(row=1, column=1, sticky="ew")
        # endregion
        # === Padding ===
        # region
        for widget in self.category_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        # endregion
        # endregion

        # Equalize column widths in all frames
        # First configure the main grid so that the frames are equally wide
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Then distribute the columns evenly in each frame
        for frame in [self.account_infomation_frame,
                      self.transaction_information_frame, self.category_frame]:
            frame.grid_columnconfigure(0, weight=1, uniform="col")
            frame.grid_columnconfigure(1, weight=2, uniform="col")
