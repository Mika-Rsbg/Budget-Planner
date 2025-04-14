import tkinter as tk
from tkinter import ttk
from gui.plugins import load_plugins


class BaseWindow(tk.Tk):
    def __init__(self, plugin_scope=None, title="Fenster", geometry="800x600",
                 bg_color="white", fullscreen=False):
        super().__init__()
        # z. B. "homepage", "admin", "einstellungen"
        self.plugin_scope = plugin_scope
        self.title(title)
        self.geometry(geometry)
        self.bg_color = bg_color
        self.configure(bg=bg_color)
        if fullscreen:
            self.state("zoomed")
        self._apply_styles()
        self._setup_main_frame()
        self._setup_status_bar()
        self._setup_menu()
        self.init_ui()

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color)
        style.configure("TButton", background=self.bg_color)
        style.configure("TEntry", fieldbackground=self.bg_color)
        style.configure("TCheckbutton", background=self.bg_color)

    def _setup_main_frame(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    def _setup_status_bar(self):
        self.status_var = tk.StringVar(value="Bereit")
        self.status_bar = ttk.Label(self, textvariable=self.status_var,
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        for plugin in load_plugins("menu", self.plugin_scope):
            if hasattr(plugin, "add_to_menu"):
                plugin.add_to_menu(self, menu_bar)

    def init_ui(self):
        """
        Methode zum Aufbau der Benutzeroberfläche.
        Diese Methode sollte in abgeleiteten Klassen überschrieben werden.
        """
        raise NotImplementedError("init_ui() muss in Unterklassen"
                                  " überschrieben werden.")

    def show_message(self, message):
        """Hilfsmethode zur Ausgabe von einfachen Meldungen."""
        popup = tk.Toplevel(self)
        popup.title("Nachricht")

        label = ttk.Label(popup, text=message, padding=10)
        label.pack()

        button = ttk.Button(popup, text="OK", command=popup.destroy)
        button.pack(pady=10)

        popup.grab_set()  # blockiert das Hauptfenster
        popup.transient(self)  # bleibt im Vordergrund

    def run(self):
        """Startet die tkinter-Hauptschleife."""
        self.mainloop()
