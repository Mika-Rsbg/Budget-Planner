import tkinter as tk
from tkinter import ttk
import logging
from gui.basewindow import BaseWindow
from utils.logging.logging_tools import log_fn
from gui.plugins.__init__ import load_plugins


logger = logging.getLogger(__name__)


class BaseToplevelWindow(tk.Toplevel):
    def __init__(self, master: BaseWindow, plugin_scope: str,
                 title: str = "Fenster", geometry: str = "600x400",
                 bg_color: str = "white") -> None:
        """
        Init an instance of the BaseToplevelWindow class.

        Args:
            master (tk.Tk): The parent window.
            plugin_scope (str): The scope for loading plugins.
            title (str): The title of the window.
            geometry (str): The size of the window.
            bg_color (str): The background color of the window.
        """
        super().__init__(master)
        self.master = master
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

    @log_fn
    def init_ui(self) -> None:
        """
        Methode to initialize the user interface.
        This method needs to be overridden in subclasses.
        It is called after the main frame, status bar and the menu
        have been set up.
        """
        logger.error("init_ui() not implemented in subclass")
        raise NotImplementedError(
            "init_ui() needs to be implemented in subclasses"
        )

    @log_fn
    def show_message(self, message: str) -> None:
        """
        Helpmethod that shows a message in a popup window.

        Args:
            message (str): The message to display.
        """
        popup = tk.Toplevel(self)
        popup.title("Nachricht")

        label = ttk.Label(popup, text=message, padding=10)
        label.pack()

        button = ttk.Button(popup, text="OK", command=popup.destroy)
        button.pack(pady=10)

        popup.grab_set()
        popup.transient(self)

    @log_fn
    def reload(self) -> None:
        """
        Destroys all widgets in the main frame and reinitializes the UI.
        """
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        logger.debug("Destroyed all widgets in the main frame.")
        self.init_ui()
        logger.info("Reloaded the UI.")
