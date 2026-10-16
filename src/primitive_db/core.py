from primitive_db.constants import (
    DELETE_RECORD_ACTION,
    DROP_TABLE_ACTION,
    ID_COLUMN_NAME,
    ID_COLUMN_TYPE,
    VALID_TYPES,
)
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

_select_cache = create_cacher()


def _is_valid_type(value, expected_type: str) -> bool:
    """Проверяет, соответствует ли Python-значение ожидаемому типу столбца."""
    if expected_type == "bool":
        return isinstance(value, bool)
    if expected_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "str":
        return isinstance(value, str)
    return False


def _filter_rows(table_data: list, where_clause: dict | None) -> list:
    """Возвращает записи, соответствующие условию where"""
    if not where_clause:
        return table_data
    return [
        row
        for row in table_data
        if all(row.get(key) == value for key, value in where_clause.items())
    ]


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    if table_name in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" уже существует.')

    parsed_columns = {ID_COLUMN_NAME: ID_COLUMN_TYPE}

    for column in columns:
        if ":" not in column:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")

        column_name, column_type = column.split(":", 1)

        if not column_name or column_type not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")

        parsed_columns[column_name] = column_type

    metadata[table_name] = {"columns": parsed_columns}

    columns_str = ", ".join(
        f"{name}:{col_type}" for name, col_type in parsed_columns.items()
    )
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')

    return metadata


@confirm_action(DROP_TABLE_ACTION)
@handle_db_errors
def drop_table(metadata: dict, table_name: str) -> dict:
    if table_name not in metadata:
        raise KeyError(f'Ошибка: Таблица "{table_name}" не существует.')

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


def list_tables(metadata: dict) -> None:
    if not metadata:
        print("Список таблиц пуст.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


@log_time
@handle_db_errors
def insert(metadata: dict, table_name: str, table_data: list, values: list) -> list:
    if table_name not in metadata:
        raise KeyError(f'Ошибка: Таблица "{table_name}" не существует.')

    columns = metadata[table_name]["columns"]
    data_columns = {
        name: col_type for name, col_type in columns.items() if name != ID_COLUMN_NAME
    }

    if len(values) != len(data_columns):
        raise ValueError(
            f"Некорректное значение: ожидается {len(data_columns)} "
            f"значений, получено {len(values)}. Попробуйте снова."
        )

    for (column_name, column_type), value in zip(data_columns.items(), values):
        if not _is_valid_type(value, column_type):
            raise ValueError(f"Некорректное значение: {value}. Попробуйте снова.")

    new_id = max((row[ID_COLUMN_NAME] for row in table_data), default=0) + 1

    record = {ID_COLUMN_NAME: new_id}
    for (column_name, _), value in zip(data_columns.items(), values):
        record[column_name] = value

    table_data.append(record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

    return table_data


@log_time
@handle_db_errors
def select(table_data: list, where_clause: dict | None = None) -> list:
    """Возвращает записи таблицы, соответствующие условию where"""
    cache_key = (
        repr(table_data),
        tuple(sorted(where_clause.items())) if where_clause else None,
    )

    return _select_cache(cache_key, lambda: _filter_rows(table_data, where_clause))


@handle_db_errors
def update(
    table_data: list, table_name: str, set_clause: dict, where_clause: dict
) -> list:
    matched = _filter_rows(table_data, where_clause)

    if not matched:
        raise ValueError(
            f'Ошибка: Записи, соответствующие условию, '
            f'не найдены в таблице "{table_name}".'
        )

    for row in matched:
        row.update(set_clause)
        print(
            f'Запись с ID={row[ID_COLUMN_NAME]} в таблице "{table_name}" '
            f"успешно обновлена."
        )

    return table_data


@confirm_action(DELETE_RECORD_ACTION)
@handle_db_errors
def delete(table_data: list, table_name: str, where_clause: dict) -> list:
    matched = _filter_rows(table_data, where_clause)

    if not matched:
        raise ValueError(
            f'Ошибка: Записи, соответствующие условию, '
            f'не найдены в таблице "{table_name}".'
        )

    matched_ids = {row[ID_COLUMN_NAME] for row in matched}

    for row_id in matched_ids:
        print(f'Запись с ID={row_id} успешно удалена из таблицы "{table_name}".')

    table_data[:] = [
        row for row in table_data if row[ID_COLUMN_NAME] not in matched_ids
    ]

    return table_data


@handle_db_errors
def table_info(metadata: dict, table_name: str, table_data: list) -> None:
    """в примере задания есть функция info, хотя в задании ее нет, добавил здесь ее"""
    if table_name not in metadata:
        raise KeyError(f'Ошибка: Таблица "{table_name}" не существует.')

    columns = metadata[table_name]["columns"]
    columns_str = ", ".join(
        f"{name}:{col_type}" for name, col_type in columns.items()
    )

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_str}")
    print(f"Количество записей: {len(table_data)}")