from tkinter import ttk
from gui.basetoplevelwindow import BaseToplevelWindow


class CashPage(BaseToplevelWindow):
    def __init__(self, master=None, title="Cash Page", geometry="800x600"):
        super().__init__(master, plugin_scope="cashpage", title=title,
                         geometry=geometry)
        self.cash = None  # Placeholder for cash data
        self.init_ui()

    def init_ui(self):
        # ============= Heading =============
        self.heading_label = ttk.Label(
            self.main_frame,
            text="Cash Page",
            font=("Helvetica", 35),
            padding=10
        )
        self.heading_label.grid(row=0, column=0, sticky="nsew")
