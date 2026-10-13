import shlex
import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help() -> None:
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> "
        "<столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_welcome() -> None:
    print("\n***База данных***")
    print_help()


def run() -> None:
    """Запускает основной цикл работы с базой данных."""
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
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue
            table_name, *columns = params
            metadata = create_table(metadata, table_name, columns)
            save_metadata(METADATA_FILE, metadata)

        elif command == "drop_table":
            if len(params) != 1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue
            metadata = drop_table(metadata, params[0])
            save_metadata(METADATA_FILE, metadata)

        elif command == "list_tables":
            list_tables(metadata)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")