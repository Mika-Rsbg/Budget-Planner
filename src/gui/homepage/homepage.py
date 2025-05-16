import tkinter as tk
from tkinter import ttk
import locale
import logging
from utils.logging.logging_tools import logg
from gui.basewindow import BaseWindow
from utils.data.date_utils import get_month_literal
from utils.data.database.account_utils import get_account_data
from gui.budget_suggestion.suggestion_dialog import BudgetSuggestionDialog

logger = logging.getLogger(__name__)


class Homepage(BaseWindow):
    def __init__(self, fullscreen: bool = False) -> None:
        logger.debug("Initializing Homepage")
        # Init empty dictionary for account widgets
        self.account_widgets = {}
        super().__init__(plugin_scope="homepage",
                         title="Budget Planner - Homepage", geometry="800x600",
                         fullscreen=fullscreen)

    def _create_account_widget_frame(self, row: int, column: int) -> tk.Frame:
        """
        Create a frame for the account widget.

        Args:
            row (int): The row of the frame.
            column (int): The column of the frame.
        Returns:
            tk.Frame: The created frame.
        """
        frame = tk.Frame(
            self.main_frame,
            padx=10, pady=10,
            width=200, height=150
        )
        frame.grid_propagate(False)
        frame.grid(
            row=row, column=column, sticky="nsew", padx=5, pady=5
        )
        return frame

    def _make_account_widget_label(self, parent: tk.Widget, text: str = "",
                                   font: tuple | None = None,
                                   **kwargs) -> tk.Label:
        """
        Create a label for the account widget.

        Args:
            parent (tk.Widget): The parent widget.
            text (str): The text of the label.
            font (tuple | None): The font of the label.
            **kwargs: Additional arguments for the label.
        Returns:
            tk.Label: The created label.
        """
        label = tk.Label(parent, text=text, font=font, **kwargs)
        label.pack(pady=kwargs.get('pady', 0))
        return label

    def init_ui(self):
        """
        Init the UI for the homepage.
        """
        # ============= Heanding =============
        self.heading_frame = ttk.Frame(self.main_frame, padding=10)
        self.heading_frame.grid(row=0, column=0, sticky="nsew")
        self.homepage_heading_label = ttk.Label(
            self.heading_frame,
            text="Willkommen im Budget Planner",
            font=("Helvetica", 35),
            padding=10
        )
        self.homepage_heading_label.grid(row=0, column=0, sticky="nsew")
        self.homepage_heading_label.config(text=get_month_literal())

        # ============= Budget Frame (Row 1, Column 0) =============
        self.budget_frame = tk.Frame(self.main_frame, width=80, height=150)
        self.budget_frame.configure(padx=10, pady=10)
        self.budget_frame.grid_propagate(False)
        self.budget_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.budget_label = tk.Label(
            self.budget_frame,
            text="0.00 €",
            font=("Helvetica", 28, "bold"),
            pady=10
        )
        self.budget_label.pack(expand=True)
        self.set_budget(0.0)

        # ============= AI Suggestion Button =============
        self.suggestion_button = ttk.Button(
            self.budget_frame,
            text="Get AI Budget Suggestions",
            command=self.open_budget_suggestions
        )
        self.suggestion_button.pack(side=tk.BOTTOM, pady=5)

        # ============= Konto-Widgets (Row 1, Columns 1 - ...) =============
        # Get the account data from the database
        account_list = list(get_account_data())
        logger.info(f"Retrieved {len(account_list)} accounts from database.")
        logger.debug(f"Account data retrieved: {account_list}")

        for (i8_AccountID, i8_WidgetPosition, str_AccountName,
             str_AccountNumber, real_AccountBalance,
             real_AccountDifference, str_RecordDate,
             str_ChangeDate) in account_list:
            logger.info(f"Creating widget for account '{str_AccountName}' "
                        f"at position {i8_WidgetPosition}")
            self.create_account_widget(
                row=2, column=i8_WidgetPosition,
                account_name=str_AccountName,
                current_value=real_AccountBalance,
                difference_value=real_AccountDifference
            )

        total_columns = len(account_list) if len(account_list) > 0 else 1
        for i in range(total_columns):
            self.main_frame.columnconfigure(i, weight=1)

        # Set columnspan for heading and buttons
        self.heading_frame.grid_configure(columnspan=total_columns)
        self.budget_frame.grid_configure(columnspan=total_columns)

    @logg
    def create_account_widget(self, row: int, column: int, account_name: str,
                              current_value: float = 0.0,
                              difference_value: float = 0.0) -> None:
        """
        Create an account widget for the homepage.

        Args:
            row (int): The row of the widget.
            column (int): The column of the widget.
            account_name (str): The name of the account.
            current_value (float): The current value of the account.
            difference_value (float): The difference value of the account.
        """
        frame = self._create_account_widget_frame(row, column)
        labels = {
            'name': self._make_account_widget_label(
                frame,
                text=account_name,
                font=("Helvetica", 14, "bold")
            ),
            'value': self._make_account_widget_label(
                frame,
                font=("Helvetica", 24, "bold"),
                pady=5
            ),
            'diff': self._make_account_widget_label(
                frame,
                font=("Helvetica", 16)
            ),
        }
        self.account_widgets[column] = {
            'frame': frame,
            'name_label': labels['name'],
            'value_label': labels['value'],
            'diff_label': labels['diff'],
        }
        self.update_account_values(column, current_value, difference_value)

    @logg
    def update_account_values(self, widget_position: int, current_value: float,
                              difference_value: float) -> None:
        try:
            widget = self.account_widgets[widget_position]
            frame = widget['frame']
            value_label = widget['value_label']
            diff_label = widget['diff_label']
            name_label = widget['name_label']

            current_str = locale.format_string(
                "%.2f €", current_value, grouping=True
            )
            diff_str = locale.format_string(
                "%.2f €", abs(difference_value), grouping=True
            )

            is_current_positive = current_value >= 0
            is_diff_positive = difference_value >= 0
            bg_color = "#ccffcc" if is_current_positive else "#ffcccc"
            current_fg = "#006600" if is_current_positive else "#990000"
            diff_fg = "#006600" if is_diff_positive else "#990000"

            frame.config(bg=bg_color)
            for lbl in (value_label, name_label):
                lbl.config(bg=bg_color, fg=current_fg)
            diff_label.config(bg=bg_color)

            value_label.config(text=current_str)
            sign = '+' if difference_value >= 0 else '-'
            diff_label.config(text=f"{sign}{diff_str}", fg=diff_fg)
            name_label.config(fg=current_fg)
            logger.info(f"Updated widget {widget_position}: "
                        f"value={current_value}, diff={difference_value}")
        except Exception as e:
            logger.error(f"Error updating widget {widget_position}: {e}")

    @logg
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
        self.budget_frame.config(bg=bg_color)
        logger.info(f"Budget set to {amount:.2f} €")

    @logg
    def open_budget_suggestions(self):
        """Open the budget suggestions dialog."""
        logger.info("Opening budget suggestions dialog.")
        suggestion_dialog = BudgetSuggestionDialog(self)
        self.wait_window(suggestion_dialog)
        logger.info("Budget suggestions dialog closed.")
