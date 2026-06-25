import logging
import tksheet
import csv
from pathlib import Path
from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow
from features.importer.mt940.importer import import_mt940_file_gui


logger = logging.getLogger(__name__)


def save_to_csv(
    file_path: Path,
    header: list[str],
    data: list[list],
) -> None:
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(header)
        writer.writerows(data)


class ImportOverview(BaseToplevelWindow):
    def __init__(self, parent: BaseWindow, plugin_scope: str,
                 title="Transactions Importer Page",
                 geometry="500x600", bg_color="white") -> None:
        self.parent = parent
        (header, data) = import_mt940_file_gui(self.parent)
        self.sheet_header = header
        self.sheet_data = data
        super().__init__(parent, plugin_scope, title, geometry, bg_color)

    def init_ui(self) -> None:
        save_to_csv(
            Path("transactions_nogithub.csv"),
            self.sheet_header,
            self.sheet_data,
        )
        self.sheet = tksheet.Sheet(
            self.main_frame,
            headers=self.sheet_header,
            data=self.sheet_data,
            auto_resize_columns=20
        )

        self.sheet.enable_bindings()
        self.sheet.pack(fill="both", expand=True)
