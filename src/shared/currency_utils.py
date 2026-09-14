def format_mt940_currency(value: float) -> str:
    """Formats a value as a euro amount with two decimal places."""
    # TODO: add international format support
    # TODO: add custom currency support
    return f"{value:.2f} €".replace(".", ",")
