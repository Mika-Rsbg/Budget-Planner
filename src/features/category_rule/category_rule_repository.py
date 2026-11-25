import logging
import sqlite3
from pathlib import Path

import config
from core.database.connection import DatabaseConnection
from features.importer.transaction_query.parser import parse_string
from models.category_rule.entity import CategoryRule

logger = logging.getLogger(__name__)


class Error(Exception):
    """General exception class for database errors."""


def add_category_rule(
    rule: CategoryRule, db_path: Path = config.Database.PATH
) -> int:
    """
    Adds a category rule to the database.

    Args:
        rule (CategoryRule): Category rule to insert.
        db_path (Path): Path to the database.

    Returns:
        int: ID of the newly created category rule.

    Raises:
        Error: If the database operation fails.
    """
    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)

        cursor.execute(
            """
            INSERT INTO tbl_CategoryRule (
                i8_CategoryID,
                str_Name,
                i8_Priority,
                i8_Enabled,
                str_Rule
            )
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                rule.category_id,
                rule.name,
                rule.priority,
                int(rule.enabled),
                rule.rule,
            ),
        )

        conn.commit()

        rule_id = cursor.lastrowid

        logger.debug(
            "Category rule '%s' added successfully (ID: %s).",
            rule.name,
            rule_id,
        )

        return rule_id if rule_id is not None else -1
        # TODO: Add better default value handling

    except sqlite3.Error as e:
        logger.exception("Error adding category rule.")
        raise Error(f"Error adding category rule: {e}") from e

    finally:
        DatabaseConnection.close_cursor()


def get_category_rule_data(
    db_path: Path = config.Database.PATH,
) -> list[CategoryRule]:
    # TODO: add docs
    cursor = DatabaseConnection.get_cursor(db_path)

    try:
        cursor.execute(
            """
            SELECT i8_CategoryRuleID,
                    i8_CategoryID,
                    str_Name,
                    i8_Priority,
                    i8_Enabled,
                    str_Rule
            FROM tbl_CategoryRule
            """
        )
        raw_category_rule_data = cursor.fetchall()
        logger.debug("Category rule data retrieved successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error querying data: {e}")
        raise Error(f"Error querying data: {e}")
    finally:
        DatabaseConnection.close_cursor()

    category_rule_data = []
    for rule in raw_category_rule_data:
        if rule is not None and rule[5] is not None:
            category_rule_data.append(
                CategoryRule(
                    id=rule[0],
                    category_id=rule[1],
                    name=rule[2],
                    priority=rule[3],
                    enabled=rule[4] == 1,
                    rule=rule[5],
                    query=parse_string(rule[5]),
                )
            )

    if not category_rule_data:
        logger.warning("No category rule data found.")

    return category_rule_data


def delete_category_rule(
    rule: int | CategoryRule, db_path: Path = config.Database.PATH
) -> None:
    """
    Deletes a category rule from the database.

    Args:
        rule: The ID of the category rule or the CategoryRule object.
        db_path: Path to the database.

    Raises:
        Error: If a database error occurs.
    """
    rule_id = rule.id if isinstance(rule, CategoryRule) else rule

    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)

        cursor.execute(
            """
            DELETE FROM tbl_CategoryRule
            WHERE i8_CategoryRuleID = ?;
            """,
            (rule_id,),
        )

        conn.commit()

        if cursor.rowcount == 0:
            logger.warning(f"No category rule found with ID {rule_id}.")
        else:
            logger.debug(
                f"Category rule with ID {rule_id} deleted successfully."
            )

    except sqlite3.Error as e:
        logger.error(f"Error deleting category rule: {e}")
        raise Error(f"Error deleting category rule: {e}") from e

    finally:
        DatabaseConnection.close_cursor()
