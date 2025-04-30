import tkinter as tk
from tkinter import ttk
from gui.plugins import load_plugins


class BaseToplevelWindow(tk.Toplevel):
    def __init__(self, master=None, plugin_scope=None, title="Fenster",
                 geometry="600x400", bg_color="white"):
        super().__init__(master)
        self.plugin_scope = plugin_scope
        self.title(title)
        self.geometry(geometry)
        self.bg_color = bg_color
        self.configure(bg=bg_color)
        self._apply_styles()
        self._setup_main_frame()
        self._setup_status_bar()
        self._setup_menu()
        self.init_ui()

    def _apply_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color)
        style.configure("TButton", background=self.bg_color)
        style.configure("TEntry", fieldbackground=self.bg_color)
        style.configure("TCheckbutton", background=self.bg_color)

    def _setup_main_frame(self) -> None:
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    def _setup_status_bar(self) -> None:
        self.status_var = tk.StringVar(value="Bereit")
        self.status_bar = ttk.Label(self, textvariable=self.status_var,
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_menu(self) -> None:
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        for plugin in load_plugins("menu", self.plugin_scope):
            if hasattr(plugin, "add_to_menu"):
                plugin.add_to_menu(self, menu_bar)

    def init_ui(self) -> None:
        raise NotImplementedError("init_ui() muss in Unterklassen"
                                  "überschrieben werden.")

    def show_message(self, message) -> None:
        popup = tk.Toplevel(self)
        popup.title("Nachricht")

        label = ttk.Label(popup, text=message, padding=10)
        label.pack()

        button = ttk.Button(popup, text="OK", command=popup.destroy)
        button.pack(pady=10)

        popup.grab_set()
        popup.transient(self)

    def reload(self) -> None:
        """
        Destroys all widgets in the main frame and reinitializes the UI.
        """
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.init_ui()
