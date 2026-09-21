from models.category.entity import Category


def get_category_names(data: list[Category]) -> list[str]:
    """Returns the names of the given categories."""
    return [category.name for category in data]


def get_category_id_name_mapping(data: list[Category]) -> dict[int, str]:
    """Creates a mapping from category IDs to category names."""
    return {category.id: category.name for category in data}


def get_category_name_id_mapping(data: list[Category]) -> dict[str, int]:
    """Creates a mapping from category Names to category id."""
    return {category.name: category.id for category in data}
