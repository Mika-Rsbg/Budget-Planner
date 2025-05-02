from gui.homepage.homepage import Homepage
from utils.data.createdatabase_utils import create_database


def main() -> None:
    """
    Main function to run the application.
    It creates the database and runs the homepage application.
    """
    create_database()
    app = Homepage(fullscreen=False)
    app.run()


if __name__ == "__main__":
    main()
