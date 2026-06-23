import tkinter as tk
from tkinter import ttk
from typing import List, Union
from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow


class CategoryPage(BaseToplevelWindow):
    def __init__(
            self,
            parent: BaseWindow,
            plugin_scope: str,
            title: str = "Category Page",
            geometry: str = "500x600",
            bg_color: str = "white",
    ) -> None:
        self.parent = parent
        self.frames: List[Union[tk.LabelFrame, tk.Frame]] = []
        super().__init__(parent, plugin_scope, title, geometry, bg_color)
        self.init_ui()

    def _clear_placeholder(self, event, placeholder: str):
        """
        Clears the placeholder text when the tk.Entry gains focus.
        """
        widget: tk.Entry = event.widget
        if widget.get() == placeholder:
            widget.delete(0, tk.END)
            widget.config(foreground="black")

    def _add_placeholder(self, event, placeholder: str):
        """
        Adds a placeholder text if the tk.Entry is empty when focus is lost.
        """
        widget: tk.Entry = event.widget
        if not widget.get():
            widget.insert(0, placeholder)
            widget.config(foreground="grey")

    def save_categorie(self):
        pass

    def init_ui(self) -> None:
        # ======= Categorie Information =======
        # region

        # === Frame ===
        # region
        self.categorie_infomation_frame = tk.LabelFrame(
            self.main_frame, text="Kategorie Informationen",
            background=self.bg_color, foreground="black",
        )
        self.categorie_infomation_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew"
        )
        self.frames.append(self.categorie_infomation_frame)
        # endregion

        # === Categorie Name ===
        # region
        self.category_name_label = tk.Label(
            self.categorie_infomation_frame, text="Kategorie Name:",
            background=self.bg_color, foreground="black", cursor="xterm"
        )
        self.category_name_label.grid(row=4, column=0)
        self.category_name_entry = tk.Entry(
            self.categorie_infomation_frame, background=self.bg_color,
            foreground="black")
        self.category_name_entry.grid(row=4, column=1, sticky="ew")
        # Placeholder handling for the category name entry
        self._category_name_placeholder = "Name eingeben"
        # Insert initial placeholder
        self.category_name_entry.insert(0, self._category_name_placeholder)
        self.category_name_entry.config(foreground="grey")
        # Bind focus events to clear/add placeholder
        self.category_name_entry.bind(
            "<FocusIn>", lambda e,
            p=self._category_name_placeholder: self._clear_placeholder(e, p)
        )
        self.category_name_entry.bind(
            "<FocusOut>", lambda e,
            p=self._category_name_placeholder: self._add_placeholder(e, p)
        )
        # endregion

        # endregion

        # === Cancel Button ===
        # region
        self.cancel_button = ttk.Button(
            self.main_frame, text="Abbrechen", command=self.destroy
        )
        self.cancel_button.grid(row=3, column=0, padx=10, pady=10,
                                sticky="ew")
        # endregion

        # === Save Button ===
        # region
        self.save_button = ttk.Button(
            self.main_frame, text="Speichern", command=self.save_categorie
        )
        self.save_button.grid(row=4, column=0, padx=10, pady=10,
                              sticky="ew")
        # endregion

        # Equalize column widths in all frames
        # First configure the main grid so that the frames are equally wide
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Then distribute the columns evenly in each frame
        for frame in self.frames:
            frame.grid_columnconfigure(0, weight=1, uniform="col")
            frame.grid_columnconfigure(1, weight=2, uniform="col")
