import tkinter.ttk as ttk
from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow


class CategorySelectionPage(BaseToplevelWindow):
    def __init__(self, master: BaseWindow, plugin_scope: str = "selection",
                 title: str = "Kategorie auswählen ...",
                 geometry: str = "600x160") -> None:
        super().__init__(master, plugin_scope, title, geometry)

    def init_ui(self) -> None:
        # ============= Footer =============
        # region
        self.selection_fram = ttk.Frame(self.main_frame, padding=10)
        self.selection_fram.grid(row=0, column=0, sticky="nsew")

        self.category_id_entry = ttk.Entry(self.selection_fram, width=10)
        self.category_id_entry.pack(pady=5, side="left")
        self.category_id_entry.focus()

        self.category_name_dropdown = ttk.Combobox(
            self.selection_fram, width=70
        )
        self.category_name_dropdown.pack(padx=30, side="left")
        # endregion

        # ============= Footer =============
        # region
        self.footer_fram = ttk.Frame(self.main_frame, padding=10)
        self.footer_fram.grid(row=1, column=0, sticky="nsew")

        self.select_button = ttk.Button(
            self.footer_fram, text="Auswählen", width=40,
            command=self.destroy
        )
        self.select_button.pack(padx=0, side="left")

        self.cancel_button = ttk.Button(
            self.footer_fram, text="Abbrechnen",
            command=self.destroy, width=40
        )
        self.cancel_button.pack(padx=30, side="left")
        # endregion
