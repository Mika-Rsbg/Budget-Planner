import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re
import difflib

# Datenbankpfad
DB_PATH = 'src/data/database.db'


def fetch_transactions():
    """
    Lädt alle Transaktionen samt der zugehörigen Counterparty-Namen
    aus der Datenbank.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.*, cp.str_CounterpartyName
             FROM tbl_Transaction t
             LEFT JOIN tbl_Counterparty cp
             ON t.i8_CounterpartyID = cp.i8_CounterpartyID
        """)
        transactions = cursor.fetchall()
        return transactions
    except Exception as e:
        print(f"Fehler beim Laden der Transaktionen: {e}")
        return []
    finally:
        if conn:
            conn.close()


def analyze_by_purpose(transactions):
    """
    Gruppiert Transaktionen mit gleichem Purpose.
    """
    groups = {}
    for tx in transactions:
        key = tx["str_Purpose"].strip()
        if key:
            groups.setdefault(key, []).append(tx)
    patterns = []
    for purpose, txs in groups.items():
        if len(txs) > 1:
            patterns.append({
                "description": f"Gleicher Purpose: '{purpose}'",
                "transactions": txs
            })
    return patterns


def analyze_by_counterparty_amount(transactions):
    """
    Gruppiert Transaktionen mit gleichem Counterparty und
    gleichem Betrag.
    """
    groups = {}
    for tx in transactions:
        cp = tx["str_CounterpartyName"] if tx["str_CounterpartyName"] else ""
        key = (cp.strip(), tx["real_Amount"])
        if cp:
            groups.setdefault(key, []).append(tx)
    patterns = []
    for (cp, amount), txs in groups.items():
        if len(txs) > 1:
            patterns.append({
                "description": f"Gleicher Counterparty ('{cp}') und Betrag ({amount})",
                "transactions": txs
            })
    return patterns


def analyze_by_recurring_day(transactions):
    """
    Gruppiert Transaktionen, die am selben Tag (Tag des Monats)
    stattfinden.
    Annahme: i8_Date ist im Format YYMMDD (als Integer oder String).
    """
    groups = {}
    for tx in transactions:
        try:
            date_str = str(tx["i8_Date"]).zfill(6)  # s.a. '230101'
            day = date_str[-2:]
            groups.setdefault(day, []).append(tx)
        except Exception as e:
            print(f"Datumsextraktion fehlgeschlagen: {e}")
    patterns = []
    for day, txs in groups.items():
        if len(txs) > 1:
            patterns.append({
                "description": f"Transaktionen am Tag {day} (möglicher Zyklus)",
                "transactions": txs
            })
    return patterns


def analyze_by_weekday(transactions):
    """
    Gruppiert Transaktionen nach Wochentag basierend auf dem Datum.
    Annahme: i8_Date im Format YYMMDD.
    """
    groups = {}
    for tx in transactions:
        try:
            date_str = str(tx["i8_Date"]).zfill(6)
            dt = datetime.strptime(date_str, "%y%m%d")
            weekday = dt.strftime("%A")
            groups.setdefault(weekday, []).append(tx)
        except Exception as e:
            print(f"Fehler bei Wochentagsanalyse: {e}")
    patterns = []
    for weekday, txs in groups.items():
        if len(txs) > 1:
            patterns.append({
                "description": f"Transaktionen am {weekday}",
                "transactions": txs
            })
    return patterns


def analyze_by_amount_variation(transactions, threshold=1.0):
    """
    Gruppiert Transaktionen basierend auf ähnlichen Beträgen.
    Beträge, die sich um maximal 'threshold' unterscheiden, werden gemeinsam
    gruppiert.
    """
    groups = {}
    for tx in transactions:
        amount = tx["real_Amount"]
        # Gruppierung basierend auf runden Beträgen
        key = round(amount)
        groups.setdefault(key, []).append(tx)
    patterns = []
    for base_amount, txs in groups.items():
        if len(txs) > 1:
            similar_group = [tx for tx in txs if abs(tx["real_Amount"] - base_amount) <= threshold]
            if len(similar_group) > 1:
                patterns.append({
                    "description": f"Ähnliche Beträge um {base_amount} (±{threshold})",
                    "transactions": similar_group
                })
    return patterns


def analyze_by_geographical(transactions):
    """
    Gruppiert Transaktionen, die Hinweise auf Filial- oder
    geografische Zugehörigkeit enthalten.
    Annahme: Filialen/Regionen können anhand von Substrings in
    str_CounterpartyName identifiziert werden (z. B. 'Filiale', 'Store',
    'Branch').
    """
    groups = {}
    keywords = ["Filiale", "Store", "Branch"]
    for tx in transactions:
        cp = tx["str_CounterpartyName"] if tx["str_CounterpartyName"] else ""
        for keyword in keywords:
            if keyword.lower() in cp.lower():
                groups.setdefault(keyword, []).append(tx)
                break
    patterns = []
    for keyword, txs in groups.items():
        if len(txs) > 1:
            patterns.append({
                "description": f"Transaktionen von {keyword}",
                "transactions": txs
            })
    return patterns


def analyze_by_payment_method(transactions):
    """
    Gruppiert Transaktionen nach Zahlungsmittel, falls das Feld
    'str_PaymentMethod' vorhanden ist.
    """
    groups = {}
    for tx in transactions:
        # Prüfe, ob der Schlüssel existiert
        if "str_PaymentMethod" in tx.keys():
            method = tx["str_PaymentMethod"].strip()
            if method:
                groups.setdefault(method, []).append(tx)
    patterns = []
    for method, txs in groups.items():
        if len(txs) > 1:
            patterns.append({
                "description": f"Zahlungsmittel: {method}",
                "transactions": txs
            })
    return patterns


def normalize_text(text):
    """
    Normalisiert den Text: Kleinbuchstaben, Entfernen von Satzzeichen.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()


def analyze_by_text_similarity(transactions):
    """
    Gruppiert Transaktionen anhand des normalisierten Purpose-Textes.
    So können unscharfe Übereinstimmungen (bspw. Tippfehler) erkannt werden.
    """
    groups = {}
    for tx in transactions:
        purp = tx["str_Purpose"].strip()
        norm = normalize_text(purp)
        if norm:
            groups.setdefault(norm, []).append(tx)
    patterns = []
    for norm_text, txs in groups.items():
        if len(txs) > 1:
            patterns.append({
                "description": f"Ähnliche Texte im Purpose: '{norm_text}'",
                "transactions": txs
            })
    return patterns


def normalize_counterparty(name):
    """
    Normalisiert den Counterparty-Namen: Kleinbuchstaben, Zahlen und
    Satzzeichen entfernen.
    """
    name = name.lower()
    name = re.sub(r'[\d]', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    return name.strip()


def analyze_by_similar_counterparty(transactions, similarity_cutoff=0.8):
    """
    Gruppiert Transaktionen anhand ähnlicher Counterparty-Namen.
    Es wird der normalisierte Name verglichen, um Tippfehler und Variationen
    (z.B. "E-Center Cevik" und "E-Center ...") zu erfassen.
    """
    groups = []  # Liste von Tupeln: (group_name, [transactions])
    for tx in transactions:
        cp = tx["str_CounterpartyName"] if tx["str_CounterpartyName"] else ""
        if not cp:
            continue
        norm_cp = normalize_counterparty(cp)
        found = False
        for i, (group_name, tx_list) in enumerate(groups):
            similarity = difflib.SequenceMatcher(None, norm_cp,
                                                 group_name).ratio()
            if similarity >= similarity_cutoff:
                groups[i][1].append(tx)
                found = True
                break
        if not found:
            groups.append((norm_cp, [tx]))
    patterns = []
    for group_name, txs in groups:
        if len(txs) > 1:
            patterns.append({
                "description": f"Ähnliche Counterparty Namen: '{group_name}'",
                "transactions": txs
            })
    return patterns


def analyze_transactions():
    """
    Führt alle Analyseverfahren aus und gibt die Liste aller
    gefundenen Muster zurück.
    """
    transactions = fetch_transactions()
    patterns = []
    # Jeder Analysefunktion können weitere Kriterien hinzugefügt werden
    patterns.extend(analyze_by_purpose(transactions))
    patterns.extend(analyze_by_counterparty_amount(transactions))
    patterns.extend(analyze_by_recurring_day(transactions))
    patterns.extend(analyze_by_weekday(transactions))
    patterns.extend(analyze_by_amount_variation(transactions))
    patterns.extend(analyze_by_geographical(transactions))
    # Neue Kriterien:
    patterns.extend(analyze_by_payment_method(transactions))
    patterns.extend(analyze_by_text_similarity(transactions))
    patterns.extend(analyze_by_similar_counterparty(transactions))
    return patterns


def update_transactions(transactions, new_counterparty, new_category):
    """
    Aktualisiert in der Datenbank alle angegebenen Transaktionen.
    Bspw. wird für jede Transaktion,
    deren Counterparty den Begriff "EdekaFiliale" enthält, der
    Counterparty-Feld auf new_counterparty und Category auf new_category
    gesetzt.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for tx in transactions:
            tx_id = tx["i8_TransactionID"]
            # Update-Befehl anpassen: Hier wird angenommen,
            # dass ein Update in tbl_Transaction erfolgt.
            cursor.execute("""
                UPDATE tbl_Transaction SET
                    i8_CounterpartyID = (SELECT i8_CounterpartyID
                                          FROM tbl_Counterparty
                                          WHERE str_CounterpartyName = ?),
                    i8_CategoryID = (SELECT i8_CategoryID
                                      FROM tbl_Category
                                      WHERE str_CategoryName = ?)
                WHERE i8_TransactionID = ?
            """, (new_counterparty, new_category, tx_id))
        conn.commit()
        messagebox.showinfo("Update", "Transaktionen wurden aktualisiert.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Aktualisieren:\n{e}")
    finally:
        if conn:
            conn.close()


class TransactionPatternGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transaktionsmuster Analyse")
        self.geometry("900x600")
        # Analyse durchführen
        self.patterns = analyze_transactions()
        self.create_widgets()

    def create_widgets(self):
        # Linker Frame: Liste der Muster
        left_frame = ttk.Frame(self)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        ttk.Label(left_frame, text="Gefundene Muster:").pack(anchor="w")
        self.pattern_listbox = tk.Listbox(left_frame, width=50)
        self.pattern_listbox.pack(fill="y", expand=True)
        self.pattern_listbox.bind("<<ListboxSelect>>", self.on_select_pattern)
        # Muster in Listbox hinzufügen
        for pattern in self.patterns:
            self.pattern_listbox.insert("end", pattern["description"])

        # Rechter Frame: Details und Aktionen
        right_frame = ttk.Frame(self)
        right_frame.pack(side="right", fill="both", expand=True, padx=10,
                         pady=10)
        ttk.Label(right_frame, text="Details zum Muster:").pack(anchor="w")
        self.details_text = tk.Text(right_frame, wrap="none")
        self.details_text.pack(fill="both", expand=True)
        # Button zum Anwenden manueller Änderungen
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill="x", pady=5)
        self.apply_btn = ttk.Button(btn_frame, text="Änderungen anwenden",
                                    command=self.apply_changes)
        self.apply_btn.pack(side="left", padx=5)
        # Schließen-Button
        self.close_btn = ttk.Button(btn_frame, text="Schließen",
                                    command=self.destroy)
        self.close_btn.pack(side="right", padx=5)

    def on_select_pattern(self, event):
        # Zeigt bei Auswahl eines Musters
        # Details der enthaltenen Transaktionen.
        selection = event.widget.curselection()
        if not selection:
            return
        index = selection[0]
        pattern = self.patterns[index]
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, f"Beschreibung: {pattern['description']}\n")
        self.details_text.insert(tk.END, "Enthaltene Transaktionen:\n")
        for tx in pattern["transactions"]:
            # Kurze Darstellung jeder Transaktion
            dt = str(tx["i8_Date"]).zfill(6)
            am = tx["real_Amount"]
            purp = tx["str_Purpose"]
            cp = tx["str_CounterpartyName"] if tx["str_CounterpartyName"] else ""
            self.details_text.insert(tk.END, f"ID: {tx['i8_TransactionID']} | Datum: {dt} | Betrag: {am} | Zweck: {purp} | Counterparty: {cp}\n")

    def apply_changes(self):
        # Wendet bei Bedarf manuelle Änderungen an.
        selected = self.pattern_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warnung", "Kein Muster ausgewählt.")
            return
        index = selected[0]
        pattern = self.patterns[index]
        # Beispiel: Falls das Muster einen Hinweis wie "EdekaFiliale" enthält,
        # können die Änderungen vorgeschlagen werden.
        if "EdekaFiliale" in pattern["description"]:
            antwort = messagebox.askyesno(
                "Änderung anwenden",
                "Das Muster enthält 'EdekaFiliale'. Soll Counterparty auf 'Edeka' "
                "und Kategorie auf 'Einkäufe' geändert werden?"
            )
            if antwort:
                update_transactions(pattern["transactions"], "Edeka", "Einkäufe")
        else:
            # Allgemeiner Dialog für manuelle Entscheidung
            antwort = messagebox.askyesno("Änderung anwenden",
                                          "Möchten Sie Änderungen an diesen Transaktionen vornehmen?")
            if antwort:
                # Hier können weitere Logiken implementiert werden.
                messagebox.showinfo("Info", "Manuelle Änderungen werden aktuell nicht "
                                            "automatisch umgesetzt.")
        # Nach Update evtl. erneute Analyse durchführen
        self.patterns = analyze_transactions()
        self.pattern_listbox.delete(0, tk.END)
        for pattern in self.patterns:
            self.pattern_listbox.insert(tk.END, pattern["description"])
        self.details_text.delete("1.0", tk.END)


if __name__ == "__main__":
    app = TransactionPatternGUI()
    app.mainloop()
