import tkinter as tk
from tkinter import ttk
import sqlite3
import time

DB_PATH = 'src/data/database.db'


class TransactionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transaktion hinzufügen/ändern")
        self.geometry("800x400")
        # None = neuer Eintrag, ansonsten Update-Modus
        self.current_transaction_id = None
        self.create_widgets()
        self.load_transactions()

    def create_widgets(self):
        # Root-Grid konfigurieren
        self.grid_columnconfigure(0, weight=1, uniform="group")
        self.grid_columnconfigure(1, weight=2, uniform="group")

        # Linke Seite: Formular in einem LabelFrame
        form_frame = ttk.LabelFrame(self, text="Transaktionsformular")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        form_frame.columnconfigure(1, weight=1)

        # Datum (YYMMDD)
        self.label_date = ttk.Label(form_frame, text="Datum (YYMMDD):")
        self.label_date.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_date = ttk.Entry(form_frame)
        self.entry_date.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Betrag
        self.lable_amount = ttk.Label(form_frame, text="Betrag:")
        self.lable_amount.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_amount = ttk.Entry(form_frame)
        self.entry_amount.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Zweck
        self.lable_purpose = ttk.Label(form_frame, text="Zweck:")
        self.lable_purpose.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_purpose = ttk.Entry(form_frame)
        self.entry_purpose.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Betragstyp (Plus oder Minus)
        self.lable_amounttype = ttk.Label(form_frame, text="Betragstyp:")
        self.lable_amounttype.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.combo_amounttype = ttk.Combobox(form_frame, values=["+", "-"],
                                             state="readonly")
        self.combo_amounttype.current(0)
        self.combo_amounttype.grid(row=4, column=1, padx=5, pady=5,
                                   sticky="ew")

        # Konto
        self.lable_account = ttk.Label(form_frame, text="Konto:")
        self.lable_account.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.entry_account = ttk.Entry(form_frame)
        self.entry_account.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        # Counterparty
        self.lable_counterparty = ttk.Label(form_frame, text="Counterparty:")
        self.lable_counterparty.grid(row=6, column=0, padx=5, pady=5,
                                     sticky="w")
        self.combo_counterparty = ttk.Combobox(form_frame)
        self.combo_counterparty.grid(row=6, column=1, padx=5, pady=5,
                                     sticky="ew")
        self.combo_counterparty.bind("<KeyRelease>",
                                     self.update_counterparty_list)
        self.load_counterparties()

        # Speichern-/Update-Button
        self.btn_save = ttk.Button(form_frame, text="Speichern",
                                   command=self.save_transaction)
        self.btn_save.grid(row=7, column=0, columnspan=2, padx=5, pady=10)

        # Rechte Seite: Treeview in einem LabelFrame, mit Transaktionen
        list_frame = ttk.LabelFrame(self, text="Transaktionen")
        list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("Date", "Amount", "Purpose")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings",
                                 selectmode="browse")
        self.tree.heading("Date", text="Datum")
        self.tree.heading("Amount", text="Betrag")
        self.tree.heading("Purpose", text="Zweck")
        self.tree.column("Date", width=100)
        self.tree.column("Amount", width=100)
        self.tree.column("Purpose", width=150)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar für Treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                  command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Doppelklick-Event: Details in Formular laden
        self.tree.bind("<Double-1>", self.on_treeview_double_click)

    def load_counterparties(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT str_CounterpartyName FROM tbl_Counterparty')
        counterparties = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.combo_counterparty['values'] = counterparties

    def update_counterparty_list(self, event):
        typed_text = self.combo_counterparty.get()
        if typed_text == '':
            data = self.combo_counterparty['values']
        else:
            data = [item for item in self.combo_counterparty['values'] if typed_text.lower() in item.lower()]
        self.combo_counterparty['values'] = data
        self.combo_counterparty.event_generate('<Down>')

    def save_transaction(self):
        # Eingabedaten sammeln
        date = self.entry_date.get()
        bookingdate = self.entry_bookingdate.get()
        amount = self.entry_amount.get()
        purpose = self.entry_purpose.get()
        amount_type = self.combo_amounttype.get()
        account = self.entry_account.get()
        counterparty = self.combo_counterparty.get()
        # Umrechnung: "+" = 1, "-" = 0
        i8_amounttype = 1 if amount_type == "+" else 0

        conn = None
        for _ in range(5):  # Retry mechanism
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                # Check if counterparty exists, if not, insert it
                cursor.execute('SELECT i8_CounterpartyID FROM tbl_Counterparty WHERE str_CounterpartyName = ?', (counterparty,))
                result = cursor.fetchone()
                if result:
                    counterparty_id = result[0]
                else:
                    cursor.execute('INSERT INTO tbl_Counterparty (str_CounterpartyName) VALUES (?)', (counterparty,))
                    counterparty_id = cursor.lastrowid

                if self.current_transaction_id:
                    # Update existierender Transaktion
                    cursor.execute('''
                        UPDATE tbl_Transaction
                        SET i8_Date = ?, i8_Bookingdate = ?, real_Amount = ?, str_Purpose = ?, i8_AmountType = ?, i8_Account = ?, i8_CounterpartyID = ?
                        WHERE i8_TransactionID = ?
                    ''', (date, bookingdate, amount, purpose, i8_amounttype, account, counterparty_id, self.current_transaction_id))
                    conn.commit()
                    self.current_transaction_id = None
                    self.btn_save.config(text="Speichern")
                else:
                    # Neue Transaktion einfügen
                    cursor.execute('''
                        INSERT INTO tbl_Transaction (i8_Date, i8_Bookingdate, real_Amount, str_Purpose, i8_AmountType, i8_Account, i8_CounterpartyID)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (date, bookingdate, amount, purpose, i8_amounttype, account, counterparty_id))
                    conn.commit()
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    time.sleep(1)
                else:
                    raise
            finally:
                if conn:
                    conn.close()
        self.clear_form()
        self.load_transactions()

    def load_transactions(self):
        # Alle Einträge im Treeview löschen
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Nur wesentliche Spalten laden
        cursor.execute('''
            SELECT i8_TransactionID, i8_Date, real_Amount, str_Purpose
            FROM tbl_Transaction
        ''')
        for row in cursor.fetchall():
            trans_id, date, amount, purpose = row
            self.tree.insert("", "end", iid=trans_id,
                             values=(date, amount, purpose))
        conn.close()

    def on_treeview_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            trans_id = selected_item[0]
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT i8_Date, i8_Bookingdate, real_Amount, str_Purpose, i8_AmountType, i8_Account, i8_CounterpartyID
                FROM tbl_Transaction
                WHERE i8_TransactionID = ?
            ''', (trans_id,))
            result = cursor.fetchone()
            conn.close()
            if result:
                date, bookingdate, amount, purpose, i8_amounttype, account, counterparty_id = result
                # Daten in Formularfelder laden
                self.entry_date.delete(0, tk.END)
                self.entry_date.insert(0, date)
                self.entry_bookingdate.delete(0, tk.END)
                self.entry_bookingdate.insert(0, bookingdate)
                self.entry_amount.delete(0, tk.END)
                self.entry_amount.insert(0, amount)
                self.entry_purpose.delete(0, tk.END)
                self.entry_purpose.insert(0, purpose)
                self.combo_amounttype.set("+" if i8_amounttype == 1 else "-")
                self.entry_account.delete(0, tk.END)
                self.entry_account.insert(0, account)
                cursor.execute('SELECT str_CounterpartyName FROM tbl_Counterparty WHERE i8_CounterpartyID = ?', (counterparty_id,))
                counterparty_name = cursor.fetchone()[0]
                self.combo_counterparty.set(counterparty_name)
                # Update-Modus aktivieren
                self.current_transaction_id = trans_id
                self.btn_save.config(text="Änderungen speichern")

    def clear_form(self):
        self.entry_date.delete(0, tk.END)
        self.entry_bookingdate.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.entry_purpose.delete(0, tk.END)
        self.combo_amounttype.set("+")
        self.entry_account.delete(0, tk.END)
        self.combo_counterparty.set('')
        self.current_transaction_id = None
        self.btn_save.config(text="Speichern")


if __name__ == "__main__":
    app = TransactionApp()
    app.mainloop()
