from typing import List
import tkinter as tk
from tkinter import ttk
import logging
from gui.plugins.__init__ import load_plugins
from utils.logging.logging_tools import log_fn


logger = logging.getLogger(__name__)


class BaseWindow(tk.Tk):
    def __init__(self, plugin_scope: str, title: str = "Fenster",
                 geometry: str = "800x600", bg_color: str = "white",
                 fullscreen: bool = False) -> None:
        """
        Base class for all windows in the application.
        Initializes the main window and sets up the menu, status bar,
        and main frame.

        Args:
            plugin_scope (str): The scope of the plugin.
            title (str): The title of the window.
            geometry (str): The geometry of the window.
            bg_color (str): The background color of the window.
            fullscreen (bool): Whether to start in fullscreen mode.
        """
        super().__init__()
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
    def ask_permission(self, message: str,
                       focus_on: List[bool]) -> None:
        """
        Ask the user for permission to perform an action.

        Args:
            message (str): The message to display in the dialog.
            focus_on (List[bool], optional): [ok_button, cancel_button]
                                             - The buttons to focus on.
        """
        popup = tk.Toplevel(self)
        popup.title("Berechtigung erforderlich")

        label = ttk.Label(popup, text=message, padding=10)
        label.pack()

        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10)

        yes_button = ttk.Button(
            button_frame, text="Ja",
            command=lambda: self._set_permission(popup, True)
        )
        yes_button.pack(side=tk.LEFT, padx=5)
        no_button = ttk.Button(
            button_frame, text="Nein",
            command=lambda: self._set_permission(popup, False)
        )
        no_button.pack(side=tk.LEFT, padx=5)

        popup.grab_set()

        if focus_on is not None:
            if len(focus_on) != 2:
                logger.exception("focus_on must be a list of two booleans")
                raise ValueError("focus_on must be a list of two booleans")
            if focus_on[0]:
                logger.debug("Focusing on yes button")
                yes_button.focus_set()
                yes_button.bind("<Return>", lambda event: yes_button.invoke())
            elif focus_on[1]:
                logger.debug("Focusing on no button")
                no_button.focus_set()
                no_button.bind("<Return>", lambda event: no_button.invoke())

        self.wait_window(popup)
        logger.debug("Permission dialog closed.")

    def _set_permission(self, popup: tk.Toplevel, permission: bool) -> None:
        """
        Set the permission value and destroy the popup window.

        Args:
            popup (tk.Toplevel): The popup window to destroy.
            permission (bool): The permission value to set.
        """
        self.permission = permission
        logger.debug(f"Permission set to {permission}.")
        popup.destroy()

    @log_fn
    def run(self) -> None:
        """Starts the main loop of the application."""
        logger.info("Starting main loop.")
        self.mainloop()

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
