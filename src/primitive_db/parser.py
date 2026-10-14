def split_outside_quotes(text: str, separator: str = ",") -> list[str]:
    """разбивает строку по разделителю, игнорируя разделители внутри кавычек"""
    parts = []
    current = []
    in_quotes = False

    for char in text:
        if char == '"':
            in_quotes = not in_quotes
            current.append(char)
        elif char == separator and not in_quotes:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    parts.append("".join(current).strip())
    return [part for part in parts if part]


def parse_literal(token: str):
    token = token.strip()

    if token.startswith('"') and token.endswith('"') and len(token) >= 2:
        return token[1:-1]

    if token.lower() == "true":
        return True
    if token.lower() == "false":
        return False

    return int(token)


def parse_values(values_str: str) -> list:
    tokens = split_outside_quotes(values_str, ",")
    return [parse_literal(token) for token in tokens]


def parse_condition(condition_str: str) -> tuple[str, object]:
    if "=" not in condition_str:
        raise ValueError(f"некорректное условие: {condition_str}")

    column, value = condition_str.split("=", 1)
    return column.strip(), parse_literal(value.strip())


def parse_set_clause(set_clause_str: str) -> dict:
    assignments = split_outside_quotes(set_clause_str, ",")
    result = {}

    for assignment in assignments:
        column, value = parse_condition(assignment)
        result[column] = value

    return result