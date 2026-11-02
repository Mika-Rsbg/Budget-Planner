import logging
import tkinter as tk
from tkinter import ttk

import tksheet

from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow

logger = logging.getLogger(__name__)


class CategoryRulePage(BaseToplevelWindow):
    def __init__(
        self,
        master: BaseWindow,
        plugin_scope: str = "automationcreation",
        title: str = "Kategorie Zuordnungsregel für "
        "Transaktionsimport verwalten",
        geometry: str = "600x160",
    ) -> None:
        self.sheet_header = ["Aktiv", "Datum", "Prio", "Kategorie", "Name"]
        self.sheet_data = [
            [True, "21.03.2026", 0, 2, "Test"],
            [False, "21.03.2026", 0, 2, "Test"],
            [True, "21.03.2026", 0, 2, "Test"],
        ]
        super().__init__(
            master, plugin_scope, title, geometry, fullscreen=True
        )

    def init_ui(self) -> None:
        # ============= Header =============
        # region
        self.header_frame = ttk.Frame(self.main_frame, padding=10)
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        # self.header_frame.grid_columnconfigure(0, minsize=550)
        self.create_rule_button = ttk.Button(
            self.header_frame,
            text="Neu Regel erstellen",
            command=self.create_rule,
        )
        self.create_rule_button.grid(row=0, column=0, padx=10)
        self.delete_rule_button = ttk.Button(
            self.header_frame,
            text="Ausgewählte Regel löschen",
            command=self.create_rule,
        )
        self.delete_rule_button.grid(row=0, column=1, padx=10)
        self.delete_rule_button.config(state="disabled")

        # ============= Separator =============
        self.separator = ttk.Separator(self.main_frame, orient="horizontal")
        self.separator.grid(row=1, column=0, sticky="ew", padx=10)
        # endregion

        # ============= Sheet =============
        # region
        self.sheet_frame = ttk.Frame(self.main_frame, padding=10)
        self.sheet_frame.grid(row=4, column=0, sticky="nsew", columnspan=2)
        self.sheet = tksheet.Sheet(
            self.sheet_frame,
            headers=self.sheet_header,
            data=self.sheet_data,
        )

        self.sheet.set_all_column_widths()

        if self.sheet_data[0].__len__() > 4:
            self.sheet["A"].checkbox()
            self.sheet["A"].checkbox(
                check_function=self.on_checkbox_changed,
            )
            self.sheet.column_width(
                column=4,
                width=500,
            )
        self.sheet.enable_bindings("single_select", "row_select")
        self.sheet.readonly(True)

        # self.sheet.bind(
        #     "<<SheetSelect>>", lambda event=None: self._update_selected_count()
        # )
        self.sheet.pack(fill="both", expand=True)

        # ============= Separator =============
        self.separator = ttk.Separator(self.main_frame, orient="horizontal")
        self.separator.grid(row=5, column=0, sticky="ew", padx=10)
        # endregion

        # # ============= Account Info =============
        # region
        # account_name = self.account_data.name
        # account_number = self.account_data.number
        # last_database_entry = self.account_data.record_date.strftime(
        #     "%d.%m.%Y"
        # )

        # account_balance = self.account_data.balance

        # self.account_info_frame = ttk.Frame(self.main_frame, padding=10)
        # self.account_info_frame.grid(row=2, column=0, sticky="nsew")

        # # ====== Old Balance ======
        # self.account_balance_label = ttk.Label(
        #     self.account_info_frame,
        #     text="Alter Kontostand:",
        #     background=self.bg_color,
        #     foreground="black",
        #     compound="right",
        # )
        # self.account_balance_label.grid(row=0, column=0, sticky="ew", pady=10)
        # self.acc_old_balance_readonly_entry = ttk.Entry(
        #     self.account_info_frame,
        #     state="readonly",
        #     background=self.bg_color,
        #     foreground="black",
        # )
        # self.acc_old_balance_readonly_entry.config(state="normal")
        # self.acc_old_balance_readonly_entry.delete(0, tk.END)
        # self.acc_old_balance_readonly_entry.insert(0, str(account_balance))
        # self.acc_old_balance_readonly_entry.config(state="readonly")
        # self.acc_old_balance_readonly_entry.grid(
        #     row=0, column=1, sticky="ew", padx=10
        # )

        # # ====== Account Name ======
        # self.account_name_label = ttk.Label(
        #     self.account_info_frame,
        #     text="Konto Name:",
        #     background=self.bg_color,
        #     foreground="black",
        #     compound="right",
        # )
        # self.account_name_label.grid(row=0, column=2, sticky="ew")
        # self.acc_name_readonly_entry = ttk.Entry(
        #     self.account_info_frame,
        #     state="readonly",
        #     background=self.bg_color,
        #     foreground="black",
        # )
        # self.acc_name_readonly_entry.config(state="normal")
        # self.acc_name_readonly_entry.delete(0, tk.END)
        # self.acc_name_readonly_entry.insert(0, account_name)
        # self.acc_name_readonly_entry.config(state="readonly")
        # self.acc_name_readonly_entry.grid(
        #     row=0, column=3, sticky="ew", padx=10
        # )

        # # ====== Account Number ======
        # self.account_number_label = ttk.Label(
        #     self.account_info_frame,
        #     text="Konto Nummer:",
        #     background=self.bg_color,
        #     foreground="black",
        #     compound="right",
        # )
        # self.account_number_label.grid(row=0, column=4, sticky="ew")
        # self.acc_number_readonly_entry = ttk.Entry(
        #     self.account_info_frame,
        #     state="readonly",
        #     background=self.bg_color,
        #     foreground="black",
        # )
        # self.acc_number_readonly_entry.config(state="normal")
        # self.acc_number_readonly_entry.delete(0, tk.END)
        # self.acc_number_readonly_entry.insert(0, account_number)
        # self.acc_number_readonly_entry.config(state="readonly")
        # self.acc_number_readonly_entry.grid(
        #     row=0, column=5, sticky="ew", padx=10
        # )

        # # ====== Last Database Entry ======
        # self.last_db_entry_date_label = ttk.Label(
        #     self.account_info_frame,
        #     text="Letzter Eintrag vom:",
        #     background=self.bg_color,
        #     foreground="black",
        #     compound="right",
        # )
        # self.last_db_entry_date_label.grid(row=0, column=6, sticky="ew")
        # self.last_db_entry_readonly_entry = ttk.Entry(
        #     self.account_info_frame,
        #     state="readonly",
        #     background=self.bg_color,
        #     foreground="black",
        # )
        # self.last_db_entry_readonly_entry.config(state="normal")
        # self.last_db_entry_readonly_entry.delete(0, tk.END)
        # self.last_db_entry_readonly_entry.insert(0, last_database_entry)
        # self.last_db_entry_readonly_entry.config(state="readonly")
        # self.last_db_entry_readonly_entry.grid(
        #     row=0, column=7, sticky="ew", padx=10
        # )

        # # ============= Separator =============
        # self.separator = ttk.Separator(self.main_frame, orient="horizontal")
        # self.separator.grid(row=3, column=0, sticky="ew", padx=10)
        # endregion

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)

    def create_rule(self) -> None:
        pass

    def on_checkbox_changed(self, event) -> None:
        print(event)
