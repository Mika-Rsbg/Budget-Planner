class DatabaseMT940Error(Exception):
    """General exception class for database errors."""
    pass


class InvalidMT940FileError(Exception):
    """Exceoption class for errors during the file parsing."""
    pass
