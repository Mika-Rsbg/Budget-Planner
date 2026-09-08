from typing import List, Dict
from models.category.entity import Category


def get_category_names(data: List[Category]) -> List[str]:
    """Returns the names of the given categories."""
    return [category.name for category in data]


def get_category_id_name_mapping(data: List[Category]) -> Dict[int, str]:
    """Creates a mapping from category IDs to category names."""
    return {
        category.id: category.name
        for category in data
    }


def get_category_name_id_mapping(data: List[Category]) -> Dict[str, int]:
    """Creates a mapping from category Names to category id."""
    return {
        category.name: category.id
        for category in data
    }
