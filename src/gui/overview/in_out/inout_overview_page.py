from tkinter import ttk
from gui.basetoplevelwindow import BaseToplevelWindow
from gui.basewindow import BaseWindow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class InOutOverviewPage(BaseToplevelWindow):
    def __init__(self, parent: BaseWindow) -> None:
        """
        Initialize the InOutOverviewPage.
        Args:
            parent (BaseWindow): The parent window.
        """
        self.parent = parent
        super().__init__(parent, plugin_scope="inoutpage",
                         title="Budget Planner - Einnahmen Ausgaben",
                         geometry="1200x900",)

    def init_ui(self) -> None:
        """
        Create and configure the user interface for the Account Page.
        This includes widgets for account selection, account details,
        and action buttons.
        """
        # ============= Heading =============
        self.heading_label = ttk.Label(
            self.main_frame,
            text="Einnahmen und Ausgaben Übersicht",
            font=("Helvetica", 35),
            padding=10
            )
        self.heading_label.grid(row=0, column=0, sticky="nsew")

        # ============= Time Selection =============
        self.time_selection_frame = ttk.Frame(self.main_frame)
        self.time_selection_frame.grid(row=1, column=0, sticky="nsew")

        self.time_selection_label = ttk.Label(
            self.time_selection_frame,
            text="Zeitraum auswählen:",
            font=("Helvetica", 14)
        )
        self.time_selection_label.grid(row=0, column=0, padx=10, pady=10)
        self.time_selection_combobox = ttk.Combobox(
            self.time_selection_frame,
            values=["Letzte Woche", "Letzter Monat", "Letztes Jahr", "Benutzerdefiniert"],
            state="readonly",
            width=20
        )
        self.time_selection_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.time_selection_combobox.current(0)

        self.start_date_selction_label = ttk.Label(
            self.time_selection_frame,
            text="Von:",
            font=("Helvetica", 14)
        )
        self.start_date_selction_label.grid(row=1, column=0, padx=10, pady=10)
        self.start_date_entry = ttk.Entry(
            self.time_selection_frame,
            width=15
        )
        self.start_date_entry.grid(row=1, column=1, padx=10, pady=10)

        # Diagramm
        self.diagramm_frame = ttk.Frame(self.main_frame)
        self.diagramm_frame.grid(row=2, column=0, sticky="nsew")
        self.diagramm_label = ttk.Label(
            self.diagramm_frame,
            text="Diagramm",
            font=("Helvetica", 20),
            padding=10
        )
        self.diagramm_label.grid(row=0, column=0, sticky="nsew")

        # Beispiel-Daten
        income_expense = ["Einnahmen", "Ausgaben"]
        data_layer_1 = [240, 80]
        data_layer_2 = [50, 30]
        data_layer_3 = [0, 19]
        data_layer_4 = [0, 17]
        data_layer_5 = [0, 12]
        data_layer_6 = [0, 6]

        # Diagramm erstellen
        fig, ax = plt.subplots(figsize=(10, 5))

        # Einnahmen (grün) und Ausgaben (rot) gestapelt darstellen
        ax.bar(
            income_expense, data_layer_1, label="Einnahmen", color="green"
        )
        ax.bar(
            income_expense, data_layer_2, bottom=data_layer_1, label="Ausgaben", color="red"
        )

        ax.set_ylabel("Betrag (€)")
        ax.set_title("Einnahmen und Ausgaben nach Kategorien")
        ax.legend()

        # Diagramm in tkinter einbetten
        canvas = FigureCanvasTkAgg(fig, master=self.diagramm_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
