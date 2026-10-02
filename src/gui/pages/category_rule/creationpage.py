from gui.app.basetoplevelwindow import BaseToplevelWindow
from gui.app.basewindow import BaseWindow


class CategoryRuleCreationPage(BaseToplevelWindow):
    def __init__(
        self,
        master: BaseWindow,
        plugin_scope: str = "automationcreation",
        title: str = "Kategorie Zuordnungsregel erstellen",
        geometry: str = "600x160",
    ) -> None:
        self.final_selected_category: int | None = None
        super().__init__(master, plugin_scope, title, geometry)

    def init_ui(self) -> None:
        pass
