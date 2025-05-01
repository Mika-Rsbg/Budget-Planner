import tkinter as tk
from tkinter import ttk
import locale
from gui.basetoplevelwindow import BaseToplevelWindow
import utils.data.database.account_utils as db_account_utils


class ReorderAccountWidgetsWindow(BaseToplevelWindow):
    def __init__(self, master: tk.Tk = None) -> None:
        """
        Init an instance of the ReorderAccountWidgetsWindow class.
        This class is used to reorder account widgets in the GUI.

        Args:
            master (tk.Tk): The parent window.
        """
        self.account_widgets = {}
        super().__init__(master, title="Reorder Account Widgets",
                         geometry="620x300")

    def init_ui(self) -> None:
        # Bind the Enter key to trigger saving the order
        self.bind("<Return>", lambda event: self.save_order())

        # Create a "Save Order" button at the top of the main frame
        save_btn = ttk.Button(self.main_frame, text="Speichern",
                              command=self.save_order)
        save_btn.grid(row=1, column=0, sticky="nswe", padx=10, pady=10)
        account_list = list(db_account_utils.get_account_data())
        print(account_list)

        # ============= Konto-Widgets (Row 1) =============
        for (i8_AccountID, i8_WidgetPosition, str_AccountName,
             str_AccountNumber, real_AccountBalance,
             real_AccountDifference, str_RecordDate,
             str_ChangeDate) in account_list:
            self.create_account_widget(
                row=0, column=i8_WidgetPosition,
                account_name=str_AccountName,
                current_value=real_AccountBalance,
                difference_value=real_AccountDifference,
                account_id=i8_AccountID
            )

        total_columns = len(account_list)
        for i in range(total_columns):
            self.main_frame.columnconfigure(i, weight=1)

        self.add_reorder_buttons()

    def create_account_widget(self, row: int, column: int, account_name: str,
                              account_id: int, current_value: float = 0.0,
                              difference_value: float = 0.0) -> None:
        """
        Creates a single account widget with fixed size
        and spacing to other widgets.
        """
        frame = tk.Frame(
            self.main_frame, padx=10, pady=10, width=200, height=150
        )
        frame.grid_propagate(False)
        frame.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        name_label = tk.Label(frame, text=account_name,
                              font=("Helvetica", 14, "bold"))
        name_label.pack()
        value_label = tk.Label(frame, font=("Helvetica", 24, "bold"))
        value_label.pack(pady=5)
        diff_label = tk.Label(frame, font=("Helvetica", 16))
        diff_label.pack()
        self.account_widgets[column] = {
            "frame": frame, "value_label": value_label,
            "diff_label": diff_label, "name_label": name_label,
            "account_id": account_id, "old_position": column
        }
        self.update_account_values(widget_position=column,
                                   current_value=current_value,
                                   difference_value=difference_value)

    def update_account_values(self, widget_position: int, current_value: float,
                              difference_value: float) -> None:
        widget = self.account_widgets[widget_position]
        frame, value_label, diff_label, name_label = (
            widget["frame"], widget["value_label"], widget["diff_label"],
            widget["name_label"],
        )
        current_str = locale.format_string("%.2f €", current_value,
                                           grouping=True)
        diff_str = locale.format_string("%.2f €", abs(difference_value),
                                        grouping=True)
        value_label.config(text=current_str)
        if current_value >= 0:
            bg, fg = "#ccffcc", "#006600"
        else:
            bg, fg = "#ffcccc", "#990000"
        frame.config(bg=bg)
        value_label.config(bg=bg, fg=fg)
        diff_label.config(bg=bg)
        name_label.config(bg=bg, fg=fg)
        sign = "+" if difference_value >= 0 else "-"
        diff_label.config(text=f"{sign}{diff_str}", fg=fg)

    def add_reorder_buttons(self) -> None:
        """
        Adds reorder buttons (left and right) to each account widget.
        """
        total_widgets = len(self.account_widgets)
        for position, widget in self.account_widgets.items():
            frame = widget["frame"]

            # Skip adding buttons for the first and last widgets
            if not position == 0:
                # Add left button
                left_button = tk.Button(frame, text="←",
                                        command=lambda pos=position:
                                        self.move_widget(pos, -1))
                left_button.pack(side="left", padx=5)

            if position == total_widgets - 1:
                continue

            # Add right button
            right_button = tk.Button(frame, text="→",
                                     command=lambda pos=position:
                                     self.move_widget(pos, 1))
            right_button.pack(side="right", padx=5)

    def move_widget(self, position: int, delta: int) -> None:
        new_position = position + delta
        print(f"Moving widget from {position} to {new_position}")
        # Check if the new position is valid
        if new_position < 0 or new_position >= len(self.account_widgets):
            return

        # Build a sorted list of current widget positions.
        positions = sorted(self.account_widgets.keys())
        print(f"Current positions: {positions}")

        # Swap the positions in the list.
        idx1, idx2 = positions.index(position), positions.index(new_position)
        print(f"Swapping positions {idx1} and {idx2}")
        positions[idx1], positions[idx2] = positions[idx2], positions[idx1]
        print(f"New positions: {positions}")

        # Reassign the widgets with new column indices.
        new_account_widgets = {}
        for new_col, old_key in enumerate(positions):
            widget = self.account_widgets[old_key]
            print(f"Reassigning widget {old_key} to new column {new_col}")
            widget["frame"].grid_configure(column=new_col)
            new_account_widgets[new_col] = widget

        self.account_widgets = new_account_widgets

        # Remove existing reorder buttons from every widget.
        for widget in self.account_widgets.values():
            for child in widget["frame"].winfo_children():
                if child.winfo_class() == "Button":
                    child.destroy()

        # Re-add the reorder buttons in the new order.
        self.add_reorder_buttons()

    def save_order(self) -> None:
        """
        Save the new order of the account widgets to the database.
        """
        for widget in self.account_widgets:
            print(f"Widget Position: {widget} - AccountID: "
                  f"{self.account_widgets[widget]['account_id']}"
                  f" - Old Position: "
                  f"{self.account_widgets[widget]['old_position']}")
            try:
                db_account_utils.shift_widget_positions(
                    account_id=self.account_widgets[widget]["account_id"],
                    old_pos=self.account_widgets[widget]['old_position'],
                    new_pos=widget
                )
            except db_account_utils.NoChangesDetectedError as e:
                print(f"Info: {e}")
                continue
        self.reload()
