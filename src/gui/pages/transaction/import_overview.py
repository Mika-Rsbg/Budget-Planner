import logging
import tksheet
import csv
from pathlib import Path
from tkinter import ttk
import tkinter as tk
from typing import List, Tuple, Dict, Union
from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow
from features.importer.mt940.importer import import_mt940_file_gui


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
        (path, header, data, account_data,
         new_balance) = import_mt940_file_gui(self.parent)
        self.file_path: str = path
        self.sheet_header: List[str] = header
        self.sheet_data: List[List[Union[str, Tuple[str], int, float]]] = data
        self.account_data: Dict[str, str | float | int] = account_data
        self.new_balance: str = new_balance
        """
        Dictionary with account metadata:
                "account_id", "account_name", "account_number",
                "account_balance", "last_record_date"
        """
        save_to_csv(
            Path("transactions_nogithub.csv"),
            self.sheet_header,
            self.sheet_data,
        )
        super().__init__(parent, plugin_scope, title, geometry, bg_color,
                         fullscreen=True)

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
        # endregion

        # ============= Separator =============
        self.separator = ttk.Separator(
            self.main_frame,
            orient="horizontal"
        )
        self.separator.grid(row=1, column=0, sticky="ew", padx=10)

        # ============= Account Info =============
        # region
        account_name = str(self.account_data.get("account_name"))
        account_number = str(self.account_data.get("account_number"))
        last_database_entry = str(self.account_data.get("last_record_date"))
        account_balance = str(self.account_data.get("account_balance"))

        self.account_info_frame = ttk.Frame(self.main_frame, padding=10)
        self.account_info_frame.grid(row=2, column=0, sticky="nsew")

        # ====== Account Name ======
        self.account_name_label = ttk.Label(
            self.account_info_frame, text="Konto Name:",
            background=self.bg_color, foreground="black", compound="right"
        )
        self.account_name_label.grid(row=0, column=0, sticky="ew")
        self.acc_name_readonly_entry = ttk.Entry(
            self.account_info_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.acc_name_readonly_entry.config(state="normal")
        self.acc_name_readonly_entry.delete(0, tk.END)
        self.acc_name_readonly_entry.insert(0, account_name)
        self.acc_name_readonly_entry.config(state="readonly")
        self.acc_name_readonly_entry.grid(
            row=0, column=1, sticky="ew", padx=10
        )

        # ====== Account Number ======
        self.account_number_label = ttk.Label(
            self.account_info_frame, text="Konto Nummer:",
            background=self.bg_color, foreground="black", compound="right"
        )
        self.account_number_label.grid(row=0, column=3, sticky="ew")
        self.acc_number_readonly_entry = ttk.Entry(
            self.account_info_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.acc_number_readonly_entry.config(state="normal")
        self.acc_number_readonly_entry.delete(0, tk.END)
        self.acc_number_readonly_entry.insert(0, account_number)
        self.acc_number_readonly_entry.config(state="readonly")
        self.acc_number_readonly_entry.grid(
            row=0, column=4, sticky="ew", padx=10
        )

        # ====== Last Database Entry ======
        self.last_db_entry_date_label = ttk.Label(
            self.account_info_frame, text="Letzter Eintrag vom:",
            background=self.bg_color, foreground="black", compound="right"
        )
        self.last_db_entry_date_label.grid(row=0, column=5, sticky="ew")
        self.last_db_entry_readonly_entry = ttk.Entry(
            self.account_info_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.last_db_entry_readonly_entry.config(state="normal")
        self.last_db_entry_readonly_entry.delete(0, tk.END)
        self.last_db_entry_readonly_entry.insert(0, last_database_entry)
        self.last_db_entry_readonly_entry.config(state="readonly")
        self.last_db_entry_readonly_entry.grid(
            row=0, column=6, sticky="ew", padx=10
        )

        # ====== Old Balance ======
        self.account_balance_label = ttk.Label(
            self.account_info_frame, text="Alter Kontostand:",
            background=self.bg_color, foreground="black", compound="right"
        )
        self.account_balance_label.grid(row=1, column=0, sticky="ew", pady=10)
        self.acc_old_balance_readonly_entry = ttk.Entry(
            self.account_info_frame, state="readonly",
            background=self.bg_color, foreground="black"
        )
        self.acc_old_balance_readonly_entry.config(state="normal")
        self.acc_old_balance_readonly_entry.delete(0, tk.END)
        self.acc_old_balance_readonly_entry.insert(0, account_balance)
        self.acc_old_balance_readonly_entry.config(state="readonly")
        self.acc_old_balance_readonly_entry.grid(
            row=1, column=1, sticky="ew", padx=10
        )
        # endregion

        # ============= Separator =============
        self.separator = ttk.Separator(
            self.main_frame,
            orient="horizontal"
        )
        self.separator.grid(row=3, column=0, sticky="ew", padx=10)

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
        self.sheet.column_width(
            column=5,
            width=500,
        )
        # FIXME: Add no/empty file selected support

        self.sheet.enable_bindings()
        self.sheet.pack(fill="both", expand=True)

        # endregion

        # ============= Separator =============
        self.separator = ttk.Separator(
            self.main_frame,
            orient="horizontal"
        )
        self.separator.grid(row=5, column=0, sticky="ew", padx=10)

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
            command=self.open_file
        )
        self.refresh_selection_button.grid(row=0, column=4)
        # endregion

        # ============= Separator =============
        self.separator = ttk.Separator(
            self.main_frame,
            orient="horizontal"
        )
        self.separator.grid(row=7, column=0, sticky="ew", padx=10)

        # ============= Categorization =============
        # region
        self.categoration_frame = ttk.Frame(self.main_frame, padding=10)
        self.categoration_frame.grid(row=8, column=0, sticky="nsew")

        # ====== Manage Categorization ======
        self.manage_categorization_button = ttk.Button(
            self.categoration_frame, text="Zuordnungen verwalten",
            command=self.open_file
        )
        self.manage_categorization_button.grid(row=0, column=0, padx=10)

        # ====== Add Categorization ======
        self.add_categorization_button = ttk.Button(
            self.categoration_frame, text="Zuordnungen anlegen",
            command=self.open_file
        )
        self.add_categorization_button.grid(row=0, column=1, padx=10)

        # ====== Manual Categorization ======
        self.manual_categorization_button = ttk.Button(
            self.categoration_frame, text="Manuell Zuordnen",
            command=self.open_file
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

        self.save_button = ttk.Button(
            self.footer_fram, text="Speichern",
            command=self.open_file, width=30
        )
        self.save_button.grid(row=0, column=0, padx=10)

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
