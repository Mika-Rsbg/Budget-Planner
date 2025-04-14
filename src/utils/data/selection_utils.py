import datetime
import calendar


def get_month_literal(month: int = None) -> str:
    """Gibt den Monatsnamen in deutscher Sprache zurück.
    Wenn kein Monat angegeben wird, wird der aktuelle Monat verwendet.

    Args:
        month (int, optional): Monatszahl (1-12). Defaults to None.

    Returns:
        str: Monatsname in deutscher Sprache.
    """
    if month is None:
        month = datetime.datetime.now().month
    return calendar.month_name[month]
