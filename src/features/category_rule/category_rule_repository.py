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
) -> None:
    # TODO: add docs
    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")

    try:
        enabled = 1 if rule.enabled else 0
        cursor.execute(
            """
            INSERT INTO tbl_CategoryRule (
                    i8_CategoryID,
                    str_Name,
                    i8_Priority,
                    i8_Enabled,
                    str_Rule,
            ) VALUES (?, ?, ?, ?, ?);
            """,
            (rule.category_id, rule.name, rule.priority, enabled, rule.rule),
        )
        conn.commit()
        logger.debug("Category Rule added successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error inserting data: {e}")
        raise Error(f"Error inserting data: {e}")
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
