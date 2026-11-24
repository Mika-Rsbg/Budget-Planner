from models.category_rule.query import (
    DatePartOperator,
    DateRangeOperator,
    LogicalOperator,
    Query,
    QueryCondition,
    QueryDatePartCondition,
    QueryDateRangeCondition,
    QueryGroup,
    QueryOperator,
    QueryValue,
)


def parse_object(
    query: Query,
) -> str:
    """Convert a query object into its textual query representation.

    String values in ``QueryCondition`` objects have spaces replaced with
    asterisks so they can be parsed as a single token. Query groups are
    rendered recursively and preserve their logical operators.

    Args:
        query (Condition | QueryGroup): Condition or group to convert
            into a query string.

    Returns:
        str: A textual representation of ``query``.
    """
    match query:
        case QueryCondition():
            if type(query.value) is str:
                query.value = query.value.replace(" ", "*")
            condition = (
                query.field
                + " "
                + str(query.operator)
                + ' "'
                + str(query.value)
                + '"'
            )
            if query.tolerance != 0.0:
                condition += " +- " + str(query.tolerance)
            return condition
        case QueryDatePartCondition():
            date_part_condition = (
                query.field
                + " "
                + str(query.operator)
                + " "
                + str(query.value)
            )
            return date_part_condition
        case QueryDateRangeCondition():
            date_range_condition = (
                query.field
                + " "
                + str(query.operator)
                + " "
                + str(query.start)
                + " "
                + str(query.end)
            )
            return date_range_condition
        case QueryGroup():
            group = "( "
            for i, child in enumerate(query.children):
                group += parse_object(child)
                if (i + 1) != query.children.__len__():
                    group += " " + query.operator + " "
            group += " )"
            return group

    return "LOL"


def parse_string(
    query: str,
) -> Query:
    """Parse a textual query into its corresponding query object.

    Args:
        query (str): Query string containing a simple condition or a nested
            group.

    Returns:
        Condition | QueryGroup: The parsed condition or query group.

    Raises:
        ValueError: If the query is empty, malformed, or uses incompatible
            logical operators in one group.
    """
    return parse_nested_string(query)


def value_parser(value: str) -> QueryValue:
    """Convert a textual query value to its corresponding Python value.

    Surrounding whitespace and double quotes are removed before conversion.
    Values are recognized in the order ``None``, booleans, integers, and
    floating-point numbers; any other value remains a string.

    Args:
        value: Textual value from a query condition.

    Returns:
        The converted query value.
    """
    value = value.strip()
    value = value.strip('"')

    if value == "None":
        return None

    if value == "True":
        return True

    if value == "False":
        return False

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    return value


def parse_simple_string(
    query: str,
) -> Query:
    """Parse a query containing one condition without nested groups.

    Args:
        query (str): Query string with a field, operator, and operator-specific
            value tokens.

    Returns:
        Condition | QueryGroup: The parsed value condition, date-part
            condition, or date-range condition.

    Raises:
        IndexError: If required query tokens are missing.
        ValueError: If a value, date part, or date-range operator is invalid.
    """
    tokens = query.split()

    field = tokens[0]
    operator = tokens[1]

    if operator in QueryOperator:
        operator = QueryOperator(operator)
        value = value_parser(tokens[2])
        tolerance = 0.0
        if tokens.__len__() == 5:
            tolerance = float(tokens[4])
        return QueryCondition(field, operator, value, tolerance)

    elif operator in DatePartOperator:
        operator = DatePartOperator(operator)
        value = int(tokens[2])
        return QueryDatePartCondition(field, operator, value)

    else:  # operator in DateRangeOperator:
        operator = DateRangeOperator(operator)
        start = tokens[2]
        end = tokens[3]
        return QueryDateRangeCondition(field, operator, start, end)


def parse_nested_string(
    query: str,
) -> Query:
    """Parse a query string containing nested logical groups.

    A group starts with ``(`` and ends with ``)``. All direct children of a
    group must use the same logical operator. Nested groups are parsed
    recursively; groups without an explicit operator default to ``AND``.

    Args:
        query (str): Query string containing a simple condition or a nested
            group.

    Raises:
        ValueError: If the query is empty, has unbalanced parentheses, mixes
            logical operators within a group, or contains no group children.
        IndexError: If a child condition is missing required query tokens.

    Returns:
        Condition | QueryGroup: The parsed condition or recursively
            constructed query group.
    """
    tokens = query.split()

    if not tokens:
        raise ValueError("Query must not be empty.")

    if tokens[0] != "(":
        return parse_simple_string(query)

    expressions: list[str] = []
    group_operator: LogicalOperator | None = None

    bracket_level = 0
    memory = ""

    for token in tokens:
        if token == "(":
            bracket_level += 1
            if bracket_level != 1:
                memory += "( "
            continue

        elif token == ")":
            bracket_level -= 1

            if bracket_level == 0:
                expressions.append(memory.strip())
                memory = ""
                break

            memory += ") "
            continue

        elif token in LogicalOperator and bracket_level == 1:
            operator = LogicalOperator(token)

            if group_operator is None:
                group_operator = operator
            elif group_operator != operator:
                raise ValueError(
                    "A QueryGroup must use the same logical operator "
                    "for all its children."
                )

            expressions.append(memory.strip())
            memory = ""
            continue

        memory += token + " "

    if bracket_level != 0:
        raise ValueError("Unbalanced parentheses in query.")

    if not expressions:
        raise ValueError("QueryGroup must contain at least one child.")

    children = []

    for expression in expressions:
        expression = expression.strip()

        if expression.startswith("("):
            children.append(parse_nested_string(expression))
        else:
            children.append(parse_simple_string(expression))

    if group_operator is None:
        group_operator = LogicalOperator.AND

    return QueryGroup(
        operator=group_operator,
        children=children,
    )
