import shlex
import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    table_info,
    update,
)
from primitive_db.parser import parse_condition, parse_set_clause, parse_values
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

METADATA_FILE = "db_meta.json"


def print_help() -> None:
    print("Функции:")
    print(
        '<command> insert into <имя_таблицы> values (<значение1>, '
        '<значение2>, ...) - создать запись.'
    )
    print(
        '<command> select from <имя_таблицы> where <столбец> = <значение> '
        '- прочитать записи по условию.'
    )
    print('<command> select from <имя_таблицы> - прочитать все записи.')
    print(
        '<command> update <имя_таблицы> set <столбец1> = <новое_значение1> '
        'where <столбец_условия> = <значение_условия> - обновить запись.'
    )
    print(
        '<command> delete from <имя_таблицы> where <столбец> = <значение> '
        '- удалить запись.'
    )
    print('<command> info <имя_таблицы> - вывести информацию о таблице.')
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_welcome() -> None:
    print("\n***Операции с данными***\n")
    print_help()


def print_table(rows: list) -> None:
    if not rows:
        print("Записи не найдены.")
        return

    table = PrettyTable()
    table.field_names = list(rows[0].keys())

    for row in rows:
        table.add_row(list(row.values()))

    print(table)


def _extract_table_name(text: str, keyword_before: str) -> tuple[str, str]:
    parts = text.strip().split(maxsplit=1)
    table_name = parts[0] if parts else ""
    remainder = parts[1] if len(parts) > 1 else ""
    return table_name, remainder


def handle_insert(metadata: dict, args: list[str]) -> None:
    """Обрабатывает команду insert into <table> values ..."""
    rest = " ".join(args)

    if not rest.startswith("into "):
        print(f"Некорректное значение: {rest}.")
        return

    rest = rest[len("into "):]
    table_name, remainder = _extract_table_name(rest, "into")

    if not remainder.startswith("values"):
        print(f"Некорректное значение: {rest}.")
        return

    values_part = remainder[len("values"):].strip()

    if not (values_part.startswith("(") and values_part.endswith(")")):
        print(f"Некорректное значение: {values_part}.")
        return

    values_str = values_part[1:-1]

    try:
        values = parse_values(values_str)
    except ValueError:
        print(f"Некорректное значение: {values_str}.")
        return

    table_data = load_table_data(table_name)
    table_data = insert(metadata, table_name, table_data, values)
    save_table_data(table_name, table_data)


def handle_select(args: list[str]) -> None:
    """Обрабатывает команды:
    select from <table>
    select from <table> where ... = ...
    """
    rest = " ".join(args)

    if not rest.startswith("from "):
        print(f"Некорректное значение: {rest}.")
        return

    rest = rest[len("from "):]
    table_name, remainder = _extract_table_name(rest, "from")

    where_clause = None
    if remainder:
        if not remainder.startswith("where "):
            print(f"Некорректное значение: {remainder}.")
            return
        condition_str = remainder[len("where "):]
        try:
            column, value = parse_condition(condition_str)
        except ValueError:
            print(f"Некорректное значение: {condition_str}.")
            return
        where_clause = {column: value}

    table_data = load_table_data(table_name)
    result = select(table_data, where_clause)
    print_table(result)


def handle_update(args: list[str]) -> None:
    """Обрабатывает команду update"""
    rest = " ".join(args)
    table_name, remainder = _extract_table_name(rest, "")

    if not remainder.startswith("set "):
        print(f"Некорректное значение: {remainder}.")
        return

    remainder = remainder[len("set "):]

    if " where " not in remainder:
        print(f"Некорректное значение: {remainder}.")
        return

    set_part, where_part = remainder.split(" where ", 1)

    try:
        set_clause = parse_set_clause(set_part)
        column, value = parse_condition(where_part)
    except ValueError:
        print(f"Некорректное значение: {remainder}.")
        return

    where_clause = {column: value}

    table_data = load_table_data(table_name)
    table_data = update(table_data, table_name, set_clause, where_clause)
    save_table_data(table_name, table_data)


def handle_delete(args: list[str]) -> None:
    """Обрабатывает команду delete"""
    rest = " ".join(args)

    if not rest.startswith("from "):
        print(f"Некорректное значение: {rest}.")
        return

    rest = rest[len("from "):]
    table_name, remainder = _extract_table_name(rest, "from")

    if not remainder.startswith("where "):
        print(f"Некорректное значение: {remainder}.")
        return

    condition_str = remainder[len("where "):]

    try:
        column, value = parse_condition(condition_str)
    except ValueError:
        print(f"Некорректное значение: {condition_str}.")
        return

    where_clause = {column: value}

    table_data = load_table_data(table_name)
    table_data = delete(table_data, table_name, where_clause)
    save_table_data(table_name, table_data)


def run() -> None:
    """Запускает основной цикл работы с данными таблиц"""
    print_welcome()

    while True:
        metadata = load_metadata(METADATA_FILE)

        user_input = prompt.string(">>>Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError as error:
            print(f"Ошибка разбора команды: {error}")
            continue

        if not args:
            continue

        command, *params = args

        if command == "exit":
            break

        elif command == "help":
            print_help()

        elif command == "create_table":
            if not params:
                print(f"Некорректное значение: {user_input}.")
                continue
            table_name, *columns = params
            metadata = create_table(metadata, table_name, columns)
            save_metadata(METADATA_FILE, metadata)

        elif command == "drop_table":
            if len(params) != 1:
                print(f"Некорректное значение: {user_input}.")
                continue
            metadata = drop_table(metadata, params[0])
            save_metadata(METADATA_FILE, metadata)

        elif command == "list_tables":
            list_tables(metadata)

        elif command == "insert":
            handle_insert(metadata, params)

        elif command == "select":
            handle_select(params)

        elif command == "update":
            handle_update(params)

        elif command == "delete":
            handle_delete(params)

        elif command == "info":
            if len(params) != 1:
                print(f"Некорректное значение: {user_input}.")
                continue
            table_name = params[0]
            table_data = load_table_data(table_name)
            table_info(metadata, table_name, table_data)

        else:
            print(f"Функции {command} нет.")