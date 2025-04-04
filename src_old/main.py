from utils.manuel_adding.utils_addtransaction import TransactionApp
from utils.utils_createdatabase import create_database


def main():
    create_database()
    app = TransactionApp()
    app.mainloop()


if __name__ == '__main__':
    main()
