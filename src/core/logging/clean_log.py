import tkinter as tk
from tkinter import filedialog
import os


def main():
    # GUI-Fenster verstecken
    root = tk.Tk()
    root.withdraw()

    # Datei auswählen
    file_path = filedialog.askopenfilename(
        title="Log-Datei auswählen",
        filetypes=[("Log-Dateien", "*.log"), ("Alle Dateien", "*.*")]
    )

    if not file_path:
        print("Keine Datei ausgewählt.")
        return

    # Ausgabe-Dateipfad
    base, ext = os.path.splitext(file_path)
    output_path = f"{base}_cleaned{ext}"

    try:
        with open(file_path, "r", encoding="utf-8") as infile:
            lines = infile.readlines()

        cleaned_lines = [line for line in lines if
                         "utils.logging.logging_tools" not in line]

        with open(output_path, "w", encoding="utf-8") as outfile:
            outfile.writelines(cleaned_lines)

        print(f"Bereinigte Datei gespeichert unter: {output_path}")

    except Exception as e:
        print(f"Fehler beim Verarbeiten der Datei: {e}")


if __name__ == "__main__":
    main()
