#!/usr/bin/env python3
# Dieses Beispielprogramm ruft die letzten 30 Tage der Konto-Historie ab.
# Voraussetzung: Installation der FinTS-Bibliothek: pip install fints

from fints.client import FinTS3PinTanClient
from datetime import date, timedelta
import getpass

import data.nogithub_infos as nogithub_infos


def get_account_history():
    fin_ts_url = "https://banking-rl3.s-fints-pt-rl.de/fints30"
    bank_code = "39050000"
    username = input("username: ")
    pin = getpass.getpass(prompt="Pin: ")
    product_id = nogithub_infos.product_id

    # Initialisieren des FinTS-Clients inklusive Produkt-ID
    client = FinTS3PinTanClient(server=fin_ts_url,
                                bank_identifier=bank_code,
                                user_id=username,
                                pin=pin,
                                product_id=product_id)

    try:
        # Abrufen der SEPA-Konten (Kontenliste)
        accounts = client.get_sepa_accounts()
    except Exception as e:
        print("Fehler beim Abrufen der Konten:", e)
        return

    if not accounts:
        print("Keine Konten gefunden.")
        return

    # Verwende das erste Konto in der Liste
    account = accounts[0]
    print("Konto gefunden:", account)

    # Definiere den Zeitraum: letzte 30 Tage
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()

    try:
        # Abrufen der Transaktionen im definierten Zeitraum
        transactions = client.get_transactions(account, start_date, end_date)
    except Exception as e:
        print("Fehler beim Abrufen der Transaktionen:", e)
        return

    if not transactions:
        print("Keine Transaktionen im angegebenen Zeitraum gefunden.")
    else:
        print("Transaktionen der letzten 30 Tage:")
        for t in transactions:
            print(t)


if __name__ == '__main__':
    get_account_history()
