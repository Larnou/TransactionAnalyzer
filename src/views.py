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
from typing import Any

from src.parser import print_json, read_file_from_xlsx
from src.utils import get_welcome_words, get_transaction_history, get_card_numbers, get_cards_transactions_info


def main_view(transaction_data: list[dict]) -> dict[str, Any]:
    # Вступительные слова приветствия
    welcome_words = get_welcome_words()

    # Получение списка транзакицй по условию даты
    history_period = get_transaction_history(transaction_data, '30.12.2021')
    card_numbers = get_card_numbers(history_period)

    cards_info = get_cards_transactions_info(card_numbers, history_period)

    return {
        "greeting": welcome_words,
        "cards": cards_info,
    }


transactions = read_file_from_xlsx("operations.xlsx")
view = main_view(transaction_data=transactions)

print_json(view)