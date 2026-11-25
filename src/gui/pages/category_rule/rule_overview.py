from __future__ import annotations

import logging
from tkinter import ttk

import tksheet

from features.category_rule.category_rule_repository import (
    delete_category_rule,
    get_category_rule_data,
)
from features.importer.formater.table_config import (
    CATEGORY_RULE_TABLE_COLUMNS,
)
from features.importer.formater.table_formater import format_data
from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow
from gui.pages.category_rule.rulepage import CategoryRulePage
from models.category_rule.entity import CategoryRule
from models.transaction.import_view import TransactionImportView

logger = logging.getLogger(__name__)


class CategoryRuleOverviewPage(BaseToplevelWindow):
    def __init__(
        self,
        master: BaseWindow,
        transactions_by_view_id: dict[int, TransactionImportView],
        plugin_scope: str = "rule-overview",
        title: str = "Kategorie Zuordnungsregelen für "
        "Transaktionsimport verwalten",
        geometry: str = "1500x844",
    ) -> None:
        self.parent = master
        self.transactions_by_view_id = transactions_by_view_id
        self._load_rules()

        self.sheet_header = [
            column.header for column in CATEGORY_RULE_TABLE_COLUMNS
        ]
        self.sheet_data = format_data(self.rules, CATEGORY_RULE_TABLE_COLUMNS)
        self.selected_rule: CategoryRule
        self._load_rules()
        super().__init__(
            master, plugin_scope, title, geometry, fullscreen=False
        )

    def _load_rules(self) -> None:
        """Initialisiert die derzeit verfügbaren Beispielregeln."""
        self.rules: list[CategoryRule] = get_category_rule_data()
        self.rule_id_by_name = {rule.name: rule.id for rule in self.rules}
        self.rule_by_id = {rule.id: rule for rule in self.rules}

    def init_ui(self) -> None:
        # ============= Header =============
        # region
        self.header_frame = ttk.Frame(self.main_frame, padding=10)
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        # self.header_frame.grid_columnconfigure(0, minsize=550)
        self.create_rule_button = ttk.Button(
            self.header_frame,
            text="Neue Regel erstellen",
            command=self.create_rule,
        )
        self.separator = ttk.Separator(self.header_frame, orient="vertical")
        self.separator.grid(row=0, column=1, sticky="ns", padx=10)
        self.create_rule_button.grid(row=0, column=0, padx=10)
        self.delete_rule_button = ttk.Button(
            self.header_frame,
            text="Regel löschen",
            command=self.delete_rule,
        )
        self.delete_rule_button.grid(row=0, column=2, padx=10)
        self.delete_rule_button.config(state="disabled")
        self.edit_rule_button = ttk.Button(
            self.header_frame,
            text="Regel bearbeiten",
            command=self.edit_rule,
        )
        self.edit_rule_button.grid(row=0, column=3, padx=10)
        self.edit_rule_button.config(state="disabled")

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

        def on_double_click(event):
            if self.sheet.identify_column(event) == 0:
                return
            identified_row = self.sheet.identify_row(event)
            row = identified_row if identified_row is not None else 0
            self.edit_rule(row=row)

        def on_cell_select(event):
            self.delete_rule_button.config(state="enable")
            self.edit_rule_button.config(state="enable")

            identified_row = self.sheet.identify_row(event)
            row = identified_row if identified_row is not None else 0
            id = self.sheet.get_cell_data(row, 1)

            self.selected_rule = self.rule_by_id[id]

        def on_deselect(event):
            self.delete_rule_button.config(state="disabled")
            self.edit_rule_button.config(state="disabled")

        self.sheet.bind("<Double-Button-1>", on_double_click)

        self.sheet.extra_bindings("cell_select", func=on_cell_select)
        self.sheet.extra_bindings("deselect", func=on_deselect)

        # self.sheet.bind(
        #     "<<SheetSelect>>",
        #     lambda event=None: self._update_selected_count()
        # )
        self.sheet.pack(fill="both", expand=True)

        # ============= Separator =============
        self.separator = ttk.Separator(self.main_frame, orient="horizontal")
        self.separator.grid(row=5, column=0, sticky="ew", padx=10)
        # endregion

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)

    def edit_rule(self, row: int | None = None) -> None:
        """Open the category rule editor for the selected rule."""
        if row is None:
            selected_rows = self.sheet.get_selected_rows(
                get_cells_as_rows=True
            )

            if not selected_rows:
                return

            selected_row = next(iter(selected_rows))

            if isinstance(selected_row, tuple):
                row = selected_row[0]
            else:
                row = selected_row

        rule_id = self.sheet.get_cell_data(row, 1)

        selected_rule = self.rule_by_id.get(rule_id)

        if selected_rule is None:
            logger.error("Category rule with ID %s not found.", rule_id)
            return

        self.selected_rule = selected_rule

        rulepage = CategoryRulePage(
            self.parent,
            self.transactions_by_view_id,
            selected_rule=selected_rule,
        )
        self.wait_window(rulepage)

    def create_rule(self) -> None:
        rulepage = CategoryRulePage(
            self.parent,
            self.transactions_by_view_id,
        )
        self.wait_window(rulepage)
        self._load_rules()
        self.reload()

    def delete_rule(self) -> None:
        delete_category_rule(self.selected_rule)

    def on_checkbox_changed(self, event) -> None:
        print(event)
