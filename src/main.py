import logging
from core.logging.logger_config import setup_logging
from core.logging.logging_tools import log_fn


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
    from gui.pages.transaction.transactionpage import TransactionPage
    from core.database.schema import create_database

    logger.info("")
    logger.info("################### TEST MODE STARTED #####################")
    logger.info("")
    create_database()
    app = BaseWindow(
        title="Test Transaction Page",
        geometry="500x600",
        bg_color="white",
        plugin_scope="test"
    )
    app.withdraw()  # Hide the root window
    transaction_page = TransactionPage(parent=app, plugin_scope="test")
    print(transaction_page)
    app.mainloop()


def main_fn_test() -> None:
    """
    Test function to run a function of the code.
    It creates the database.
    Logs in a test log file.
    """
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
    print(get_total_cash_history("2024-12-01", ""))


if __name__ == "__main__":
    import config
    TEST_MODE: bool = False
    if TEST_MODE:
        config.Logging.log_file_name = 'test_log.log'
        config.Logging.log_file_name_no_debug = 'test_log_no_debug.log'
    else:
        pass
    setup_logging()

    logger.info("")
    logger.info("=============== BOOTSTRAP APPLICATION =====================")
    logger.info("")
    main()
    # main_test()
    # main_fn_test()
    logger.info("")
    logger.info("=============== SHUTDOWN COMPLETE =========================")
    logger.info("")
