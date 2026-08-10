import logging
import tksheet
import csv
from pathlib import Path
from tkinter import ttk
import tkinter as tk
from typing import List, Tuple, Union, Dict
from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow
from features.importer.mt940.importer import (import_mt940_file_gui,
                                              insert_transactions_to_db)
from models.account.entity import Account
from models.transaction.imported_view import ImportedTransactionView


logger = logging.getLogger(__name__)


def save_to_csv(
    file_path: Path,
    header: list[str],
    data: list[list],
) -> None:
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(header)
        writer.writerows(data)


class ImportOverview(BaseToplevelWindow):
    def __init__(self, parent: BaseWindow, plugin_scope: str,
                 title="Transactions Importer Page",
                 geometry="500x600", bg_color="white") -> None:
        self.parent = parent

        (path, header, data, initialy_selected_rows, account_data,
         new_balance, transactions, history_data,
         latest, valid_file) = import_mt940_file_gui(
            self.parent,
            path="C:/Users/Mika/Downloads/20260704-1077149530-umsMT940.TXT"
            )
        # TODO: Delete path

        self.file_path: str = path
        self.sheet_header: List[str] = header
        self.sheet_data: List[List[Union[str, Tuple[str], int, float]]] = data
        self.rows_not_in_database = initialy_selected_rows
        self.account_data: Account = account_data
        self.new_balance: str = new_balance
        self.transactions_by_import_id: Dict[int, ImportedTransactionView] = {
            transaction.import_id: transaction
            for transaction in transactions
        }
        self.history_data = history_data
        self.latest = latest
        self.valid_file_selected = valid_file

        save_to_csv(
            Path("transactions_nogithub.csv"),
            self.sheet_header,
            self.sheet_data,
        )
        super().__init__(parent, plugin_scope, title, geometry, bg_color,
                         fullscreen=True)

    def _selected_not_already_imported(self):
        for row in self.rows_not_in_database:
            self.sheet.add_row_selection(row)

    def _refresh_selection(self):
        mode = self.selection_mode_dropdown.get()
        if mode == "Nicht importiert":
            self._selected_not_already_imported()
        else:
            self.sheet.deselect("all")
        # TODO: add differnt mode support

    def init_ui(self) -> None:
        """
        Init the UI for the Import Overview Page.
        """
        # ============= File Info =============
        # region
        self.file_info_frame = ttk.Frame(self.main_frame, padding=10)
        self.file_info_frame.grid(row=0, column=0, sticky="nsew")
        self.path_readonly_entry = ttk.Entry(
            self.file_info_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.path_readonly_entry.config(state="normal")
        self.path_readonly_entry.delete(0, tk.END)
        self.path_readonly_entry.insert(0, self.file_path)
        self.path_readonly_entry.config(state="readonly")
        self.path_readonly_entry.grid(row=0, column=0, sticky="ew")
        self.file_info_frame.grid_columnconfigure(0, minsize=550)
        self.open_file_button = ttk.Button(
            self.file_info_frame, text="Öffne andere Datei",
            command=self.open_file
        )
        self.open_file_button.grid(row=0, column=1, padx=10)

        # ============= Separator =============
        self.separator = ttk.Separator(
            self.main_frame,
            orient="horizontal"
        )
        self.separator.grid(row=1, column=0, sticky="ew", padx=10)
        # endregion

        # ============= Account Info =============
        # region
        account_name = self.account_data.name
        account_number = self.account_data.number
        last_database_entry = self.account_data.record_date.strftime(
            "%d.%m.%Y"
            )

        # FIXME: add clear typ declaration
        account_balance = self.account_data.balance

        self.account_info_frame = ttk.Frame(self.main_frame, padding=10)
        self.account_info_frame.grid(row=2, column=0, sticky="nsew")

        # ====== Old Balance ======
        self.account_balance_label = ttk.Label(
            self.account_info_frame, text="Alter Kontostand:",
            background=self.bg_color, foreground="black", compound="right"
        )
        self.account_balance_label.grid(row=0, column=0, sticky="ew", pady=10)
        self.acc_old_balance_readonly_entry = ttk.Entry(
            self.account_info_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.acc_old_balance_readonly_entry.config(state="normal")
        self.acc_old_balance_readonly_entry.delete(0, tk.END)
        self.acc_old_balance_readonly_entry.insert(0, str(account_balance))
        self.acc_old_balance_readonly_entry.config(state="readonly")
        self.acc_old_balance_readonly_entry.grid(
            row=0, column=1, sticky="ew", padx=10
        )

        # ====== Account Name ======
        self.account_name_label = ttk.Label(
            self.account_info_frame, text="Konto Name:",
            background=self.bg_color, foreground="black", compound="right"
        )
        self.account_name_label.grid(row=0, column=2, sticky="ew")
        self.acc_name_readonly_entry = ttk.Entry(
            self.account_info_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.acc_name_readonly_entry.config(state="normal")
        self.acc_name_readonly_entry.delete(0, tk.END)
        self.acc_name_readonly_entry.insert(0, account_name)
        self.acc_name_readonly_entry.config(state="readonly")
        self.acc_name_readonly_entry.grid(
            row=0, column=3, sticky="ew", padx=10
        )

        # ====== Account Number ======
        self.account_number_label = ttk.Label(
            self.account_info_frame, text="Konto Nummer:",
            background=self.bg_color, foreground="black", compound="right"
        )
        self.account_number_label.grid(row=0, column=4, sticky="ew")
        self.acc_number_readonly_entry = ttk.Entry(
            self.account_info_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.acc_number_readonly_entry.config(state="normal")
        self.acc_number_readonly_entry.delete(0, tk.END)
        self.acc_number_readonly_entry.insert(0, account_number)
        self.acc_number_readonly_entry.config(state="readonly")
        self.acc_number_readonly_entry.grid(
            row=0, column=5, sticky="ew", padx=10
        )

        # ====== Last Database Entry ======
        self.last_db_entry_date_label = ttk.Label(
            self.account_info_frame, text="Letzter Eintrag vom:",
            background=self.bg_color, foreground="black", compound="right"
        )
        self.last_db_entry_date_label.grid(row=0, column=6, sticky="ew")
        self.last_db_entry_readonly_entry = ttk.Entry(
            self.account_info_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.last_db_entry_readonly_entry.config(state="normal")
        self.last_db_entry_readonly_entry.delete(0, tk.END)
        self.last_db_entry_readonly_entry.insert(0, last_database_entry)
        self.last_db_entry_readonly_entry.config(state="readonly")
        self.last_db_entry_readonly_entry.grid(
            row=0, column=7, sticky="ew", padx=10
        )

        # ============= Separator =============
        self.separator = ttk.Separator(
            self.main_frame,
            orient="horizontal"
        )
        self.separator.grid(row=3, column=0, sticky="ew", padx=10)
        # endregion

        # ============= Sheet =============
        # region
        self.sheet_frame = ttk.Frame(self.main_frame, padding=10)
        self.sheet_frame.grid(row=4, column=0, sticky="nsew", columnspan=2)
        self.sheet = tksheet.Sheet(
            self.sheet_frame,
            headers=self.sheet_header,
            data=self.sheet_data,
            # auto_resize_columns=20
        )
        self.sheet.set_all_column_widths()
        if self.sheet_data[0].__len__() > 5:
            self.sheet.column_width(
                column=4,
                width=500,
            )
        self.sheet.readonly(True)

        # self.sheet.select_row(1)
        # self.sheet.add_row_selection(5)
        # self.sheet.add_row_selection(8)
        # self.sheet.deselect("all")

        self._selected_not_already_imported()

        # FIXME: Add no or empty file selected support

        self.sheet.enable_bindings()
        self.sheet.pack(fill="both", expand=True)

        # ============= Separator =============
        self.separator = ttk.Separator(
            self.main_frame,
            orient="horizontal"
        )
        self.separator.grid(row=5, column=0, sticky="ew", padx=10)
        # endregion

        # ============= Selection =============
        # region
        self.selection_frame = ttk.Frame(self.main_frame, padding=10)
        self.selection_frame.grid(row=6, column=0, sticky="nsew")

        # ====== New Balance ======
        self.new_account_balance_label = ttk.Label(
            self.selection_frame, text="Neuer Kontostand:",
            background=self.bg_color, foreground="black", compound="right"
        )
        self.new_account_balance_label.grid(row=0, column=0, sticky="ew")
        self.acc_new_balance_readonly_entry = ttk.Entry(
            self.selection_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.acc_new_balance_readonly_entry.config(state="normal")
        self.acc_new_balance_readonly_entry.delete(0, tk.END)
        self.acc_new_balance_readonly_entry.insert(0, self.new_balance)
        self.acc_new_balance_readonly_entry.config(state="readonly")
        self.acc_new_balance_readonly_entry.grid(
            row=0, column=1, sticky="ew", padx=10
        )

        # ====== Selection Mode ======
        self.selection_mode_dropdown = ttk.Combobox(
            self.selection_frame, state="readonly",
            values=[
                "Bereits importiert", "Nicht importiert",
                "Nicht importiert, nicht zugeordnet",
                "Nicht zugeordnet", "Bereits zugeordnet"
                ]
        )
        self.selection_mode_dropdown.current(1)
        self.selection_mode_dropdown.grid(
            row=0, column=2, sticky="ew"
        )

        self.selection_frame.grid_columnconfigure(2, minsize=250)

        self.number_selected_readonly_entry = ttk.Entry(
            self.selection_frame, state="readonly",
            background=self.bg_color, foreground="black", width=10
        )

        number_selected = "0/" + str(self.sheet_data.__len__())

        self.number_selected_readonly_entry.config(
            state="normal", justify="center"
        )
        self.number_selected_readonly_entry.delete(0, tk.END)
        self.number_selected_readonly_entry.insert(0, number_selected)
        self.number_selected_readonly_entry.config(state="readonly")
        self.number_selected_readonly_entry.grid(
            row=0, column=3, sticky="ew", padx=10
        )

        self.refresh_selection_button = ttk.Button(
            self.selection_frame, text="Aktualisieren",
            command=self._refresh_selection
        )
        self.refresh_selection_button.grid(row=0, column=4)

        # ============= Separator =============
        self.separator = ttk.Separator(
            self.main_frame,
            orient="horizontal"
        )
        self.separator.grid(row=7, column=0, sticky="ew", padx=10)
        # endregion

        # ============= Categorization =============
        # region
        self.categoration_frame = ttk.Frame(self.main_frame, padding=10)
        self.categoration_frame.grid(row=8, column=0, sticky="nsew")

        # ====== Manage Categorization ======
        self.manage_categorization_button = ttk.Button(
            self.categoration_frame, text="Zuordnungen verwalten",
            # command=self.open_file
        )
        self.manage_categorization_button.grid(row=0, column=0, padx=10)

        # ====== Add Categorization ======
        self.add_categorization_button = ttk.Button(
            self.categoration_frame, text="Zuordnungen anlegen",
            # command=self.open_file
        )
        self.add_categorization_button.grid(row=0, column=1, padx=10)

        # ====== Manual Categorization ======
        self.manual_categorization_button = ttk.Button(
            self.categoration_frame, text="Manuell Zuordnen",
            # command=self.open_file
        )
        self.manual_categorization_button.grid(row=0, column=2, padx=10)

        # ====== Toggle Categorization ======
        self.toggle_categorization_button = ttk.Checkbutton(
            self.categoration_frame, text="Automatische Zuordnung",
            variable=tk.BooleanVar(value=True)
        )
        self.toggle_categorization_button.grid(row=0, column=3, padx=10)
        # endregion

        # ============= Footer =============
        # region
        self.footer_fram = ttk.Frame(self.main_frame, padding=10)
        self.footer_fram.grid(row=9, column=0, sticky="nsew")

        self.import_button = ttk.Button(
            self.footer_fram, text="Importieren", width=30,
            command=self.import_transactions
        )
        self.import_button.grid(row=0, column=0, padx=10)

        self.cancel_button = ttk.Button(
            self.footer_fram, text="Abbrechnen",
            command=self.destroy, width=30
        )
        self.cancel_button.grid(row=0, column=1, padx=10)
        # endregion

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)

    def open_file(self):
        (path, header, data,
         account_data, new_balance) = import_mt940_file_gui(self.parent)
        self.file_path = path
        self.sheet_header = header
        self.sheet_data = data
        self.account_data = account_data
        self.new_balance = new_balance
        save_to_csv(
            Path("transactions_nogithub.csv"),
            self.sheet_header,
            self.sheet_data,
        )
        self.reload()

    def import_transactions(self):
        if self.valid_file_selected:
            selected_rows = self.sheet.get_selected_rows(
                get_cells_as_rows=True
            )
            data_selected_rows = self.sheet.get_sheet_data(
                only_rows=iter(selected_rows)  # type: ignore
            )

            if data_selected_rows == []:
                self.show_message("No Transaction to import selected.")
                logger.debug("Close Import Overview. No Transaction selected.")
                self.destroy()

            selected_transactions: List[ImportedTransactionView] = [
                self.transactions_by_import_id[row[-1]]
                for row in data_selected_rows
                if row and row[-1] in self.transactions_by_import_id
            ]

            insert_transactions_to_db(
                selected_transactions, self.history_data, self.latest,
                self.master
            )

            self.show_message("Transactions imported succesfully.")
            # TODO: improve user feedback
            logger.debug("Close Import Overview. After import.")
            self.destroy()
        else:
            self.show_message("Empty or invalid file selected.")
            logger.info("Empty or invalid file selected. No import possible.")
            logger.debug("Close Import Overview.")
            self.destroy()
