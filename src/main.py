from gui.homepage.homepage import Homepage
from utils.data.createdatabase_utils import create_database


def main() -> None:
    create_database()
    app = Homepage(fullscreen=False)
    app.run()


if __name__ == "__main__":
    main()
