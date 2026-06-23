import re
import os
from tkinter import Tk, filedialog


def anonymize_ibans_in_log():
    # Suppress the Tkinter root window
    root = Tk()
    root.withdraw()

    # Open file dialog to select the log file
    file_path = filedialog.askopenfilename(
        title="Select Log File",
        filetypes=[("Log Files", "*.log"), ("Text Files", "*.txt"),
                   ("All Files", "*.*")]
    )

    if not file_path:
        print("No file selected.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace IBANs, 10-digit numbers, float numbers,
        # strings in single quotes, and dates (YYMMDD) with #
        anonymized_content = re.sub(
            r'(\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b|\b\d{10}\b|\b\d+\.\d+\b|'
            r'\'[^\']*\'|\b\d{6}\b)',
            lambda match: '#' * len(match.group()),
            content
        )

        # Remove lines containing specific debug messages
        lines = anonymized_content.splitlines()
        filtered_lines = [line for line in lines if not (
            "utils.logging.logging_tools - wrapper - [DEBUG]" in line or
            "utils.data.database_connection - get_connection - [DEBUG]" in line
        )]
        anonymized_content = '\n'.join(filtered_lines)

        # Create a copy of the file with '_zensiert' appended to the name
        dir_name, base_name = os.path.split(file_path)
        name, ext = os.path.splitext(base_name)
        new_file_path = os.path.join(dir_name, f"{name}_zensiert{ext}")

        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.write(anonymized_content)

        print("IBANs have been anonymized successfully.")
        print(f"Anonymized file saved as: {new_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    anonymize_ibans_in_log()
