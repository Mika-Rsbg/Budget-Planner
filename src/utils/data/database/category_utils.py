import sqlite3
from pathlib import Path
from typing import List, Tuple, Union
import logging
from utils.data.database_connection import DatabaseConnection
import config


logger = logging.getLogger(__name__)


class Error(Exception):
    """Base class for errors in the category utilities module."""
    pass


def get_category_data(selected_columns: List[bool] = [True, True, True, True],
                      db_path: Path = config.Database.PATH
                      ) -> List[Tuple[Union[str, float, int], ...]]:
    """
    Retrieves category data from the database based on selected columns.
    Args:
        selected_columns (List): A list of booleans indicating which columns
            to retrieve. The order is:
                [i8_CategoryID (int), str_CategoryName (str),
                 real_Budget (float), i8_BudgetPeriodID (int)].
        db_path (Path): Path to the SQLite database file.
    Returns:
        (List): A list of tuples containing the category data.
    Raises:
        Error: If there is a database error or if the number of selected
            columns does not match the expected number of columns.
    """
    try:
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")

    columns = ["i8_CategoryID", "str_CategoryName",
               "real_Budget", "i8_BudgetPeriodID"]

    if len(columns) != len(selected_columns):
        logger.error("Wrong number of selected columns provided."
                     f"Expected {len(columns)}, got {len(selected_columns)}.")
        raise Error("Wrong number of values provided."
                    f"Expected {len(columns)}, got {len(selected_columns)}.")

    query = "SELECT "
    for i, col in enumerate(columns):
        if selected_columns[i]:
            query += f"{col}, "
    query = query[:-2] + " FROM tbl_Category"

    try:
        cursor.execute(query)
        category_data = cursor.fetchall()
        logger.debug("Category data retrieved successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error querying data: {e}")
        raise Error(f"Error querying data: {e}")
    finally:
        DatabaseConnection.close_cursor()
    if not category_data:
        logger.warning("No counterparty data found.")
    return category_data

# region
# def get_category_data(selected_columns: List[bool] = [True,
#                                                       True, True, True],
#                       include_budget_period_name: bool = False,
#                       db_path: Path = config.Database.PATH
#                       ) -> List[Tuple[Union[str, float, int], ...]]:
#     """
#     Retrieves category data from the database based on selected columns.
#     If 'include_budget_period_name' is True, the query returns the budget
#     period name instead of the budget period id.
#     Args:
#         selected_columns (List): A list of booleans indicating which columns
#             to retrieve. The order is:
#                 [i8_CategoryID (int), str_CategoryName (str),
#                  real_Budget (float), i8_BudgetPeriodID or
#                  str_BudgetPeriodName (str)].
#         include_budget_period_name (bool): If True, retrieves the budget
#             period name via a join.
#         db_path (Path): Path to the SQLite database file.
#     Returns:
#         List[Tuple]: A list of tuples containing the category data.
#     Raises:
#         Error: If there is a database error or if no column is selected.
#     """
#     try:
#         cursor = DatabaseConnection.get_cursor(db_path)
#     except sqlite3.Error as e:
#         logger.error(f"Error connecting to database: {e}")
#         raise Error(f"Error connecting to database: {e}")

#     table_category = "tbl_Category"
#     # Build select clause based on selected_columns and the
#     # include_budget_period_name flag.
#     columns = []
#     if selected_columns[0]:
#         columns.append(f"{table_category}.i8_CategoryID")
#     if selected_columns[1]:
#         columns.append(f"{table_category}.str_CategoryName")
#     if selected_columns[2]:
#         columns.append(f"{table_category}.real_Budget")
#     if selected_columns[3]:
#         if include_budget_period_name:
#             columns.append("tbl_BudgetPeriod.str_BudgetPeriodName")
#         else:
#             columns.append(f"{table_category}.i8_BudgetPeriodID")

#     if not columns:
#         logger.error("No columns selected for retrieval.")
#         raise Error("At least one column must be selected for retrieval.")

#     query = "SELECT " + ", ".join(columns) + f" FROM {table_category}"
#     if include_budget_period_name:
#         # Join with tbl_BudgetPeriod to get the budget period name.
#         query += (" INNER JOIN tbl_BudgetPeriod ON tbl_Category."
#                   "i8_BudgetPeriodID = tbl_BudgetPeriod.i8_BudgetPeriodID")

#     try:
#         cursor.execute(query)
#         category_data = cursor.fetchall()
#         logger.debug("Category data retrieved successfully.")
#     except sqlite3.Error as e:
#         logger.error(f"Error querying data: {e}")
#         raise Error(f"Error querying data: {e}")
#     finally:
#         DatabaseConnection.close_cursor()

#     if not category_data:
#         logger.warning("No category data found.")
#     return category_data
# endregion
