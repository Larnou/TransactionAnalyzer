from datetime import datetime, timedelta
from typing import Any, Callable, Optional

import pandas as pd

from src.parser import read_file_from_json, read_file_from_xlsx
from src.utils import create_logger


def write_log_to_file(filename: str, data_log: list) -> None:
    """
    Записывает данные data_log в файл по пути filename.
    Args:
        filename: Путь до файла, в котором будут записаны логи.
        data_log: Данные логирования работы.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for line in data_log:
            f.write(line + "\n")


def log(filename: str | None = None) -> Callable:
    """
    Декоратор, позволяющий проанализировать и отследить поведение функции.
    Args:
        filename: Путь до файла, в котором будут записаны логи.
    """

    def func_decorator(func) -> Any:
        def wrapper(*args, **kwargs) -> Any:
            log_data = []

            # Описание времени вызова
            date = datetime.now()
            date_formatted = datetime.strftime(date, "%d.%m.%Y %H:%M:%S")
            date_log = f"Time to access the function: {date_formatted}"
            log_data.append(date_log)

            name_log = f"Function name: {func.__name__}()"
            log_data.append(name_log)
            args_log = f"Arguments used: {args[1:]} and {kwargs}"
            log_data.append(args_log)

            try:
                result = func(*args, **kwargs)
                result_log = f"The result of the function execution {func.__name__}(): {result}\n"
                log_data.append(result_log)

                if filename:
                    write_log_to_file(filename, log_data)
                else:
                    standart_filename = f"../reports/{func.__name__}.log"
                    write_log_to_file(standart_filename, log_data)

                return result
            except Exception as e:
                error_log = f"\n{e}\n{args_log}"
                log_data.append(error_log)

                if filename:
                    write_log_to_file(filename, log_data)
                else:
                    standart_filename = f"../reports/{func.__name__}.log"
                    write_log_to_file(standart_filename, log_data)
                return None

        return wrapper

    return func_decorator


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца от переданной даты.
    Args:
        transactions: Полный набор данных по транзакциям.
        category: Категория, по которой проводится отчёт.
        date: Дата по которую проводится отчёт в формате "01.01.2025 00:00:00".

    Returns: Датафрейм с информацией по тратам по категориям.
    """
    spending_by_category_logger.info(f"Траты по заданной категории {category} за последние три месяца.")
    if date is None:
        period_end_date = datetime.now()
    else:
        period_end_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")

    spending_by_category_logger.info(f"Конец периода для анализа трат {period_end_date}.")
    period_start_date = period_end_date - timedelta(days=92)
    period = {"start": period_start_date, "end": period_end_date}
    spending_by_category_logger.info(f"Начало периода для анализа трат {period_start_date}.")

    operations = transactions.loc[
        (period["start"] <= transactions["Дата операции"])
        & (transactions["Дата операции"] <= period["end"])
        & (transactions["Категория"] == category)
    ]
    spending_by_category_logger.info(f"Список транзакций за указанный период состоит из {len(operations)} записей.")

    operations.reset_index(drop=True, inplace=True)
    spending_by_category_logger.info("Вывод списка транзакций operations.")

    return operations


# Для тестового вызова раскоментировать последние три строчки
transactions = read_file_from_xlsx("operations.xlsx")
user_settings = read_file_from_json("user_settings.json")
spending_by_category_logger = create_logger("spending_by_category_logger", "spending_by_category")
spending_by_category(transactions, "Супермаркеты", "01.01.2022 00:00:00")
