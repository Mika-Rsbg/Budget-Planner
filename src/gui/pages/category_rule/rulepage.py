"""Dialog zum Anzeigen und Testen von Kategorie-Zuordnungsregeln.

Die Regelverwaltung lädt Regeln derzeit noch aus Beispieldaten. Das Speichern
ist deshalb absichtlich als TODO markiert und verändert keine Datenbank.
"""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk

import tksheet

from features.category.category_repository import get_category_data
from features.category.service import (
    get_category_id_name_mapping,
    get_category_name_id_mapping,
    get_category_names,
)
from features.category_rule.category_rule_repository import (
    get_category_rule_data,
)
from features.importer.formater.table_config import TRANSACTION_TABLE_COLUMNS
from features.importer.formater.table_formater import format_data
from features.importer.transaction_query.evaluator import evaluate
from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow
from models.category_rule.entity import CategoryRule
from models.transaction.import_view import TransactionImportView

logger = logging.getLogger(__name__)


class CategoryRulePage(BaseToplevelWindow):
    """Fenster zur Auswahl, Anzeige und Prüfung einer Kategorie-Regel.

    Die öffentlichen Argumente des ursprünglichen Fensters bleiben erhalten.
    Regeln werden aktuell aus ``example_rule`` bereitgestellt; Persistenz ist
    noch nicht implementiert.
    """

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
        self.transactions_by_view_id = transactions_by_view_id
        self.sheet_header = header
        self.sheet_data = format_data([], TRANSACTION_TABLE_COLUMNS)

        self._load_categories()
        self._load_rules()

        self.selected_rule = selected_rule or self.rules[0]
        self.selected_rule_index = self._rule_index(self.selected_rule)
        self.rule_name = self.selected_rule.name
        self.priority = self.selected_rule.priority
        self.enabled = tk.BooleanVar(value=self.selected_rule.enabled)
        self.category_id = self.selected_rule.category_id
        self.query = self._rule_query(self.selected_rule)

        super().__init__(
            master, plugin_scope, title, geometry, fullscreen=False
        )

    def _load_categories(self) -> None:
        """Lädt Kategorienamen und beide Richtungen der ID-Zuordnung."""
        self.category_data = get_category_data()
        self.category_names = get_category_names(self.category_data)
        self.category_id_to_name = get_category_id_name_mapping(
            self.category_data
        )
        self.category_name_to_id = get_category_name_id_mapping(
            self.category_data
        )

    def _load_rules(self) -> None:
        """Initialisiert die derzeit verfügbaren Beispielregeln."""
        # TODO: Regeln aus dem Repository bzw. der Datenbank laden.
        self.rules: list[CategoryRule] = get_category_rule_data()
        self.rule_names = [rule.name for rule in self.rules]
        self.rule_id_by_name = {rule.name: rule.id for rule in self.rules}
        self.rule_by_id = {rule.id: rule for rule in self.rules}

    @staticmethod
    def _rule_query(rule: CategoryRule) -> str:
        """Liefert den Query-Text; ältere Modelle können ``None`` enthalten."""
        return getattr(rule, "query", None) or ""

    def _rule_index(self, rule: CategoryRule) -> int:
        """Ermittelt die Anzeigeposition anhand der ID, nicht des Namens."""
        for index, candidate in enumerate(self.rules):
            if candidate.id == rule.id:
                return index
        return 0

    def _refresh_selection(self, reload: bool = True) -> None:
        """Überträgt die ausgewählte Regel in die sichtbaren Eingabefelder."""
        rule_name = self.rule_selector.get()
        rule_id = self.rule_id_by_name.get(rule_name)
        if rule_id is not None:
            rule = self.rule_by_id.get(rule_id)
        else:
            rule = None
        if rule is None:
            logger.warning("Unbekannte Regel ausgewählt: %r", rule_name)
            return

        self.selected_rule = rule
        self.selected_rule_index = self._rule_index(rule)
        self.rule_name = rule.name
        self.priority = rule.priority
        self.enabled.set(bool(rule.enabled))
        self.category_id = rule.category_id
        self.query = self._rule_query(rule)

        if hasattr(self, "rule_name_entry"):
            self._set_entry(self.rule_name_entry, self.rule_name)
            self._set_entry(self.priority_entry, str(self.priority))
            self._set_entry(self.rule_id_entry, str(rule.id), readonly=True)
            self._set_entry(self.query_entry, self.query)
            self._show_category_id()
            category_name = self.category_id_to_name.get(self.category_id, "")
            self.category_selector.set(category_name)
        if reload:
            self.reload()

    @staticmethod
    def _set_entry(
        entry: ttk.Entry, value: str, *, readonly: bool = False
    ) -> None:
        """Ersetzt den Inhalt eines Entry-Feldes, auch wenn es readonly ist."""
        if readonly:
            entry.configure(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)
        if readonly:
            entry.configure(state="readonly")

    # --------------------------------------------------------------- callbacks
    def _category_selected(self, _event: tk.Event | None = None) -> None:
        """Aktualisiert die Kategorie-ID passend
        zum gewählten Kategorienamen."""
        category_name = self.category_selector.get()
        category_id = self.category_name_to_id.get(category_name)
        if category_id is None:
            return
        self.category_id = category_id
        self._show_category_id()

    def _show_category_id(self) -> None:
        """Zeigt die aktuell gewählte Kategorie-ID
        im schreibgeschützten Feld."""
        self._set_entry(
            self.category_id_entry,
            str(self.category_id) if self.category_id is not None else "",
            readonly=True,
        )

    def _filter_categories(self, event: tk.Event) -> None:
        """Filtert die Combobox während der Eingabe,
        ohne Auswahl zu verlieren."""
        search_text = self.category_selector.get().casefold()
        filtered = [
            name
            for name in self.category_names
            if search_text in name.casefold()
        ]
        self.category_selector.configure(values=filtered)
        # Alt-Down öffnet die Ergebnisliste; ein fehlendes Binding-Event ist
        # kein Fehler und darf die Texteingabe nicht unterbrechen.
        try:
            event.widget.event_generate("<Alt-Down>")
        except tk.TclError:
            logger.debug("Combobox-Liste konnte nicht geöffnet werden")

    # --------------------------------------------------------------------- UI
    def init_ui(self) -> None:
        """Erstellt die Regel-Auswahl, Vorschau, Details und Aktionsleiste."""
        self._build_rule_selector()
        self._build_transaction_sheet()
        self._build_rule_details()
        self._build_footer()

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

    def _build_rule_selector(self) -> None:
        """Erstellt die Auswahl der vorhandenen Regeln."""
        frame = ttk.Frame(self.main_frame, padding=10)
        frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(frame, text="Ausgewählte Zuordnungsregel:").grid(
            row=0, column=0, sticky="w"
        )

        self.rule_selector = ttk.Combobox(
            frame, state="readonly", values=self.rule_names
        )
        self.rule_selector.grid(row=0, column=1, sticky="ew", padx=10)
        self.rule_selector.current(self.selected_rule_index)
        self.rule_selector.bind("<<ComboboxSelected>>", self._on_rule_selected)

        frame.columnconfigure(1, weight=1)

        # ============= Separator =============
        ttk.Separator(self.main_frame, orient="horizontal").grid(
            row=1, column=0, sticky="ew", padx=10
        )

    def _on_rule_selected(self, _event: tk.Event) -> None:
        """Combobox-Adapter für den Regelauswahl-Callback."""
        self._refresh_selection()

    def _build_transaction_sheet(self) -> None:
        """Erstellt die nicht editierbare Transaktionsvorschau."""
        frame = ttk.Frame(self.main_frame, padding=10)
        frame.grid(row=2, column=0, sticky="nsew")

        self.sheet = tksheet.Sheet(
            frame, headers=self.sheet_header, data=self.sheet_data
        )
        self.sheet.set_all_column_widths()
        if self.sheet_data and len(self.sheet_data[0]) > 5:
            self.sheet.column_width(column=5, width=500)
        self.sheet.readonly(True)
        self.sheet.pack(fill="both", expand=True)

        # ============= Separator =============
        ttk.Separator(self.main_frame, orient="horizontal").grid(
            row=3, column=0, sticky="ew", padx=10
        )

    def _build_rule_details(self) -> None:
        """Erstellt Eingaben für Name, Priorität, Status,
        Kategorie und Query."""
        frame = ttk.Frame(self.main_frame, padding=10)
        frame.grid(row=4, column=0, sticky="ew")
        self.rule_detail_frame = frame

        # ====== Rule Name ======
        self._add_detail_label(frame, "Name der Zuordnungsregel:", 0)
        self.rule_name_entry = ttk.Entry(frame)
        self.rule_name_entry.grid(row=0, column=1, sticky="ew")
        self.rule_id_entry = ttk.Entry(frame, state="readonly")
        self.rule_id_entry.grid(row=0, column=2, sticky="ew", padx=10)

        # ====== Rule Priority ======
        self._add_detail_label(frame, "Priorität der Zuordnungsregel:", 1)
        self.priority_entry = ttk.Entry(frame)
        self.priority_entry.grid(row=1, column=1, sticky="ew", pady=5)

        # ====== Rule Enabled ======
        self._add_detail_label(frame, "Status der Zuordnungsregel:", 2)
        ttk.Checkbutton(
            frame, text="Zuordnung ist aktiviert", variable=self.enabled
        ).grid(row=2, column=1, sticky="w", padx=10)

        # ====== Rule Category ======
        self._add_detail_label(frame, "Kategorie der Zuordnungsregel:", 3)
        self.category_selector = ttk.Combobox(
            frame, values=self.category_names
        )
        self.category_selector.grid(row=3, column=1, sticky="ew", pady=5)
        self.category_selector.bind(
            "<<ComboboxSelected>>", self._category_selected
        )
        self.category_selector.bind("<KeyRelease>", self._filter_categories)
        self.category_id_entry = ttk.Entry(frame, state="readonly")
        self.category_id_entry.grid(row=3, column=2, sticky="ew", padx=10)

        # ====== Rule Query ======
        self._add_detail_label(frame, "Query der Zuordnungsregel:", 4)
        self.query_entry = ttk.Entry(frame)
        self.query_entry.grid(row=4, column=1, sticky="ew")
        ttk.Button(
            frame,
            text="Eigenschaften",
            width=20,
            command=self.test_rule,
        ).grid(row=4, column=2, padx=10)

        frame.columnconfigure(0, minsize=200)
        frame.columnconfigure(1, minsize=300, weight=1)
        self._refresh_selection(reload=False)

        # ============= Separator =============
        ttk.Separator(self.main_frame, orient="horizontal").grid(
            row=5, column=0, sticky="ew", padx=10
        )

    @staticmethod
    def _add_detail_label(frame: ttk.Frame, text: str, row: int) -> None:
        """Fügt ein einheitlich ausgerichtetes Beschriftungsfeld hinzu."""
        ttk.Label(frame, text=text).grid(row=row, column=0, sticky="ew")

    def _build_footer(self) -> None:
        """Erstellt Test-, Speichern- und Abbrechen-Schaltflächen."""
        frame = ttk.Frame(self.main_frame, padding=10)
        frame.grid(row=6, column=0, sticky="ew")

        ttk.Button(
            frame, text="Testen", width=30, command=self.test_rule
        ).grid(row=0, column=0, padx=10)
        ttk.Button(
            frame, text="Speichern", width=30, command=self.save_rule
        ).grid(row=0, column=1, padx=10)
        ttk.Button(
            frame, text="Abbrechen", width=30, command=self.destroy
        ).grid(row=0, column=2, padx=10)

    # --------------------------------------------------------------- actions
    def save_rule(self) -> None:
        """Speichert eine Regel.

        TODO: Eingaben validieren und über den Regel-Service persistieren.
        Bis dahin wird bewusst keine scheinbare Speicherung durchgeführt.
        """
        logger.info("Regelspeicherung ist noch nicht implementiert")

    def test_rule(self) -> None:
        """Wendet die aktuell ausgewählte Regel auf alle Transaktionen an."""
        rule = self.selected_rule
        matching_transactions: list[TransactionImportView] = []

        for transaction in self.transactions_by_view_id.values():
            # Vorherige Testergebnisse entfernen, damit ein erneuter Test keine
            # veralteten Kategoriezuweisungen in der Tabelle stehen lässt.
            transaction.category_id = 0
            if not rule.enabled or not evaluate(rule, transaction):
                continue

            transaction.category_id = rule.category_id
            matching_transactions.append(transaction)

        self.sheet_data = format_data(
            matching_transactions, TRANSACTION_TABLE_COLUMNS
        )
        self.reload()
