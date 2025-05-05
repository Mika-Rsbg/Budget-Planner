import logging
from utils.logging.logger_config import setup_logging
from utils.logging.logging_tools import logg


logger = logging.getLogger(__name__)


@logg
def main() -> None:
    """
    Main function to run the application.
    It creates the database and runs the homepage application.
    """
    from gui.homepage.homepage import Homepage
    from utils.data.createdatabase_utils import create_database

    logger.info("Application started.")

    create_database()

    app = Homepage(fullscreen=False)
    app.run()


if __name__ == "__main__":
    setup_logging()
    main()
