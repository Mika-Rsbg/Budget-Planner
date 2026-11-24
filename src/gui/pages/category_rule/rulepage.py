import logging
import tkinter as tk
from tkinter import ttk

import tksheet

from core.transaction_query.evaluator import evaluate
from features.category.category_repository import get_category_data
from features.category.service import (
    get_category_id_name_mapping,
    get_category_name_id_mapping,
    get_category_names,
)
from features.importer.formater.table_config import TRANSACTION_TABLE_COLUMNS
from features.importer.formater.table_formater import format_data
from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow
from models.category_rule.entity import CategoryRule, example_rule
from models.transaction.import_view import TransactionImportView

logger = logging.getLogger(__name__)


class CategoryRulePage(BaseToplevelWindow):
    def __init__(
        self,
        master: BaseWindow,
        header: list[str],
        transactions_by_view_id: dict[int, TransactionImportView],
        plugin_scope: str = "automationdetails",
        title: str = "Kategorie Zuordnungsregel für "
        "Transaktionsimport verwalten",
        geometry: str = "1500x844",
        selected_rule: CategoryRule | None = None,
    ) -> None:
        self._get_category_data()
        self._get_rule_data()

        self.transactions_by_view_id: dict[int, TransactionImportView] = (
            transactions_by_view_id
        )

        self.sheet_header: list[str] = header
        transactions = []
        self.sheet_data = format_data(transactions, TRANSACTION_TABLE_COLUMNS)

        if selected_rule is not None:
            self.selected_rule: CategoryRule = selected_rule
            self.selected_rule_index = self.rule_names.index(
                self.selected_rule.name
            )

        self.rule_name: str = ""
        self.priority: int = -1
        self.enabled = tk.BooleanVar(value=False)
        self.category_id: int = -1
        self.query: str = ""

        super().__init__(
            master, plugin_scope, title, geometry, fullscreen=False
        )

    def _get_category_data(self) -> None:
        self.category_data = get_category_data()
        self.category_name = get_category_names(self.category_data)
        self.category_id_name_mapping = get_category_id_name_mapping(
            self.category_data
        )
        self.category_name_id_mapping = get_category_name_id_mapping(
            self.category_data
        )

    def _get_rule_data(self) -> None:
        self.rules: list[CategoryRule] = [example_rule, example_rule]
        # TODO: implement retrieving Rules from database

        self.rule_names = [x.name for x in self.rules]
        self.category_id_by_name_dict = {
            x.name: x.category_id for x in self.rules
        }
        self.rule_id_by_name_dict = {x.name: x.id for x in self.rules}
        self.rule_by_id = {x.id: x for x in self.rules}
        self.selected_rule_index = 0

    def _refresh_selection(self, reload=True):
        rule_id = self.rule_id_by_name_dict[self.rule_name_dropdown.get()]
        self.selected_rule: CategoryRule = self.rule_by_id[rule_id]
        self.selected_rule_index = self.rule_names.index(
            self.selected_rule.name
        )

        self.rule_name = self.selected_rule.name
        self.priority = self.selected_rule.priority
        self.enabled = tk.BooleanVar(value=self.selected_rule.enabled)
        self.category_id = self.selected_rule.category_id
        query = ""
        if self.selected_rule.query is not None:
            query = self.selected_rule.rule
        self.query = query
        if reload:
            self.reload()

    def _category_selected(self, event: tk.Event) -> None:
        selected_category = self.category_name_dropdown.get()
        self.selected_category = self.category_name_id_mapping.get(
            selected_category
        )
        self.category_id = self.category_id_by_name_dict[
            self.category_name_dropdown.get()
        ]
        self.reload()

    def _category_name_changed(self, event: tk.Event) -> None:
        # AI: komplette Funktion
        search_text = self.category_name_dropdown.get().casefold()
        filtered_categories = [
            category
            for category in self.category_name
            if search_text in category.casefold()
        ]
        self.category_name_dropdown.configure(values=filtered_categories)
        event.widget.event_generate("<Alt-Down>")

    def init_ui(self) -> None:
        """
        Init the UI for the Import Overview Page.
        """
        # ============= Rule Selection =============
        # region
        self.rule_selection_frame = ttk.Frame(self.main_frame, padding=10)
        self.rule_selection_frame.grid(row=0, column=0, sticky="nsew")

        self.rule_name_label = ttk.Label(
            self.rule_selection_frame,
            text="Ausgewählte Zuordnungsregel:",
            background=self.bg_color,
            foreground="black",
            compound="right",
        )
        self.rule_name_label.grid(row=0, column=0, sticky="ew")

        self.rule_name_dropdown = ttk.Combobox(
            self.rule_selection_frame,
            state="readonly",
            values=self.rule_names,
        )
        self.rule_name_dropdown.current(self.selected_rule_index)
        self.rule_name_dropdown.grid(row=0, column=1, sticky="ew", padx=10)
        self.rule_name_dropdown.bind(
            "<<ComboboxSelected>>", lambda _event: self._refresh_selection()
        )

        self._refresh_selection(False)

        self.rule_selection_frame.grid_columnconfigure(1, minsize=150)

        # ============= Separator =============
        self.separator = ttk.Separator(self.main_frame, orient="horizontal")
        self.separator.grid(row=1, column=0, sticky="ew", padx=10)
        # endregion

        # ============= Sheet =============
        # region
        self.sheet_frame = ttk.Frame(self.main_frame, padding=10)
        self.sheet_frame.grid(row=2, column=0, sticky="nsew", columnspan=2)
        self.sheet = tksheet.Sheet(
            self.sheet_frame,
            headers=self.sheet_header,
            data=self.sheet_data,
            # auto_resize_columns=20
        )
        self.sheet.set_all_column_widths()
        if self.sheet_data and self.sheet_data[0].__len__() > 5:
            self.sheet.column_width(
                column=5,
                width=500,
            )
        self.sheet.readonly(True)
        self.sheet.pack(fill="both", expand=True)

        # ============= Separator =============
        self.separator = ttk.Separator(self.main_frame, orient="horizontal")
        self.separator.grid(row=4, column=0, sticky="ew", padx=10)
        # endregion

        # ============= Rule Details =============
        # region
        self.rule_detail_frame = ttk.Frame(self.main_frame, padding=10)
        self.rule_detail_frame.grid(row=5, column=0, sticky="nsew")

        # ====== Rule Name ======
        # region
        self.rule_name_label = ttk.Label(
            self.rule_detail_frame,
            text="Name der Zuordnungsregel:",
            background=self.bg_color,
            foreground="black",
            compound="right",
        )
        self.rule_name_label.grid(row=0, column=0, sticky="ew")

        self.rule_name_dropdown = ttk.Entry(
            self.rule_detail_frame,
            background=self.bg_color,
            foreground="black",
        )

        if self.rule_name:
            self.rule_name_dropdown.insert(0, self.rule_name)

        self.rule_name_dropdown.grid(row=0, column=1, sticky="ew")
        self.rule_name_dropdown.bind(
            "<<ComboboxSelected>>", lambda _event: self._refresh_selection()
        )

        self.readonly_rule_id_entry = ttk.Entry(
            self.rule_detail_frame,
            background=self.bg_color,
            foreground="black",
            state="readonly",
        )

        if self.query:
            rule_id = self.selected_rule.id
            self.readonly_rule_id_entry.config(state="normal")
            self.readonly_rule_id_entry.delete(0, tk.END)
            self.readonly_rule_id_entry.insert(0, str(rule_id))
            self.readonly_rule_id_entry.config(state="readonly")

        self.readonly_rule_id_entry.grid(row=0, column=2, sticky="ew", padx=10)
        # endregion

        # ====== Rule Priority ======
        # region
        self.rule_priority_label = ttk.Label(
            self.rule_detail_frame,
            text="Priorität der Zuordnungsregel:",
            background=self.bg_color,
            foreground="black",
            compound="right",
        )
        self.rule_priority_label.grid(row=1, column=0, sticky="ew")

        self.category_priority_entry = ttk.Entry(
            self.rule_detail_frame,
            background=self.bg_color,
            foreground="black",
        )

        if self.priority:
            self.category_priority_entry.insert(0, str(self.priority))

        self.category_priority_entry.grid(row=1, column=1, sticky="ew", pady=5)
        self.category_priority_entry.bind(
            "<<ComboboxSelected>>", lambda _event: self._refresh_selection()
        )
        # endregion

        # ====== Rule Enabled ======
        # region
        self.rule_enabled_label = ttk.Label(
            self.rule_detail_frame,
            text="Status der Zuordnungsregel:",
            background=self.bg_color,
            foreground="black",
            compound="right",
        )
        self.rule_enabled_label.grid(row=2, column=0, sticky="ew")

        self.toggle_enabled_button = ttk.Checkbutton(
            self.rule_detail_frame,
            text="Zuordung ist aktiviert",
            variable=self.enabled,
        )
        self.toggle_enabled_button.grid(row=2, column=1, padx=10)
        self.category_priority_entry.bind(
            "<<ComboboxSelected>>", lambda _event: self._refresh_selection()
        )
        # endregion

        # ====== Rule Category ======
        # region
        self.rule_category_label = ttk.Label(
            self.rule_detail_frame,
            text="Kategorie der Zuordnungsregel:",
            background=self.bg_color,
            foreground="black",
            compound="right",
        )
        self.rule_category_label.grid(row=3, column=0, sticky="ew")

        self.category_name_dropdown = ttk.Combobox(
            self.rule_detail_frame,
            values=self.category_name,  # , width=70
        )
        self.category_name_dropdown.grid(row=3, column=1, sticky="ew", pady=5)
        self.category_name_dropdown.bind(
            "<<ComboboxSelected>>", self._category_selected
        )
        self.category_name_dropdown.bind(
            "<KeyRelease>", self._category_name_changed
        )

        self.readonly_category_entry = ttk.Entry(
            self.rule_detail_frame,
            background=self.bg_color,
            foreground="black",
            state="readonly",
        )

        if self.query:
            category_id = self.selected_rule.category_id
            index = self.category_name.index(
                self.category_id_name_mapping[category_id]
            )
            self.category_name_dropdown.current(index)
            self.readonly_category_entry.config(state="normal")
            self.readonly_category_entry.delete(0, tk.END)
            self.readonly_category_entry.insert(0, str(category_id))
            self.readonly_category_entry.config(state="readonly")

        self.readonly_category_entry.grid(
            row=3, column=2, sticky="ew", padx=10
        )
        # endregion

        # ====== Rule Query ======
        # region
        self.query_label = ttk.Label(
            self.rule_detail_frame,
            text="Query der Zuordnungsregel:",
            background=self.bg_color,
            foreground="black",
            compound="right",
        )
        self.query_label.grid(row=4, column=0, sticky="ew")

        self.query_entry = ttk.Entry(
            self.rule_detail_frame,
            background=self.bg_color,
            foreground="black",
        )

        if self.query:
            self.query_entry.insert(0, str(self.query))

        self.query_entry.grid(row=4, column=1, sticky="ew")

        self.query_detail_button = ttk.Button(
            self.rule_detail_frame,
            text="Eigenschaften",
            width=20,
            padding=(0, 0),
            command=self.test_rule,
        )
        self.query_detail_button.grid(row=4, column=2, padx=10)
        # endregion

        self.rule_detail_frame.grid_columnconfigure(0, minsize=200)
        self.rule_detail_frame.grid_columnconfigure(1, minsize=300)

        # ============= Separator =============
        self.separator = ttk.Separator(self.main_frame, orient="horizontal")
        self.separator.grid(row=6, column=0, sticky="ew", padx=10)
        # endregion

        # ============= Footer =============
        # region
        self.footer_fram = ttk.Frame(self.main_frame, padding=10)
        self.footer_fram.grid(row=7, column=0, sticky="nsew")

        self.test_button = ttk.Button(
            self.footer_fram,
            text="Testen",
            width=30,
            command=self.test_rule,
        )
        self.test_button.grid(row=0, column=0, padx=10)

        self.save_button = ttk.Button(
            self.footer_fram,
            text="Speichern",
            width=30,
            command=self.save_rule,
        )
        self.save_button.grid(row=0, column=1, padx=10)

        self.cancel_button = ttk.Button(
            self.footer_fram, text="Abbrechen", command=self.destroy, width=30
        )
        self.cancel_button.grid(row=0, column=2, padx=10)
        # endregion

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

    def save_rule(self):
        print("And a logic for saving a new/edited Rule!!!!!")

    def test_rule(self) -> None:
        rule = self.selected_rule
        transactions: list[TransactionImportView] = []
        for transaction in self.transactions_by_view_id.values():
            transaction.category_id = 0

            if not rule.enabled:
                continue

            if not evaluate(rule, transaction):
                continue

            transaction.category_id = rule.category_id
            transactions.append(transaction)

        self.sheet_data = format_data(transactions, TRANSACTION_TABLE_COLUMNS)
        self.reload()
