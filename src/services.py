import json
from datetime import datetime, timedelta
from typing import Any

from pandas import DataFrame

from src.parser import read_file_from_xlsx, read_file_from_json, print_json
from src.utils import get_categories

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

    date_template = '01.01.2021 00:00:00'
    period_template = datetime.strptime(date_template, "%d.%m.%Y %H:%M:%S")
    period_start_date = period_template.replace(year=int(year), month=int(month), day=1, hour=0, minute=0, second=0)
    period_end_date = (period_start_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    period_end_date = period_end_date.replace(hour=23, minute=59, second=59)

    period = {'start': period_start_date, 'end': period_end_date}

    operations = transaction_data.to_dict("records")
    # Фильтруем операции, где описание соответствует шаблону period
    transaction_history = [
        operation for operation in operations
        if period["start"] <= operation["Дата операции"] <= period["end"]
    ]

    return transaction_history

def service_cashback(transaction_data, year_for_analyze, month_for_analyze):
    # Получение списка транзакций за указанный период
    transaction_history = get_transaction_history(transaction_data, year_for_analyze , month_for_analyze)

    # Список категорий за указанный период
    categories = get_categories(transaction_history)

    cashback = dict.fromkeys(categories, 0)
    not_in_categories_list = ["Наличные", "Переводы", "Пополнения", "Бонусы"]
    for operation in transaction_history:
        if operation["Категория"] not in not_in_categories_list:
            category_name = operation["Категория"]
            cashback[category_name] += operation["Бонусы (включая кэшбэк)"]

    sorted_cashback = {k: v for k, v in sorted(cashback.items(), key=lambda item: item[1], reverse=True)}
    return json.dumps(sorted_cashback, ensure_ascii=False, indent=4)

# Раскоментировать для тестового запуска следующие 4 строчки
# transactions = read_file_from_xlsx("operations.xlsx")
# user_settings = read_file_from_json("user_settings.json")
# cashback = service_cashback(transactions, 2021, 12)
# print_json(cashback)
