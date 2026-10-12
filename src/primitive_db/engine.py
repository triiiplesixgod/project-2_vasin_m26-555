import prompt

COMMANDS_HELP = (
    "<command> exit - выйти из программы\n"
    "<command> help - справочная информация"
)


def print_help():
    print(COMMANDS_HELP)


def welcome():
    print("Первая попытка запустить проект!\n")
    print("***")
    print_help()

    while True:
        command = prompt.string("Введите команду: ")

        if command == "exit":
            break
        elif command == "help":
            print()
            print_help()
        else:
            print("Неизвестная команда")