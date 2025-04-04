from tkinter import filedialog
from tkinter import messagebox
import sqlite3
import tkinter as tk


def split_toblocks_mt940(file_content):
    """
    Split the file content into blocks based on the ":" character at the
    beginning of the line.

    Args:
        file_content (str): The content of the file.

    Returns:
        list: A list of blocks.
    """
    # Split nach Zeilenumbruch
    lines = file_content.split('\n')
    blocks = []
    current_block = []

    for line in lines:
        if line.startswith(':'):
            # Wenn bereits ein Block gespeichert ist, füge ihn hinzu
            if current_block:
                blocks.append(''.join(current_block))
            # Starte einen neuen Block mit der Zeile, die mit ":" beginnt
            current_block = [line]
        elif line.strip():  # Wenn die Zeile nicht leer ist (nur Leerzeichen)
            current_block.append(line)

    # Füge den letzten Block hinzu
    if current_block:
        blocks.append(''.join(current_block))
    return blocks


def parse_block(blocks):
    """Parse the blocks and extract the data.

    Args:
        blocks (list): A list of blocks.

    Returns:
        list: A list of dictionaries containing the parsed data.
    """
    parsed_data = []
    temp_purpose_adition = ''

    for block in blocks:
        transaction = {}
        # Verarbeite den Block und extrahiere Daten
        if block.startswith(":20:"):
            temp_reference = block[4:]
        elif block.startswith(":25:"):
            temp_account = block[13:]
        elif block.startswith(":61:"):
            temp_date = block[4:10]
            temp_bookingdate = block[10:14]
            temp_amount_type = 1 if block[14] == 'C' else 0
            amount_start = (block.find('CR') if 'CR' in block
                            else block.find('DR'))
            amount_end = block.find('N', amount_start)
            temp_amount = block[amount_start + 2:block.find('N', amount_start)].replace(',', '.')
        elif block.startswith(":86:"):
            transaction['Reference'] = temp_reference
            transaction['Account'] = temp_account
            transaction['Date'] = temp_date
            transaction['Bookingdate'] = temp_bookingdate
            transaction['AmountType'] = temp_amount_type
            transaction['Amount'] = temp_amount
            transaction['TransactionType'] = block[4:7]
            transaction['str_TransactionType'] = block[10:block.find('?', 10)]

            temp_purpose = block[block.find('?20') + 3: block.find('?', block.find('?20') + 1)]
            if temp_purpose.startswith("SVWZ+"):
                temp_purpose_adition = "SVWZ"
                temp_purpose = temp_purpose[5:]  # Entfernt "SVWZ+" (5 Zeichen)
            elif temp_purpose.startswith("EREF+"):
                temp_purpose_adition = "EREF"
                temp_purpose = temp_purpose[5:]  # Entfernt "EREF+" (5 Zeichen)
            elif temp_purpose.startswith("KREF+"):
                tempt_purpose_adition = "KREF"
                temp_purpose = temp_purpose[5:]  # Entfernt "KREF+" (5 Zeichen)
            transaction['PurposeAddition'] = temp_purpose_adition
            transaction['Purpose'] = temp_purpose

            start_index = block.find('?32') + 3
            end_index = block.find('?', start_index - 2)
            temp_CounterpayName = block[start_index:end_index]
            # Falls der CounterpartyName in zwei Teilen aufgeteilt ist
            if block.find('?33', block.find('?32') + 3) != -1:
                start_index = block.find('?33') + 3
                end_index = block.find('?', start_index - 2)
                temp_CounterpayName += block[start_index:end_index]
            transaction['CounterpartyName'] = temp_CounterpayName

            parsed_data.append(transaction)

            # Setze temporäre Variablen zurück
            temp_date = None
            temp_bookingdate = None
            temp_amount_type = None
            temp_amount = None
            temp_purpose_adition = ''
            temp_purpose = None

    return parsed_data


def check_pattern(new_transaction, existing_transactions):
    import difflib
    import math
    from datetime import datetime

    # Beispiel: Vergleiche Betrag, Datum, Absender und Verwendungszweck
    for trans in existing_transactions:
        # Betragsvergleich
        if not math.isclose(float(new_transaction['Amount']), float(trans['Amount']), rel_tol=0.01):
            continue

        # Datumvergleich (angenommen, die Datumsangaben liegen im Format "YYYYMMDD")
        date_new = datetime.strptime(new_transaction['Date'], "%Y%m%d")
        date_existing = datetime.strptime(trans['Date'], "%Y%m%d")
        if abs((date_new - date_existing).days) > 1:
            continue

        # Absendervergleich (CounterpartyName)
        score = difflib.SequenceMatcher(None, new_transaction['CounterpartyName'], trans['CounterpartyName']).ratio()
        if score < 0.8:
            continue

        # Ähnlicher Verwendungszweck
        score_purpose = difflib.SequenceMatcher(None, new_transaction['Purpose'], trans['Purpose']).ratio()
        if score_purpose < 0.8:
            continue

        # Wenn alle Kriterien erfüllt sind, könnte es ein Muster sein:
        return True, trans['CounterpartyName']
    return False, None


# Beispielhafte Anwendung in deinem Loader:
def insert_transactions(data, DBPath='src/data/database.db'):
    import math
    import difflib
    from datetime import datetime

    conn = sqlite3.connect(DBPath)
    cursor = conn.cursor()

    # Hier könntest du alle vorhandenen Transaktionen laden, um Muster zu vergleichen
    cursor.execute("SELECT str_CounterpartyName, i8_Date, real_Amount, str_Purpose FROM tbl_Transaction")
    existing_transactions = [{
        'CounterpartyName': row[0],
        'Date': str(row[1]),
        'Amount': row[2],
        'Purpose': row[3]
    } for row in cursor.fetchall()]

    for entry in data:
        # Vorherige Umwandlungen wie in deinem Code...
        Account = int(entry['Account'])
        Date = int(entry['Date'])
        AmountType = int(entry['AmountType'])
        Amount = float(entry['Amount'])
        PurposeAdd = entry['PurposeAddition']
        Purpose = entry['Purpose']
        if PurposeAdd:
            str_Purpose = (PurposeAdd + " " + Purpose).strip()
        else:
            str_Purpose = Purpose
        CounterpartyName = entry['CounterpartyName']
        Category = 1
        UserComments = None
        DisplayedName = CounterpartyName

        # Hier prüfen wir auf Muster
        new_trans = {
            'CounterpartyName': CounterpartyName,
            'Date': str(Date),
            'Amount': Amount,
            'Purpose': str_Purpose
        }
        pattern_found, matched_name = check_pattern(new_trans, existing_transactions)
        if pattern_found:
            # Hier könntest du den Nutzer fragen, ob er das Muster anpassen möchte:
            # z.B. über eine Dialogbox in tkinter (messagebox.askquestion, etc.)
            print(f"Muster gefunden: {CounterpartyName} ähnelt {matched_name}. Bitte um Bestätigung.")
            # Anschließend den Namen anpassen, wenn gewünscht.

        # Counterparty prüfen (wie in deinem bestehenden Code)
        cursor.execute(
            "SELECT i8_CounterpartyID FROM tbl_Counterparty "
            "WHERE str_CounterpartyName = ?",
            (CounterpartyName,)
        )
        counterparty = cursor.fetchone()
        if counterparty:
            counterparty_id = counterparty[0]
        else:
            cursor.execute(
                "INSERT INTO tbl_Counterparty "
                "(str_CounterpartyName) VALUES (?)",
                (CounterpartyName,)
            )
            counterparty_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO tbl_Transaction (i8_AccountID, i8_Date, "
            "i8_AmountType, real_Amount, str_Purpose, "
            "i8_CounterpartyID, i8_CategoryID, "
            "str_UserComments, str_DisplayedName) VALUES "
            "(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (Account, Date, AmountType, Amount, str_Purpose,
             counterparty_id, Category, UserComments, DisplayedName)
        )
    conn.commit()
    conn.close()


def load_file():
    """Load the file and parse the data."""
    LoadNew = messagebox.askquestion("MT940 Loader",
                                     "Möchten sie Kontoauszüge laden?",
                                     default='no', icon='question')
    if LoadNew == messagebox.NO:
        return

    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"),
                                                      ("All Files", "*.*")])
    if not file_path:
        return

    with open(file_path, 'r') as file:
        content = file.read()

    blocks = split_toblocks_mt940(content)
    transactions = parse_block(blocks)
    insert_transactions(transactions)


def create_gui():
    root = tk.Tk()
    root.title("Budget Planner")
    btn_loader = tk.Button(root, text="MT940 Loader",
                           command=load_file)
    btn_loader.pack(padx=10, pady=10)
    root.mainloop()


if __name__ == "__main__":
    create_gui()
