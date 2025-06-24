import json
import math
import re
from collections import defaultdict
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer

from src.parser import read_file_from_xlsx, print_json


def get_welcome_words():
    """
    Возвращает приветственные слова в зависимости от времени пользователя.
    Returns: Приветственные слова: "Доброе утро" и т.д.
    """
    welcome_words = {0: "Доброй ночи", 1: "Доброе утро", 2: "Добрый день", 3: "Добрый вечер"}
    # Получение текущего времени
    current_time = datetime.now()
    # Извлечение часов
    current_hour = current_time.hour
    return welcome_words[int(current_hour / 6)]


def get_transaction_history(transaction_data: list[dict], period_end: str) -> list[dict[str, Any]]:
    """
    Получение списка транзакций по заданному ограничению по времени. Период строится следующим образом:
    Если дата — 20.05.2020, то данные для анализа будут в диапазоне 01.05.2020-20.05.2020.
    Args:
        transaction_data: Полный набор данных по транзакциям.
        period_end: Время до которого с начала месяца берётся информация о транзакциях.

    Returns: Список транзакций.
    """

    period_end_date = datetime.strptime(period_end, "%d.%m.%Y")
    period_start_date = period_end_date.replace(day=1)
    period = {'start': period_start_date, 'end': period_end_date}

    # Фильтруем операции, где описание соответствует шаблону period
    transaction_history = [
        operation for operation in transaction_data
        if period["start"] <= operation["Дата операции"] <= period["end"]
    ]

    return transaction_history


def get_card_numbers(transaction_data: list[dict]):
    """
    Получение списка номеров карт, с которых выполнялись платежи.
    Args:
        transaction_data: Полный набор данных по транзакциям.

    Returns: Список номеров карт.
    """
    card_numbers = [operation.get("Номер карты") for operation in transaction_data]

    # Необходимо исключить NaN значения, однако Nan != Nan
    return set([number for number in card_numbers if number == number])


def get_transactions_by_card_number(transaction_data: list[dict], card_number: str) -> list[dict[str, Any]]:
    """
    Получение списка транзакций с определённой в card_number номера карточки.
    Args:
        transaction_data: Полный набор данных по транзакциям
        card_number: Номер карточки, по которой производится поиск транзакций

    Returns: Список транзакций по номеру карты.
    """
    card_transactions = [operation for operation in transaction_data if operation["Номер карты"] == card_number]
    return card_transactions


def get_card_transactions_info(card_transactions: list[dict[str, Any]], card_number: str):
    """
    Получение информациии по списку транзакций card_transactions, совершённых с номера карты card_number.
    Информация включает в себя: сведения о номере карты, сколько было потрачено средств (прибыль - траты),
    количество кешбека, которое можно получить за эти операции.
    Args:
        card_transactions: Полный набор данных по транзакциям
        card_number: Номер карточки, по которой производится поиск транзакций

    Returns: Словарь, содержащий в себе информациюю о тратах и кешбеке по транзакциям, совершённым с номера карты
    card_number.
    """
    total_spent = sum(
        [
            -operation["Сумма операции"] for operation in card_transactions
            if not (isinstance(operation["Сумма операции"], float) and math.isnan(operation["Сумма операции"]))
               and operation["Сумма операции"] < 0
        ]
    )

    # Вопрос, какую версию кешбека нужно использовать? Скорее второй вариант, просто 1р за 100 потраченных
    # total_cashback = sum(
    #     [
    #         operation["Кэшбэк"] for operation in card_transactions
    #         if not (isinstance(operation["Кэшбэк"], float) and math.isnan(operation["Кэшбэк"]))
    #     ]
    # )

    total_cashback = round(total_spent / 100, 2)

    card_total_info = {
        "last_digits": card_number,
        "total_spent": round(total_spent, 2),
        "cashback": round(total_cashback, 2),
    }

    return card_total_info


def get_cards_transactions_info(card_numbers: list[str], transaction_history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Получение информациии по списку транзакций card_transactions, совершённых с номеров карт card_numbers.
    Args:
        card_numbers: Список номеров карт, участвующих в транзакциях за период.
        transaction_history: Полный набор данных по транзакциям.

    Returns: Список, содержащий в себе информациюю о тратах и кешбеке по транзакциям, совершённым по каждой карте из
    card_numbers.
    """
    cards_info = []
    for card_number in card_numbers:
        card_transactions = get_transactions_by_card_number(transaction_history, card_number)
        card_info = get_card_transactions_info(card_transactions, card_number)
        cards_info.append(card_info)

    return cards_info

