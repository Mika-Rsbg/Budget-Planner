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


def get_iso_date(date: str = None, today: bool = False) -> str:
    """
    Converts a date string in the format YYMMDD to ISO format YYYY-MM-DD.
    If 'today' is True, returns today's date in ISO format.

    Args:
        date (str, optional): Date string in the format YYMMDD.
        today (bool, optional): If True, returns today's date in ISO format.

    Returns:
        str: Date string in ISO format YYYY-MM-DD.
    """
    if today:
        return datetime.datetime.now().strftime("%Y-%m-%d")

    if date is None or len(date) != 6 or not date.isdigit():
        raise ValueError("Date must be a string in the format YYMMDD.")

    year = int(date[:2])
    month = int(date[2:4])
    day = int(date[4:6])

    # Jahr 00–69 => 2000–2069, Jahr 70–99 => 1970–1999
    full_year = 2000 + year if year < 70 else 1900 + year

    dt = datetime.datetime(full_year, month, day)
    return dt.strftime("%Y-%m-%d")
