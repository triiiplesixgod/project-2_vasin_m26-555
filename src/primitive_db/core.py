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

def _is_valid_type(value, expected_type: str) -> bool:
    """проверяет, соответствует ли Python-значение ожидаемому типу столбца"""
    if expected_type == "bool":
        return isinstance(value, bool)
    if expected_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "str":
        return isinstance(value, str)
    return False


def insert(
    metadata: dict, table_name: str, table_data: list, values: list
) -> list:
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = metadata[table_name]["columns"]
    data_columns = {
        name: col_type for name, col_type in columns.items() if name != "ID"
    }

    if len(values) != len(data_columns):
        print(
            f"Некорректное значение: ожидается {len(data_columns)} "
            f"значений, получено {len(values)}."
        )
        return table_data

    for (column_name, column_type), value in zip(data_columns.items(), values):
        if not _is_valid_type(value, column_type):
            print(f"Некорректное значение: {value}.")
            return table_data

    new_id = max((row["ID"] for row in table_data), default=0) + 1

    record = {"ID": new_id}
    for (column_name, _), value in zip(data_columns.items(), values):
        record[column_name] = value

    table_data.append(record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

    return table_data


def select(table_data: list, where_clause: dict | None = None) -> list:
    """Возвращает записи таблицы. Возможно добавление условия where"""
    if not where_clause:
        return table_data

    return [
        row
        for row in table_data
        if all(row.get(key) == value for key, value in where_clause.items())
    ]


def update(
    table_data: list, table_name: str, set_clause: dict, where_clause: dict
) -> list:
    matched = select(table_data, where_clause)

    if not matched:
        print(
            f'Ошибка: Записи, соответствующие условию, '
            f'не найдены в таблице "{table_name}".'
        )
        return table_data

    for row in matched:
        row.update(set_clause)
        print(f'Запись с ID={row["ID"]} в таблице "{table_name}" успешно обновлена.')

    return table_data


def delete(table_data: list, table_name: str, where_clause: dict) -> list:
    matched = select(table_data, where_clause)

    if not matched:
        print(
            f'Ошибка: Записи, соответствующие условию, '
            f'не найдены в таблице "{table_name}".'
        )
        return table_data

    matched_ids = {row["ID"] for row in matched}
    remaining = [row for row in table_data if row["ID"] not in matched_ids]

    for row_id in matched_ids:
        print(f'Запись с ID={row_id} успешно удалена из таблицы "{table_name}".')

    return remaining


def table_info(metadata: dict, table_name: str, table_data: list) -> None:
    """в примере задания есть функция info, хотя в задании ее нет, добавил здесь ее"""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    columns = metadata[table_name]["columns"]
    columns_str = ", ".join(
        f"{name}:{col_type}" for name, col_type in columns.items()
    )

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_str}")
    print(f"Количество записей: {len(table_data)}")