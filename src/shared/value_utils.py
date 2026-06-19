def convert_to_float(value: str) -> float:
    """
    Converts a string to a float. If the string is empty, returns 0.0.
    Args:
        value (str): The string to convert.
    Returns:
        float: The converted float value or 0.0 if the string is empty.
    """
    if value == "":
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0
