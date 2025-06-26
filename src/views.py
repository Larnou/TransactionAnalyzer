# Задачи по категориям: Веб-страницы:
# Главная
# События

"""
Реализуйте набор функций и главную функцию, принимающую на вход строку с датой и временем в формате
YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ со следующими данными:

Приветствие в формате
"???" где ??? — «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи» в зависимости от текущего времени.
По каждой карте: последние 4 цифры карты; общая сумма расходов; кешбэк (1 рубль на каждые 100 рублей).
Топ-5 транзакций по сумме платежа.
Курс валют.
Стоимость акций из S&P500.
"""
import json
from typing import Any

from pandas import DataFrame

from src.parser import print_json, read_file_from_xlsx, read_file_from_json
from src.utils import get_welcome_words, get_transaction_history, get_card_numbers, get_cards_transactions_info, \
    get_top_transactions, get_currency_rates, get_stock_prices, get_transaction_history_ranged, \
    get_total_expenses_amount, \
    get_categories, get_expenses_by_top_categories, get_transfers_and_cash, get_total_income_amount, \
    get_income_categories


def main_view(transaction_data: DataFrame, user_data: dict[str, Any], period_end: str, ) -> str:
    """
    Возвращает информацию по общим тратам, по каждой карте: последние 4 цифры карты; общая сумма расходов;
    кешбэк (1 рубль на каждые 100 рублей), топ-5 транзакций по сумме платежа, курс валют, стоимость акций из S&P500.
    Args:
        period_end: Конец периода, по который формируется словарь
        transaction_data: Полный набор данных по транзакциям.
        user_data: Настройки пользователя для указания валют и акций.

    Returns: Словарь с информацией.
    """
    # Вступительные слова приветствия
    welcome_words = get_welcome_words()

    # Получение списка транзакицй по условию даты
    history_period = get_transaction_history(transaction_data, period_end)
    card_numbers = get_card_numbers(history_period)
    cards_info = get_cards_transactions_info(card_numbers, history_period)

    # Топ5 транзакций по сумме платежа
    top_sorted_transactions_info = get_top_transactions(history_period)

    # Получение курсов валют
    currencies_info = get_currency_rates(user_data.get('user_currencies'))

    # Получение курса акций
    stocks_info = get_stock_prices(user_data.get('user_stocks'))

    view_dict = {
        "greeting": welcome_words,
        "cards": cards_info,
        "top_transactions": top_sorted_transactions_info,
        "currency_rates": currencies_info,
        "stock_prices": stocks_info,
    }

    json_string = json.dumps(view_dict, ensure_ascii=False, indent=4)

    return json_string


transactions = read_file_from_xlsx("operations.xlsx")
user_settings = read_file_from_json("user_settings.json")
date_period = '11.10.2021 11:25:59'

view = main_view(period_end=date_period, transaction_data=transactions, user_data=user_settings)
print_json(view)

# Реализуйте набор функций и главную функцию, принимающую на вход строку с датой и второй необязательный
# параметр — диапазон данных. По умолчанию диапазон равен одному месяцу (с начала месяца, на который
# выпадает дата, по саму дату). Возможные значения второго необязательного параметра:
# W — неделя, на которую приходится дата;
# M — месяц, на который приходится дата;
# Y — год, на который приходится дата;
# ALL — все данные до указанной даты.

def main_event(transaction_data: DataFrame, user_data: dict[str, Any], period_end: str, range_type: str = "M") -> str:
    """
    Возвращает информацию по общим тратам, по категориям, информацию о поступлениях по категориям, курс валют,
    стоимость акций из S&P500.
    Args:
        transaction_data: Полный набор данных по транзакциям.
        user_data: Настройки пользователя для указания валют и акций.
        period_end: Конец периода, по который формируется словарь.
        range_type: Тип диапазона для даты.

    Returns: Словарь с информацией.
    """
    # Получение списка транзакицй по условию даты
    history_period = get_transaction_history_ranged(transaction_data, period_end, range_type)

    # Получение общей суммы расходов
    total_expenses_amount = get_total_expenses_amount(history_period)

    # Расходы по категориям:
    categories = get_categories(history_period)
    categories_expenses = get_expenses_by_top_categories(history_period, categories)

    # Наличные и переводы
    transfers_and_cash = get_transfers_and_cash(history_period)

    # Общие пополнения
    total_income_amount = get_total_income_amount(history_period)

    # Категории пополнения
    income_categories = get_income_categories(history_period, ["Пополнения", "Бонусы"])

    # Получение курсов валют
    currencies_info = get_currency_rates(user_data.get('user_currencies'))

    # Получение курса акций
    stocks_info = get_stock_prices(user_data.get('user_stocks'))


    event_dict = {
        "expenses": {
            "total_amount": total_expenses_amount,
            "main": categories_expenses,
            "transfers_and_cash": transfers_and_cash,
        },
        "income": {
            "total_amount": total_income_amount,
            "main": income_categories,
        },
        "currency_rates": currencies_info,
        "stock_prices": stocks_info,
    }

    json_string = json.dumps(event_dict, ensure_ascii=False, indent=4)

    return json_string


# event = main_event(transaction_data=transactions, user_data=user_settings, period_end=date_period, range_type='M')
# print_json(event)

