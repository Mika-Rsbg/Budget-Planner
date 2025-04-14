import tkinter as tk
from tkinter import ttk
from gui.basewindow import BaseWindow
from utils.data.selection_utils import get_month_literal
import locale


class Homepage(BaseWindow):
    def __init__(self, fullscreen: bool = False) -> None:
        # Initialisiere leeres Dictionary, bevor UI aufgebaut wird
        self.account_widgets = {}
        super().__init__(plugin_scope="homepage",
                         title="Budget Planner - Homepage", geometry="800x600",
                         fullscreen=fullscreen)

    def init_ui(self):
        """
        Erzeuge Widgets und Layout für die Homepage.
        """
        # ============= Überschrift =============
        self.heading_frame = ttk.Frame(self.main_frame, padding=10)
        # Da wir nun 5 Spalten haben, überdeckt die Überschrift alle
        self.heading_frame.grid(row=0, column=0, columnspan=5, sticky="nsew")

        self.homepage_heading_label = ttk.Label(
            self.heading_frame,
            text="Willkommen im Budget Planner",
            font=("Helvetica", 35),
            padding=10
        )
        self.homepage_heading_label.grid(row=0, column=0, sticky="nsew")
        # Optional: Monatsname setzen, falls du get_month_literal verwendest
        self.homepage_heading_label.config(text=get_month_literal())

        # ============= Budget Frame (Row 1, Column 0) =============
        # Fest definierte Größe wie bei den Konto-Widgets (200x150)
        budget_frame = ttk.Frame(self.main_frame, padding=10, width=200,
                                 height=150)
        budget_frame.grid_propagate(False)
        budget_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.budget_label = tk.Label(
            budget_frame,
            text="0.00 €",
            font=("Helvetica", 36),
            width=20,
            pady=20
        )
        self.budget_label.pack(expand=True)
        self.set_budget(0.0)

        # ============= Konto-Widgets (Row 1, Columns 1 - 4) =============
        self.create_account_widget(
            row=1, column=1,
            account_name="Giro Konto",
            current_value=-45.04,
            difference_value=-14.43
        )
        self.create_account_widget(
            row=1, column=2,
            account_name="Sparbuch",
            current_value=1293.50,
            difference_value=362.50
        )
        self.create_account_widget(
            row=1, column=3,
            account_name="Tagesgeldkonto",
            current_value=340.50,
            difference_value=-14.43
        )
        self.create_account_widget(
            row=1, column=4,
            account_name="Bargeld",
            current_value=265.63,
            difference_value=-14.43
        )

        # ============= Weiter-Button (Row 2) =============
        button = ttk.Button(self.main_frame, text="Weiter",
                            command=self.on_next)
        button.grid(row=2, column=0, columnspan=5, pady=20)

        # Alle 5 Spalten gleichmäßig gewichten (für responsive Layout)
        for i in range(5):
            self.main_frame.columnconfigure(i, weight=1)

    def create_account_widget(self,
                              row: int,
                              column: int,
                              account_name: str,
                              current_value: float = 0.0,
                              difference_value: float = 0.0) -> None:
        """
        Erstellt ein einzelnes Konto-Widget mit fester
        Größe und Abstand zu anderen Widgets.
        """
        account_frame = tk.Frame(
            self.main_frame,
            padx=10,
            pady=10,
            width=200,
            height=150
        )
        account_frame.grid_propagate(False)  # Größe fixieren
        account_frame.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=5,
            pady=5
        )

        name_label = tk.Label(
            account_frame,
            text=account_name,
            font=("Helvetica", 14, "bold")
        )
        name_label.pack()

        value_label = tk.Label(
            account_frame,
            font=("Helvetica", 24, "bold")
        )
        value_label.pack(pady=5)

        diff_label = tk.Label(
            account_frame,
            font=("Helvetica", 16)
        )
        diff_label.pack()

        self.account_widgets[account_name] = {
            "frame": account_frame,
            "value_label": value_label,
            "diff_label": diff_label,
            "name_label": name_label
        }

        self.update_account_values(
            account_name=account_name,
            current_value=current_value,
            difference_value=difference_value
        )

    def update_account_values(self,
                              account_name: str,
                              current_value: float,
                              difference_value: float) -> None:
        widget = self.account_widgets[account_name]
        frame = widget["frame"]
        value_label = widget["value_label"]
        diff_label = widget["diff_label"]
        name_label = widget["name_label"]

        current_str = locale.format_string("%.2f €", current_value,
                                           grouping=True)
        diff_str = locale.format_string("%.2f €", abs(difference_value),
                                        grouping=True)

        value_label.config(text=current_str)

        if current_value >= 0:
            bg_color = "#ccffcc"
            value_fg = "#006600"
        else:
            bg_color = "#ffcccc"
            value_fg = "#990000"

        frame.config(bg=bg_color)
        value_label.config(bg=bg_color, fg=value_fg)
        diff_label.config(bg=bg_color)
        name_label.config(bg=bg_color, fg=value_fg)

        if difference_value >= 0:
            diff_label.config(text=f"+{diff_str}", fg="#006600")
        else:
            diff_label.config(text=f"-{diff_str}", fg="#990000")

    def set_budget(self, amount: float) -> None:
        self.budget_value = amount
        self.budget_label.config(text=f"{amount:.2f} €")

        if amount >= 0:
            bg_color = "#ccffcc"
            fg_color = "#006600"
        else:
            bg_color = "#ffcccc"
            fg_color = "#990000"

        self.budget_label.config(bg=bg_color, fg=fg_color)

    def on_next(self):
        self.set_budget(-25.6)
        self.update_account_values(
            account_name="Giro Konto",
            current_value=-5200.00,
            difference_value=14.96
        )


if __name__ == '__main__':
    app = Homepage()
    app.mainloop()
