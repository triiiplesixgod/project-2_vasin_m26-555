import time

import prompt


def _copy_metadata(wrapper, func):
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def handle_db_errors(func):
    """Декоратор, централизующий обработку исключений операций с БД."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
            )
        except KeyError as error:
            message = error.args[0] if error.args else str(error)
            print(message)
        except ValueError as error:
            print(str(error))
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return _copy_metadata(wrapper, func)


def confirm_action(action_name: str):
    """Фабрика декораторов: запрашивает подтверждение перед опасным действием."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return _copy_metadata(wrapper, func)

    return decorator


def log_time(func):
    """Декоратор, замеряющий время выполнения функции."""

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    return _copy_metadata(wrapper, func)


def create_cacher():
    """Создаёт замыкание для простого кэширования результатов по ключу."""
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result