import logging
from core.logging.logger_config import setup_logging
from core.logging.logging_tools import log_fn
import config


logger = logging.getLogger(__name__)


@log_fn
def main() -> None:
    """
    Main function to run the application.
    It creates the database and runs the homepage application.
    """
    from gui.pages.home.homepage import Homepage
    from core.database.schema import create_database

    logger.info("")
    logger.info("################### APPLICATION STARTED ###################")
    logger.info("")

    create_database()

    app = Homepage(fullscreen=True)
    app.run()

    logger.info("")
    logger.info("################### APPLICATION FINISHED ##################")
    logger.info("")


def main_test() -> None:
    """
    Test function to run the application in test mode.
    It creates the database and runs the homepage application in test mode.
    Logs in a test log file.
    """
    from gui.app.basewindow import BaseWindow
    from gui.pages.transaction.import_overview import ImportOverview
    from core.database.schema import create_database

    logger.info("")
    logger.info("################### TEST MODE STARTED #####################")
    logger.info("")
    create_database()
    app = BaseWindow(
        title="Test Transaction Page",
        geometry="500x600",
        bg_color="white",
        plugin_scope="test",
        auto_ui_init=False
    )
    app.withdraw()  # Hide the root window
    transaction_page = ImportOverview(parent=app, plugin_scope="test")
    app.wait_window(transaction_page)
    app.destroy()


def main_fn_test() -> None:
    """
    Test function to run a function of the code.
    It creates the database.
    Logs in a test log file.
    """
    from datetime import date
    from core.database.schema import create_database
    from features.account.account_history_repository import (
        get_total_cash_history
    )

    logger.info("")
    logger.info(
        "################### FUNCTION TEST MODE STARTED #####################"
    )
    logger.info("")
    create_database()
    print(get_total_cash_history(start_date=date(2024, 12, 1)))


if __name__ == "__main__":
    TEST_MODE: bool = True
    if TEST_MODE:
        config.Logging.set_to_test_mode()
    setup_logging()

    logger.info("")
    logger.info("=============== BOOTSTRAP APPLICATION =====================")
    logger.info("")
    # main()
    main_test()
    # main_fn_test()
    logger.info("")
    logger.info("=============== SHUTDOWN COMPLETE =========================")
    logger.info("")
