import tkinter as tk
from tkinter import ttk
import sqlite3
import time
from datetime import datetime
from utils.utils_mt940_loader import load_file  # Neuer Import für MT940 Loader

DB_PATH = 'src/data/database.db'


class TransactionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transaktion hinzufügen/ändern")
        # self.geometry("800x400")
        self.state("zoomed")
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

#######################################################

        # Account
        self.label_account = ttk.Label(form_frame, text="Konto:")
        self.label_account.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_account = ttk.Combobox(form_frame, values=[""],
                                          state="readonly")
        self.load_accounts()
        self.combo_account.current(0)
        self.combo_account.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        # Account erstellen Button
        self.btn_create_account = ttk.Button(form_frame,
                                             text="Konto erstellen",
                                             command=self.create_account)
        self.btn_create_account.grid(row=0, column=2, padx=5, pady=5)
        self.btn_create_account.bind("<Return>",
                                     self.create_account)

        # Date (YYMMDD)
        self.label_date = ttk.Label(form_frame, text="Datum (YYMMDD):")
        self.label_date.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_date = ttk.Entry(form_frame)
        self.entry_date.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        # Today Button
        self.btn_set_date = ttk.Button(
            form_frame,
            text="Heute",
            command=self.set_date_today
            )
        self.btn_set_date.grid(row=2, column=2, padx=5, pady=5)
        self.btn_set_date.bind("<Return>",
                               self.set_date_today)

        # AmountType (+/-)
        self.label_amounttype = ttk.Label(form_frame, text="Betragstyp:")
        self.label_amounttype.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.combo_amounttype = ttk.Combobox(form_frame, values=["+", "-"],
                                             state="readonly")
        self.combo_amounttype.current(1)
        self.combo_amounttype.grid(row=3, column=1, padx=5, pady=5,
                                   sticky="ew")
        self.combo_amounttype.bind("<Return>",
                                   self.show_amounttype_dropdown)

        # Amount
        self.label_amount = ttk.Label(form_frame, text="Betrag:")
        self.label_amount.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_amount = ttk.Entry(form_frame)
        self.entry_amount.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Purpose
        self.label_purpose = ttk.Label(form_frame, text="Zweck:")
        self.label_purpose.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.entry_purpose = ttk.Entry(form_frame)
        self.entry_purpose.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        # Counterparty
        self.label_counterparty = ttk.Label(form_frame, text="Counterparty:")
        self.label_counterparty.grid(row=6, column=0, padx=5, pady=5,
                                     sticky="w")
        self.combo_counterparty = ttk.Combobox(form_frame)
        self.combo_counterparty.grid(row=6, column=1, padx=5, pady=5,
                                     sticky="ew")
        self.load_counterparties()
        self.combo_counterparty.bind("<Return>",
                                     self.update_counterparty_list)
        # Counterparty erstellen Button
        self.btn_create_counterparty = ttk.Button(
            form_frame,
            text="Counterparty erstellen",
            command=self.create_counterparty
            )
        self.btn_create_counterparty.grid(row=6, column=2, padx=5, pady=5)
        self.btn_create_counterparty.bind("<Return>",
                                          self.create_counterparty)

        # Category
        self.label_category = ttk.Label(form_frame, text="Kategorie:")
        self.label_category.grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.combo_category = ttk.Combobox(form_frame)
        self.combo_category.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
        self.load_categories()
        # Category erstellen Button
        self.btn_create_category = ttk.Button(
            form_frame,
            text="Kategory erstellen",
            command=self.create_category
            )
        self.btn_create_category.grid(row=7, column=2, padx=5, pady=5)
        self.btn_create_category.bind("<Return>",
                                      self.create_category)


#######################################################

        # Speichern-/Update-Button
        self.btn_save = ttk.Button(form_frame, text="Speichern",
                                   command=self.save_transaction)
        self.btn_save.grid(row=10, column=0, columnspan=2, padx=5, pady=10)
        self.btn_save.bind("<Return>",
                           self.save_transaction)
        # Neue Zeile: Abbrechen-Button (zum Formular leeren)
        self.btn_cancel = ttk.Button(form_frame, text="Abbrechen",
                                     command=self.clear_form)
        self.btn_cancel.grid(row=11, column=0, columnspan=2, padx=5, pady=10)

        # Rechte Seite: Treeview in einem LabelFrame, mit Transaktionen
        list_frame = ttk.LabelFrame(self, text="Transaktionen")
        list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Update Treeview-Definition: füge "Kategorie" und "Counterparty" hinzu
        columns = ("Date", "Amount", "Purpose", "Category", "Counterparty")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings",
                                 selectmode="browse")
        self.tree.heading("Date", text="Datum")
        self.tree.heading("Amount", text="Betrag")
        self.tree.heading("Purpose", text="Zweck")
        self.tree.heading("Category", text="Kategorie")
        self.tree.heading("Counterparty", text="Counterparty")
        self.tree.column("Date", width=100)
        self.tree.column("Amount", width=100)
        self.tree.column("Purpose", width=150)
        self.tree.column("Category", width=100)
        self.tree.column("Counterparty", width=150)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar für Treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                  command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Neuen Button "Load MT940" hinzufügen
        self.btn_load_mt940 = ttk.Button(list_frame, text="Load MT940",
                                         command=self.load_mt940)
        self.btn_load_mt940.grid(row=1, column=0, columnspan=2, pady=5)
        # Neuer Button: Reload Treeview
        self.btn_reload = ttk.Button(list_frame, text="Reload Treeview",
                                     command=self.load_transactions)
        self.btn_reload.grid(row=2, column=0, columnspan=2, pady=5)

        # Doppelklick-Event: Details in Formular laden
        self.tree.bind("<Double-1>", self.on_treeview_double_click)

    def set_date_today(self):
        today = datetime.today().strftime("%y%m%d")
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, today)

    def load_accounts(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT str_AccountName FROM tbl_Account')
        accounts = [row[0] for row in cursor.fetchall()]
        conn.close()
        if not accounts:
            self.combo_account['values'] = ["Keine Konten vorhanden"]
        else:
            self.combo_account['values'] = accounts

    def create_account(self):
        # Neues Fenster zum Erstellen eines Kontos
        top = tk.Toplevel(self)
        top.title("Neues Konto erstellen")
        top.geometry("300x150")
        # Label und Eingabe für Kontonamen
        ttk.Label(top, text="Kontoname:").grid(row=0, column=0, padx=10,
                                               pady=10, sticky="w")
        entry_name = ttk.Entry(top)
        entry_name.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        # Label und Eingabe für IBAN
        ttk.Label(top, text="IBAN:").grid(row=1, column=0, padx=10,
                                          pady=10, sticky="w")
        entry_iban = ttk.Entry(top)
        entry_iban.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        def save_new_account():
            name = entry_name.get().strip()
            iban = entry_iban.get().strip()
            if not name or not iban:
                # ...optional: Fehlermeldung anzeigen...
                return
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO tbl_Account
                           (str_AccountName, str_AccountNumber, i8_UserID)
                           VALUES (?, ?, 1)""", (name, iban))
            conn.commit()
            conn.close()
            self.load_accounts()
            top.destroy()

        btn_save_account = ttk.Button(top, text="Speichern",
                                      command=save_new_account)
        btn_save_account.grid(row=2, column=0, columnspan=2, pady=10)
        top.grab_set()

    def load_counterparties(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT str_CounterpartyName FROM tbl_Counterparty')
        counterparties = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.combo_counterparty['values'] = counterparties

    def update_counterparty_list(self, event):
        typed_text = self.combo_counterparty.get()
        if (typed_text == ''):
            data = self.combo_counterparty['values']
        else:
            data = [item for item in self.combo_counterparty['values']
                    if typed_text.lower() in item.lower()]
        self.combo_counterparty['values'] = data
        self.combo_counterparty.event_generate('<Down>')

    def show_amounttype_dropdown(self):
        pass
        # self.combo_amounttype.event_generate('<Down>')

    def create_counterparty():
        # Neues Fenster zum Erstellen einer Counterparty
        top = tk.Toplevel(self)
        top.title("Neue Counterparty erstellen")
        top.geometry("300x150")
        # Label und Eingabe für Counterparty-Namen
        ttk.Label(top, text="Counterparty Name:").grid(row=0, column=0,
                                                       padx=10, pady=10,
                                                       sticky="w")
        entry_name = ttk.Entry(top)
        entry_name.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        def save_new_counterparty():
            name = entry_name.get().strip()
            if not name:
                # ...optional: Fehlermeldung anzeigen...
                return
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tbl_Counterparty (str_CounterpartyName,"
                " i8_UserID) VALUES (?, 1)",
                (name,)
            )
            conn.commit()
            conn.close()
            self.load_counterparties()
            top.destroy()

        btn_save = ttk.Button(top, text="Speichern",
                              command=save_new_counterparty)
        btn_save.grid(row=1, column=0, columnspan=2, pady=10)
        top.grab_set()

    def load_categories(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT str_CategoryName FROM tbl_Category')
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.combo_category['values'] = categories

    def create_category(self):
        top = tk.Toplevel(self)
        top.title("Neue Kategorie erstellen")
        top.geometry("300x150")
        ttk.Label(top, text="Kategoriename:").grid(row=0, column=0, padx=10,
                                                   pady=10, sticky="w")
        entry_name = ttk.Entry(top)
        entry_name.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        def save_new_category():
            name = entry_name.get().strip()
            if not name:
                return
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tbl_Category (str_CategoryName, i8_UserID)"
                " VALUES (?, 1)",
                (name,)
            )
            conn.commit()
            conn.close()
            self.load_categories()
            top.destroy()

        btn_save = ttk.Button(top, text="Speichern", command=save_new_category)
        btn_save.grid(row=1, column=0, columnspan=2, pady=10)
        top.grab_set()

    def save_transaction(self):
        # Eingabedaten sammeln
        date = self.entry_date.get()
        amount = self.entry_amount.get()
        purpose = self.entry_purpose.get()
        amount_type = self.combo_amounttype.get()
        account_name = self.combo_account.get()
        counterparty = self.combo_counterparty.get()
        category_name = self.combo_category.get()
        i8_amounttype = 1 if amount_type == "+" else 0

        # Hole Account-ID anhand des Namens
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT i8_AccountID FROM tbl_Account WHERE str_AccountName = ?',
            (account_name,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            account_id = row[0]
        else:
            account_id = None
        if account_id is None:
            return

        # Hole Kategorie-ID anhand des Namens
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT i8_CategoryID FROM tbl_Category WHERE"
            " str_CategoryName = ?",
            (category_name,)
        )
        row = cursor.fetchone()
        conn.close()
        category_id = row[0] if row else 1

        conn = None
        for _ in range(5):  # Retry-Mechanismus
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                # Prüfe, ob Counterparty existiert
                cursor.execute(
                    "SELECT i8_CounterpartyID FROM tbl_Counterparty WHERE"
                    " str_CounterpartyName = ?",
                    (counterparty,)
                )
                result = cursor.fetchone()
                if result:
                    counterparty_id = result[0]
                else:
                    cursor.execute(
                        "INSERT INTO tbl_Counterparty (str_CounterpartyName)"
                        " VALUES (?)",
                        (counterparty,)
                    )
                    counterparty_id = cursor.lastrowid
                if self.current_transaction_id:
                    cursor.execute(
                        "UPDATE tbl_Transaction SET i8_Date = ?,"
                        " real_Amount = ?, str_Purpose = ?, i8_AmountType = ?,"
                        " i8_AccountID = ?, i8_CounterpartyID = ?,"
                        " i8_CategoryID = ? WHERE i8_TransactionID = ?",
                        (date, amount, purpose, i8_amounttype, account_id,
                         counterparty_id, category_id,
                         self.current_transaction_id)
                    )
                    conn.commit()
                    self.current_transaction_id = None
                    self.btn_save.config(text="Speichern")
                else:
                    cursor.execute(
                        "INSERT INTO tbl_Transaction (i8_Date, real_Amount,"
                        " str_Purpose, i8_AmountType, i8_AccountID,"
                        " i8_CounterpartyID, i8_CategoryID)"
                        " VALUES (?,?,?,?,?,?,?)",
                        (date, amount, purpose, i8_amounttype, account_id,
                         counterparty_id, category_id)
                    )
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
        # Query angepasst: LEFT JOIN statt JOIN für tbl_Counterparty
        cursor.execute(
            'SELECT t.i8_TransactionID, t.i8_Date, t.real_Amount, t.str_Purpose, '
            'c.str_CategoryName, cp.str_CounterpartyName '
            'FROM tbl_Transaction t '
            'JOIN tbl_Category c ON t.i8_CategoryID = c.i8_CategoryID '
            'LEFT JOIN tbl_Counterparty cp ON t.i8_CounterpartyID = cp.i8_CounterpartyID'
        )
        for row in cursor.fetchall():
            trans_id, date, amount, purpose, category, counterparty = row
            # Falls kein Counterparty-Name vorhanden ist, setze leeren String
            if counterparty is None:
                counterparty = ""
            self.tree.insert("", "end", iid=trans_id,
                             values=(date, amount, purpose, category, counterparty))
        conn.close()

    def on_treeview_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            trans_id = selected_item[0]
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Hole zusätzlich i8_CategoryID
            cursor.execute(
                'SELECT i8_Date, real_Amount, str_Purpose, i8_AmountType, i8_AccountID, i8_CounterpartyID, i8_CategoryID FROM tbl_Transaction WHERE i8_TransactionID = ?',
                (trans_id,)
            )
            result = cursor.fetchone()
            conn.close()
            if result:
                date, amount, purpose, amt_type, account_id, cp_id, cat_id = result
                self.entry_date.delete(0, tk.END)
                self.entry_date.insert(0, date)
                self.entry_amount.delete(0, tk.END)
                self.entry_amount.insert(0, amount)
                self.entry_purpose.delete(0, tk.END)
                self.entry_purpose.insert(0, purpose)
                self.combo_amounttype.set("+" if amt_type == 1 else "-")
                # Hole Accountnamen anhand der Account-ID
                conn2 = sqlite3.connect(DB_PATH)
                cursor2 = conn2.cursor()
                cursor2.execute(
                    'SELECT str_AccountName FROM tbl_Account WHERE i8_AccountID = ?',
                    (account_id,)
                )
                row = cursor2.fetchone()
                account_name = row[0] if row else ""
                conn2.close()
                self.combo_account.set(account_name)
                # Hole Counterparty-Namen
                conn3 = sqlite3.connect(DB_PATH)
                cursor3 = conn3.cursor()
                cursor3.execute(
                    'SELECT str_CounterpartyName FROM tbl_Counterparty WHERE i8_CounterpartyID = ?',
                    (cp_id,)
                )
                row = cursor3.fetchone()
                cp_name = row[0] if row else ""
                conn3.close()
                self.combo_counterparty.set(cp_name)
                # Hole Kategorienamen anhand der Kategorie-ID
                conn4 = sqlite3.connect(DB_PATH)
                cursor4 = conn4.cursor()
                cursor4.execute(
                    'SELECT str_CategoryName FROM tbl_Category WHERE i8_CategoryID = ?',
                    (cat_id,)
                )
                row4 = cursor4.fetchone()
                cat_name = row4[0] if row4 else ""
                conn4.close()
                self.combo_category.set(cat_name)
                self.current_transaction_id = trans_id
                self.btn_save.config(text="Änderungen speichern")

    def clear_form(self):
        self.entry_date.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.entry_purpose.delete(0, tk.END)
        self.combo_amounttype.set("+")
        self.combo_account.set("")
        self.combo_counterparty.set("")
        self.current_transaction_id = None
        self.btn_save.config(text="Speichern")

    def load_mt940(self):
        load_file()  # Ruft die MT940-Lade-Funktion aus utils_mt940_loader.py auf
        self.load_transactions()  # Treeview nach MT940-Import neu laden


if __name__ == "__main__":
    app = TransactionApp()
    app.mainloop()
