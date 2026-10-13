ALLOWED_TYPES = {"int", "str", "bool"}


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns = {"ID": "int"}

    for column in columns:
        if ":" not in column:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        column_name, column_type = column.split(":", 1)

        if not column_name or column_type not in ALLOWED_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        parsed_columns[column_name] = column_type

    metadata[table_name] = {"columns": parsed_columns}

    columns_str = ", ".join(
        f"{name}:{col_type}" for name, col_type in parsed_columns.items()
    )
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')

    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


def list_tables(metadata: dict) -> None:
    if not metadata:
        print("Список таблиц пуст.")
        return

    for table_name in metadata:
        print(f"- {table_name}")