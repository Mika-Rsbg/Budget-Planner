import logging
import config


def setup_logging():
    config.Logging.ensure_log_directory_exists()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(funcName)s - [%(levelname)s] -"
        " %(message)s"
    )

    # formatter = logging.Formatter(
    #     "%(asctime)s - %(name)-50s - %(funcName)-30s - [%(levelname)-7s] -"
    #     " %(message)s"
    # )

    # Output to file (DEBUG level) → app.log
    debug_handler = logging.FileHandler(
        config.Logging.LOG_FILE, encoding="utf-8"
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)

    # Output to file (INFO level) → app_no_debug.log
    info_handler = logging.FileHandler(
        config.Logging.LOG_FILE_NO_DEBUG, encoding="utf-8"
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # Output to console (DEBUG level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Change back to DEBUG
    console_handler.setFormatter(formatter)

    # Remove previous handlers (if any)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Add handlers to the logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    # logger.addHandler(console_handler)
