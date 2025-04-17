import datetime
import calendar


def get_month_literal(month: int = None, en: bool = False) -> str:
    """
    Returns the month name for a given month number.

    If no month is provided, the current month is used.
    When 'en' is False (default), the month name is returned in German.
    When 'en' is True, the month name is returned in English.

    Args:
        month (int, optional): Month number (1-12). Defaults to None.
        en (bool, optional): If True, returns the month name in English.
                             Defaults to False (returns German month name).

    Returns:
        str: Month name in the selected language.
    """
    if month is None:
        month = datetime.datetime.now().month

    if en:
        return calendar.month_name[month]
    else:
        # German month names:
        # Index 0 is kept empty for convenient indexing (1-12)
        german_months = ["", "Januar", "Februar", "März", "April", "Mai",
                         "Juni", "Juli", "August", "September", "Oktober",
                         "November", "Dezember"]
        return german_months[month]
