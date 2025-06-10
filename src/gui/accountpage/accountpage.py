import tkinter as tk
from tkinter import ttk
from utils.data.date_utils import get_iso_date
from gui.basetoplevelwindow import BaseToplevelWindow
from gui.basewindow import BaseWindow
import utils.data.database.account_utils as db_account_utils
import utils.data.value_utils as value_utils


class AccountPage(BaseToplevelWindow):
    def __init__(self, parent: BaseWindow,
                 account_selection_needed: bool = True) -> None:
        """
        Initialize the AccountPage window with optional account selection.

        Args:
            parent(tk.Tk): The parent window.
            account_selection_needed (bool): Boolean indicating if account
                selection is required.
        """
        self.parent = parent
        self.account_selection_needed = account_selection_needed
        super().__init__(parent, plugin_scope="accountpage",
                         title="Budget Planner - Konto")

    def init_ui(self) -> None:
        """
        Create and configure the user interface for the Account Page.
        This includes widgets for account selection, account details,
        and action buttons.
        """
        # ============= Heading =============
        self.heading_label = ttk.Label(
            self.main_frame,
            text="Konto Fenster",
            font=("Helvetica", 35),
            padding=10
            )
        self.heading_label.grid(row=0, column=0, sticky="nsew")

        # ============= Account Selection =============+
        self.account_selection_combobox = ttk.Combobox(
            self.main_frame,
            state="readonly",
            font=("Helvetica", 16),
            width=30
        )
        if self.account_selection_needed:
            self.account_data = [(0, "Bitte wählen...")]
        else:
            self.account_data = [(0, "")]
        self.account_data.extend(db_account_utils.get_account_data(
            selected_columns=[True, True, False, False, False]
        ))
        print(self.account_data)
        self.account_data_dict = {
            name: id for id, name in self.account_data
        }
        print(self.account_data_dict)
        self.account_selection_combobox['values'] = list(
            self.account_data_dict.keys()
        )
        self.account_selection_combobox.grid(
            row=1, column=0, sticky="nsew", padx=5, pady=5
        )
        try:
            self.account_selection_combobox.current(0)
        except tk.TclError:
            self.show_message("Keine Konten gefunden.")
        self.account_selection_combobox.bind("<<ComboboxSelected>>",
                                             self.on_account_selected)

        # ============= Account Details Widgets =============
        details_frame = ttk.Frame(self.main_frame)
        details_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        name_label = ttk.Label(details_frame, text="Name:",
                               font=("Helvetica", 14))
        name_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.account_name_entry = ttk.Entry(details_frame,
                                            font=("Helvetica", 14))
        self.account_name_entry.grid(row=0, column=1, sticky="w",
                                     padx=5, pady=5)

        number_label = ttk.Label(details_frame, text="Nummer:",
                                 font=("Helvetica", 14))
        number_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.account_number_entry = ttk.Entry(details_frame,
                                              font=("Helvetica", 14))
        self.account_number_entry.grid(row=1, column=1, sticky="w",
                                       padx=5, pady=5)

        amount_label = ttk.Label(details_frame, text="Saldo:",
                                 font=("Helvetica", 14))
        amount_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.account_balance_entry = ttk.Entry(details_frame,
                                               font=("Helvetica", 14))
        self.account_balance_entry.grid(row=2, column=1, sticky="w",
                                        padx=5, pady=5)

        difference_label = ttk.Label(details_frame, text="Differenz:",
                                     font=("Helvetica", 14))
        difference_label.grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.account_difference_entry = ttk.Entry(details_frame,
                                                  font=("Helvetica", 14))
        self.account_difference_entry.grid(row=3, column=1, sticky="w",
                                           padx=5, pady=5)

        # ============= Action Buttons =============
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)

        self.cancel_button = ttk.Button(buttons_frame,
                                        text="Abbrechen/Schließen",
                                        command=self.cancel_action)
        self.cancel_button.grid(row=0, column=0, padx=5, pady=5)

        self.save_button = ttk.Button(buttons_frame, text="Speichern",
                                      command=self.save_action)
        self.save_button.grid(row=0, column=1, padx=5, pady=5)

        self.new_button = ttk.Button(buttons_frame, text="Neu",
                                     command=self.new_action)
        self.new_button.grid(row=0, column=2, padx=5, pady=5)

        self.delete_button = ttk.Button(buttons_frame, text="Löschen",
                                        command=self.delete_action)
        self.delete_button.grid(row=0, column=3, padx=5, pady=5)

    # ============= Account Selection Callback =============
    def on_account_selected(self, event=None) -> None:
        """
        Handle the event when an account is selected from the combobox.
        Updates the account details fields with the selected account's data.

        Args:
            event (tk.Event, optional): The event object. Defaults to None.
        """
        name_selected_account = self.account_selection_combobox.get()
        self.selected_account_id = self.account_data_dict.get(
            name_selected_account
        )

        def filter_list(e):
            if e[0] == self.selected_account_id:
                return True
            else:
                return False
        data = db_account_utils.get_account_data()
        data = list(filter(filter_list, data))
        print(data)
        self.account_name_entry.delete(0, "end")
        self.account_number_entry.delete(0, "end")
        self.account_balance_entry.delete(0, "end")
        self.account_difference_entry.delete(0, "end")
        self.account_name_entry.insert(0, data[0][1])
        self.account_number_entry.insert(0, data[0][2])
        self.account_balance_entry.insert(0, data[0][3])
        self.account_difference_entry.insert(0, data[0][4])

    # ============= Button Callback Methods =============
    def cancel_action(self) -> None:
        """
        Close the AccountPage window and reload the parent window.
        """
        self.destroy()
        self.parent.reload()

    def save_action(self) -> None:
        """
        Save the current account details to the database.
        Validates input and saves the new account data.
        """
        account_name_temp = self.account_selection_combobox.get()
        if account_name_temp == 0:
            self.show_message("Bitte Konto auswählen.")
            return
        account_id = self.account_data_dict.get(account_name_temp)
        name = self.account_name_entry.get()
        number = self.account_number_entry.get()
        try:
            balance = float(self.account_balance_entry.get())
            difference = float(self.account_difference_entry.get())
            print(account_id, name, number, balance, difference)
        except ValueError:
            self.show_message("Bitte gültige Zahlen für Saldo und"
                              "Differenz eingeben.")
            return
        db_account_utils.update_account(
            account_id=account_id,
            new_values=[name, number, balance, difference, "",
                        get_iso_date(today=True)]
        )

    def new_action(self) -> None:
        """
        Create a new account using the entered details.
        Validates input and calls the database utility to create the account.
        """
        name = self.account_name_entry.get()
        number = self.account_number_entry.get()
        try:
            balance = value_utils.convert_to_float(
                self.account_balance_entry.get()
            )
            difference = value_utils.convert_to_float(
                self.account_difference_entry.get()
            )
        except ValueError:
            self.show_message("Bitte gültige Zahlen für Saldo und/oder"
                              "Differenz eingeben.")

        db_account_utils.add_account(
            name=name,
            number=number,
            balance=balance,
            difference=difference
        )

    def reset_entrys(self) -> None:
        """
        Reset the account selection and clear all input fields.
        """
        try:
            self.account_selection_combobox.current(0)
        except tk.TclError:
            self.show_message("Keine Konten gefunden.")
        self.account_name_entry.delete(0, tk.END)
        self.account_number_entry.delete(0, tk.END)
        self.account_balance_entry.delete(0, tk.END)
        self.account_difference_entry.delete(0, tk.END)

    def delete_action(self) -> None:
        """
        Delete the currently selected account from the database.
        Handles errors and displays appropriate messages if deletion fails.
        """
        selected_account = self.account_selection_combobox.get()
        selected_account_id = self.account_data_dict.get(selected_account)
        try:
            db_account_utils.delete_account(account_id=selected_account_id)
        except db_account_utils.NoAccountFoundError as e:
            self.show_message(f"Fehler: {e}, Konto id: {selected_account_id}")
        except db_account_utils.Error as e:
            self.show_message(f"Fehler: {e}, Konto id: {selected_account_id}")
