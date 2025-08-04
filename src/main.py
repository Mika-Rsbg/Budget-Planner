import logging
from utils.logging.logger_config import setup_logging
from utils.logging.logging_tools import log_fn


logger = logging.getLogger(__name__)


@log_fn
def main() -> None:
    """
    Main function to run the application.
    It creates the database and runs the homepage application.
    """
    from gui.homepage.homepage import Homepage
    from utils.data.createdatabase_utils import create_database

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
    """
    from gui.basewindow import BaseWindow
    from gui.transactionpage.transactionpage import TransactionPage
    from utils.data.createdatabase_utils import create_database

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


if __name__ == "__main__":
    setup_logging()
    logger.info("")
    logger.info("=============== BOOTSTRAP APPLICATION =====================")
    logger.info("")
    main()
    # main_test()
    logger.info("")
    logger.info("=============== SHUTDOWN COMPLETE =========================")
    logger.info("")
