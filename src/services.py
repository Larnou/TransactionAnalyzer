import json
from datetime import datetime, timedelta
from typing import Any

from pandas import DataFrame

from src.parser import print_json, read_file_from_json, read_file_from_xlsx
from src.utils import create_logger, get_categories

# Выгодные категории повышенного кешбэка
# Сервис позволяет проанализировать, какие категории были наиболее выгодными для выбора в качестве
# категорий повышенного кешбэка. Напишите функцию для анализа выгодности категорий повышенного кешбэка.
# На вход функции поступают данные для анализа, год и месяц.


def get_transaction_history(transaction_data: DataFrame, year: str | int, month: str) -> list[dict[str, Any]]:
    """
    Получение списка транзакций по заданному ограничению по времени. Период строится следующим образом:
    Выбирается месяц и год для анализа. После чего получается список всех транзакций за этот период.
    Args:
        transaction_data: Полный набор данных по транзакциям.
        year: Годл для анализа.
        month: Месяц для анализа.

    Returns: Список транзакций.
    """

    service_cashback_logger.info(f"Получение списка транзакций за указанное время: месяц {month} и год {year}.")
    date_template = "01.01.2021 00:00:00"
    period_template = datetime.strptime(date_template, "%d.%m.%Y %H:%M:%S")
    period_start_date = period_template.replace(year=int(year), month=int(month), day=1, hour=0, minute=0, second=0)
    period_end_date = (period_start_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    period_end_date = period_end_date.replace(hour=23, minute=59, second=59)

    period = {"start": period_start_date, "end": period_end_date}
    service_cashback_logger.info(f"Заданный период времени: {period['start']} - {period['start']}.")

    operations = transaction_data.to_dict("records")
    # Фильтруем операции, где описание соответствует шаблону period
    transaction_history = [
        operation for operation in operations if period["start"] <= operation["Дата операции"] <= period["end"]
    ]

    service_cashback_logger.info(
        f"Список транзакций transaction_history состоит из: {len(transaction_history)} записей."
    )
    service_cashback_logger.info("Вывод списка транзакций transaction_history.")
    return transaction_history


def service_cashback(transaction_data, year_for_analyze, month_for_analyze):
    # Получение списка транзакций за указанный период
    transaction_history = get_transaction_history(transaction_data, year_for_analyze, month_for_analyze)

    # Список категорий за указанный период
    categories = get_categories(transaction_history)
    service_cashback_logger.info(f"Список категорий за указанный период состоит из {len(categories)} наименований.")

    cashback = dict.fromkeys(categories, 0)
    not_in_categories_list = ["Наличные", "Переводы", "Пополнения", "Бонусы"]
    for operation in transaction_history:
        if operation["Категория"] not in not_in_categories_list:
            category_name = operation["Категория"]
            cashback[category_name] += operation["Бонусы (включая кэшбэк)"]

    sorted_cashback = {k: v for k, v in sorted(cashback.items(), key=lambda item: item[1], reverse=True)}

    service_cashback_logger.info("Выполнена сортировка списка категорий за указанный период.")
    return json.dumps(sorted_cashback, ensure_ascii=False, indent=4)


# Раскоментировать для тестового запуска следующие 4 строчки
service_cashback_logger = create_logger("service_cashback_logger", "service_cashback")
transactions = read_file_from_xlsx("operations.xlsx")
user_settings = read_file_from_json("user_settings.json")
cashback = service_cashback(transactions, 2021, 7)
print_json(cashback)
