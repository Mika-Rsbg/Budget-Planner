import sqlite3
from pathlib import Path
from typing import List, Optional
import logging
from core.database.connection import DatabaseConnection
from models.category.entity import Category
import config


logger = logging.getLogger(__name__)


class Error(Exception):
    """Base class for errors in the category utilities module."""
    pass


def get_category_data(
        db_path: Path = config.Database.PATH
        ) -> List[Category]:
    """
    Retrieves category data from the database.
    Args:
        db_path (Path): Path to the SQLite database file.
    Returns:
        (List): A list of Categorys containing the category data.
    Raises:
        Error: If there is a database error .
    """
    category_data: List[Category] = []
    try:
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")

    columns = ["i8_CategoryID", "str_CategoryName",
               "real_Budget", "i8_BudgetPeriodID"]

    query = "SELECT "
    for col in columns:
        query += f"{col}, "
    query = query[:-2] + " FROM tbl_Category"

    try:
        cursor.execute(query)
        raw_category_data = cursor.fetchall()
        logger.debug("Category data retrieved successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error querying data: {e}")
        raise Error(f"Error querying data: {e}")
    finally:
        DatabaseConnection.close_cursor()

    if not raw_category_data:
        logger.warning("No category data found.")
    else:
        for entry in raw_category_data:
            category = Category(
                id=entry[0],
                name=entry[1],
                budget=entry[2],
                budget_period_id=entry[3]
            )
            category_data.append(category)

    return category_data


def get_category_by_id(
        id: int, db_path: Path = config.Database.PATH
        ) -> Optional[Category]:
    """
    Retrieves a category by its identifier.

    Args:
        id (int): The identifier of the category to retrieve.
        db_path (Path): Path to the SQLite database file.
    Returns:
        Optional[Category]: The matching category, or None if it is not found.
    Raises:
        Error: If there is a database error while retrieving category data.
    """

    category_list = get_category_data(db_path)

    for category in category_list:
        if category.id == id:
            return category

    return None
