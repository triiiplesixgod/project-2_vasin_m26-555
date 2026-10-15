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


def print_table(rows: list | None) -> None:
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


def handle_insert(metadata: dict, rest: str) -> None:
    """Обрабатывает команду insert into <table> values ..."""
    if not rest.startswith("into "):
        print(f"Некорректное значение: {rest}. Попробуйте снова.")
        return

    rest = rest[len("into "):]
    table_name, remainder = _extract_table_name(rest, "into")

    if not remainder.startswith("values"):
        print(f"Некорректное значение: {rest}. Попробуйте снова.")
        return

    values_part = remainder[len("values"):].strip()

    if not (values_part.startswith("(") and values_part.endswith(")")):
        print(f"Некорректное значение: {values_part}. Попробуйте снова.")
        return

    values_str = values_part[1:-1]

    try:
        values = parse_values(values_str)
    except ValueError:
        print(f"Некорректное значение: {values_str}. Попробуйте снова.")
        return

    table_data = load_table_data(table_name)
    result = insert(metadata, table_name, table_data, values)

    if result is not None:
        save_table_data(table_name, table_data)


def handle_select(rest: str) -> None:
    """Обрабатывает команды:
    select from 
    select from ... where ... = ...
    """
    if not rest.startswith("from "):
        print(f"Некорректное значение: {rest}. Попробуйте снова.")
        return

    rest = rest[len("from "):]
    table_name, remainder = _extract_table_name(rest, "from")

    where_clause = None
    if remainder:
        if not remainder.startswith("where "):
            print(f"Некорректное значение: {remainder}. Попробуйте снова.")
            return
        condition_str = remainder[len("where "):]
        try:
            column, value = parse_condition(condition_str)
        except ValueError:
            print(f"Некорректное значение: {condition_str}. Попробуйте снова.")
            return
        where_clause = {column: value}

    table_data = load_table_data(table_name)
    result = select(table_data, where_clause)
    print_table(result)


def handle_update(rest: str) -> None:
    """Обрабатывает команду update"""
    table_name, remainder = _extract_table_name(rest, "")

    if not remainder.startswith("set "):
        print(f"Некорректное значение: {remainder}. Попробуйте снова.")
        return

    remainder = remainder[len("set "):]

    if " where " not in remainder:
        print(f"Некорректное значение: {remainder}. Попробуйте снова.")
        return

    set_part, where_part = remainder.split(" where ", 1)

    try:
        set_clause = parse_set_clause(set_part)
        column, value = parse_condition(where_part)
    except ValueError:
        print(f"Некорректное значение: {remainder}. Попробуйте снова.")
        return

    where_clause = {column: value}

    table_data = load_table_data(table_name)
    result = update(table_data, table_name, set_clause, where_clause)

    if result is not None:
        save_table_data(table_name, table_data)


def handle_delete(rest: str) -> None:
    """Обрабатывает команду delete"""
    if not rest.startswith("from "):
        print(f"Некорректное значение: {rest}. Попробуйте снова.")
        return

    rest = rest[len("from "):]
    table_name, remainder = _extract_table_name(rest, "from")

    if not remainder.startswith("where "):
        print(f"Некорректное значение: {remainder}. Попробуйте снова.")
        return

    condition_str = remainder[len("where "):]

    try:
        column, value = parse_condition(condition_str)
    except ValueError:
        print(f"Некорректное значение: {condition_str}. Попробуйте снова.")
        return

    where_clause = {column: value}

    table_data = load_table_data(table_name)
    result = delete(table_data, table_name, where_clause)

    if result is not None:
        save_table_data(table_name, table_data)


def run() -> None:
    """Запускает основной цикл работы с данными таблиц."""
    print_welcome()

    while True:
        metadata = load_metadata(METADATA_FILE)

        user_input = prompt.string(">>>Введите команду: ").strip()

        parts = user_input.split(maxsplit=1)
        command = parts[0] if parts else ""
        rest = parts[1] if len(parts) > 1 else ""

        if command == "exit":
            break

        elif command == "help":
            print_help()

        elif command == "create_table":
            try:
                args = shlex.split(rest)
            except ValueError as error:
                print(f"Ошибка разбора команды: {error}")
                continue
            if not args:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue
            table_name, *columns = args
            result = create_table(metadata, table_name, columns)
            if result is not None:
                save_metadata(METADATA_FILE, metadata)

        elif command == "drop_table":
            try:
                args = shlex.split(rest)
            except ValueError as error:
                print(f"Ошибка разбора команды: {error}")
                continue
            if len(args) != 1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue
            result = drop_table(metadata, args[0])
            if result is not None:
                save_metadata(METADATA_FILE, metadata)

        elif command == "list_tables":
            list_tables(metadata)

        elif command == "insert":
            handle_insert(metadata, rest)

        elif command == "select":
            handle_select(rest)

        elif command == "update":
            handle_update(rest)

        elif command == "delete":
            handle_delete(rest)

        elif command == "info":
            try:
                args = shlex.split(rest)
            except ValueError as error:
                print(f"Ошибка разбора команды: {error}")
                continue
            if len(args) != 1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue
            table_name = args[0]
            table_data = load_table_data(table_name)
            table_info(metadata, table_name, table_data)

        elif command == "":
            continue

        else:
            print(f"Функции {command} нет. Попробуйте снова.")