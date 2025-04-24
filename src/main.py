from gui.homepage.homepage import Homepage
from utils.data.createdatabase_utils import create_database
from gui.cashpage.cashpage import CashPage
from gui.basewindow import BaseWindow


def main():
    create_database()
    app = Homepage(fullscreen=False)
    # open_cash_page(app)
    app.run()


def open_cash_page(window: BaseWindow) -> None:
    """Open the account page.

    Args:
        window: parent window
        account_selection_needed (bool)
    """
    cash_page = CashPage(window)
    window.withdraw()  # Hide the parent window
    window.wait_window(cash_page)
    window.deiconify()  # Show the parent window again
    window.reload()  # Reload the parent window to refresh the UI


if __name__ == "__main__":
    main()
