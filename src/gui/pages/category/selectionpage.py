import tkinter as tk
import tkinter.ttk as ttk
from typing import Optional
from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow
from features.category.category_repository import get_category_data
from features.category.service import (get_category_names,
                                       get_category_id_name_mapping,
                                       get_category_name_id_mapping)


class CategorySelectionPage(BaseToplevelWindow):
    def __init__(self, master: BaseWindow, plugin_scope: str = "selection",
                 title: str = "Kategorie auswählen ...",
                 geometry: str = "600x160") -> None:
        self._get_category_data()
        self.final_selected_category: Optional[int] = None
        super().__init__(master, plugin_scope, title, geometry)

    def _get_category_data(self) -> None:
        self.category_data = get_category_data()
        self.category_name = get_category_names(self.category_data)
        self.category_id_name_mapping = get_category_id_name_mapping(
            self.category_data
        )
        self.category_name_id_mapping = get_category_name_id_mapping(
            self.category_data
        )

    def _category_selected(self, event: tk.Event) -> None:
        selected_category = self.category_name_dropdown.get()
        self.selected_category = self.category_name_id_mapping.get(
            selected_category
        )
        self.category_id_entry.delete(0, tk.END)
        self.category_id_entry.insert(0, str(self.selected_category))
        self.select_button.focus_set()

    def _category_id_changed(self, event: tk.Event) -> None:
        # AI: komplette Funktion
        category_id = self.category_id_entry.get()
        try:
            category_name = self.category_id_name_mapping.get(int(category_id))
        except ValueError:
            category_name = None

        if category_name is not None:
            self.category_name_dropdown.set(category_name)
            self.selected_category = int(category_id)
        else:
            self.category_name_dropdown.set("")
            self.selected_category = None

    def _category_name_changed(self, event: tk.Event) -> None:
        # AI: komplette Funktion
        search_text = self.category_name_dropdown.get().casefold()
        filtered_categories = [
            category for category in self.category_name
            if search_text in category.casefold()
        ]
        self.category_name_dropdown.configure(values=filtered_categories)
        event.widget.event_generate("<Alt-Down>")

    def init_ui(self) -> None:
        # ============= Category Selection =============
        # region
        self.selection_fram = ttk.Frame(self.main_frame, padding=10)
        self.selection_fram.grid(row=0, column=0, sticky="nsew")

        self.category_id_entry = ttk.Entry(self.selection_fram, width=10)
        self.category_id_entry.pack(pady=5, side="left")
        self.category_id_entry.focus()
        self.category_id_entry.bind("<KeyRelease>", self._category_id_changed)

        self.category_name_dropdown = ttk.Combobox(
            self.selection_fram, width=70,
            values=self.category_name
        )
        self.category_name_dropdown.pack(padx=30, side="left")
        self.category_name_dropdown.bind(
            "<<ComboboxSelected>>", self._category_selected
        )
        self.category_name_dropdown.bind(
            "<KeyRelease>", self._category_name_changed
        )
        # TODO: add waiting
        # endregion

        # ============= Footer =============
        # region
        self.footer_fram = ttk.Frame(self.main_frame, padding=10)
        self.footer_fram.grid(row=1, column=0, sticky="nsew")

        self.select_button = ttk.Button(
            self.footer_fram, text="Auswählen", width=40,
            command=self.select_category
        )
        self.select_button.pack(padx=0, side="left")
        self.select_button.bind(
            "<Return>", lambda event: self.select_category()
        )
        # TODO: change to save function

        self.cancel_button = ttk.Button(
            self.footer_fram, text="Abbrechnen",
            command=self.destroy, width=40
        )
        self.cancel_button.pack(padx=30, side="left")
        self.select_button.bind(
            "<Return>", lambda event: self.destroy()
        )
        # endregion

    def select_category(self) -> None:
        category_id = self.category_id_entry.get()
        try:
            category_name = self.category_id_name_mapping.get(int(category_id))
        except ValueError:
            category_name = None

        if category_name is not None:
            self.final_selected_category = int(category_id)
            self.destroy()
        else:
            self.show_message(
                "Ausgewählte Kategorie ID hat keine passende Kategorie!"
            )
            self.category_id_entry.focus_set()
